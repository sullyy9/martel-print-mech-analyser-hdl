import os
import csv
from typing import AsyncGenerator, Final, Optional
from pathlib import Path

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge
from cocotb.binary import BinaryValue

import cv2 as cv

import numpy as np
from numpy import uint8, float32
from numpy.typing import NDArray


class Driver:
    def __init__(self, dut) -> None:
        self._clk: Final = dut.clk
        self._rst: Final = dut.reset
        self._mech_clk: Final = dut.mech_clk
        self._mech_data: Final = dut.mech_data
        self._mech_latch: Final = dut.mech_latch
        self._mech_dst: Final = dut.mech_dst
        self._mech_motor_phase_a: Final = dut.mech_motor_phase_a
        self._mech_motor_phase_b: Final = dut.mech_motor_phase_b

        self._last_timestamp: Optional[float] = None

        self._clk.value = 0
        self._rst.value = 1
        self._mech_clk.value = 1
        self._mech_data.value = 0
        self._mech_latch.value = 1
        self._mech_dst.value = 0
        self._mech_motor_phase_a.value = 0
        self._mech_motor_phase_b.value = 0

    async def start(self) -> None:
        cocotb.start_soon(Clock(self._clk, 10, units="ns").start())

    async def reset_dut(self, reset_cycles: int = 1) -> None:
        await RisingEdge(self._clk)
        self._rst.value = 0
        await ClockCycles(self._clk, reset_cycles)
        self._rst.value = 1

    async def write(self, data: NDArray[uint8]) -> None:
        for _, *row in data:
            bits: list[int] = [int(b) for b in row]

            await ClockCycles(self._clk, 2)
            self._mech_clk.value = bits[0]
            self._mech_data.value = bits[1]
            self._mech_latch.value = bits[2]
            self._mech_dst.value = bits[3]
            self._mech_motor_phase_a.value = bits[4]
            self._mech_motor_phase_b.value = bits[5]


class Monitor:
    def __init__(self, dut) -> None:
        self._line_advance_tick: Final = dut.line_advance_tick
        self._print_line: Final = dut.print_line

        self._lines: list[NDArray[uint8]] = []

    async def start(self) -> None:
        while True:
            await RisingEdge(self._line_advance_tick)
            await ReadOnly()

            self._lines.append(
                np.array([uint8(b) for b in self._print_line.value.binstr])
            )

    async def get_image(self) -> NDArray[uint8]:
        return np.multiply(np.vstack(self._lines), 255, dtype=uint8)


class InternalsMonitor:
    def __init__(self, dut) -> None:
        self._clk: Final = dut.clk
        self._mech_clk: Final = dut.mech_clk
        self._mech_data: Final = dut.mech_data
        self._mech_latch: Final = dut.mech_latch

        self._data_buffer_reg: Final = dut.data_buffer_reg
        self._latch_buffer_reg: Final = dut.latch_buffer_reg

        self._head_width: Final = dut.HEAD_WIDTH.value

        self._data_buffer_model: NDArray[uint8] = np.zeros(
            self._head_width, dtype=uint8
        )

        self._latch_buffer_model: NDArray[uint8] = np.zeros(
            self._head_width, dtype=uint8
        )

        self._burn_buffer_model: NDArray[uint8] = np.zeros(
            self._head_width, dtype=uint8
        )

    async def start(self) -> None:
        cocotb.start_soon(self.data_buffer_model())
        cocotb.start_soon(self.data_buffer_monitor())
        cocotb.start_soon(self.latch_buffer_model())
        cocotb.start_soon(self.latch_buffer_monitor())

    async def data_buffer_model(self) -> None:
        while True:
            await RisingEdge(self._mech_clk)
            await ReadOnly()
            self._data_buffer_model[:-1] = self._data_buffer_model[1:]
            self._data_buffer_model[-1] = self._mech_data

    async def data_buffer_monitor(self) -> None:
        while True:
            await RisingEdge(self._mech_clk)
            await ClockCycles(self._clk, 1)
            await ReadOnly()

            data_buffer = np.array(
                [uint8(b) for b in self._data_buffer_reg.value.binstr]
            )

            assert np.array_equal(data_buffer, self._data_buffer_model), (
                f"Mismatch between data buffer and model {os.linesep}"
                f"Expected:{os.linesep}{self._data_buffer_model}{os.linesep}"
                f"Actual:{os.linesep}{data_buffer}"
            )

    async def latch_buffer_model(self) -> None:
        while True:
            await FallingEdge(self._mech_latch)
            await ReadOnly()
            self._latch_buffer_model = self._data_buffer_model

    async def latch_buffer_monitor(self) -> None:
        while True:
            await FallingEdge(self._mech_latch)
            await ClockCycles(self._clk, 1)
            await ReadOnly()

            latch_buffer = np.array(
                [uint8(b) for b in self._latch_buffer_reg.value.binstr]
            )

            assert np.array_equal(latch_buffer, self._latch_buffer_model), (
                f"Mismatch between latch buffer and model {os.linesep}"
                f"Expected:{os.linesep}{self._latch_buffer_model}{os.linesep}"
                f"Actual:{os.linesep}{latch_buffer}"
            )

    async def burn_buffer_model(self) -> None:
        while True:
            await FallingEdge(self._mech_latch)
            await ReadOnly()

            self._latch_buffer_model


@cocotb.test()  # type: ignore
async def run_test(dut):
    monitor: Final[Monitor] = Monitor(dut)
    driver: Final[Driver] = Driver(dut)

    cocotb.start_soon(driver.start())
    cocotb.start_soon(monitor.start())

    await driver.reset_dut()

    # cocotb.start_soon(InternalsMonitor(dut).start())

    with open(Path(os.path.dirname(__file__), "./Arial16.csv")) as file:
        await driver.write(
            np.genfromtxt(
                file,
                delimiter=",",
                skip_header=1,
                dtype=[float32, uint8, uint8, uint8, uint8, uint8, uint8],
            )
        )

    image: NDArray[uint8] = await monitor.get_image()

    cv.imwrite("test.png", image)
