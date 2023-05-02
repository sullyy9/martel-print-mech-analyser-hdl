import os
import csv
import re
from typing import AsyncGenerator, Final, Optional
from pathlib import Path

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly, FallingEdge
from cocotb.binary import BinaryValue

import cv2 as cv

import numpy as np
from numpy import dtype, uint8, float32
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

            await ClockCycles(self._clk, 4)
            self._mech_clk.value = bits[0]
            self._mech_data.value = bits[1]
            self._mech_latch.value = bits[2]
            self._mech_dst.value = bits[3]
            self._mech_motor_phase_a.value = bits[4]
            self._mech_motor_phase_b.value = bits[5]


class Monitor:
    def __init__(self, dut) -> None:
        self._clk: Final = dut.clk
        self._uart_tx: Final = dut.uart_tx_pin_1

        self._clks_per_bit: Final = dut.uart_tx.CLKS_PER_BIT.value

        self._bytes: bytes = bytes()

    async def start(self) -> None:
        while True:
            await FallingEdge(self._uart_tx)

            data_bits: list[int] = []

            # Check the start bit.
            for cycle in range(self._clks_per_bit - 1):
                await RisingEdge(self._clk)
                await ReadOnly()

                assert self._uart_tx.value == 0, (
                    f"Expected continuation of start bit in cycle: "
                    f"{cycle}/{self._clks_per_bit}"
                )

            # Check each data bit.
            for i in range(8):
                await RisingEdge(self._clk)
                await ReadOnly()

                data_bits.append(self._uart_tx.value)
                for cycle in range(self._clks_per_bit - 1):
                    await RisingEdge(self._clk)
                    await ReadOnly()

                    assert self._uart_tx.value == data_bits[-1], (
                        f"Expected continuation of data bit {i} in cycle: "
                        f"{cycle}/{self._clks_per_bit}"
                    )

            # Check the stop bit.
            for cycle in range(self._clks_per_bit):
                await RisingEdge(self._clk)
                await ReadOnly()

                assert self._uart_tx.value == 1, (
                    f"Expected continuation of stop bit in cycle: "
                    f"{cycle}/{self._clks_per_bit}"
                )

            await RisingEdge(self._clk)
            await ReadOnly()

            byte: int = 0
            for i, bit in enumerate(data_bits):
                byte += bit << i

            self._bytes += byte.to_bytes(1, 'little')

    async def get_bytes(self) -> bytes:
        return self._bytes


@cocotb.test()  # type: ignore
async def run_test(dut):
    driver: Final[Driver] = Driver(dut)
    monitor: Final[Monitor] = Monitor(dut)

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
                max_rows=50000,
            )
        )

    await ClockCycles(dut.clk, 100000)
    data: bytes = await monitor.get_bytes()

    # assert False, f"{data}"

    with open("uart_data", mode="wb") as file:
        file.write(data)

    lines: list[bytes] = re.findall(b"LINE:.{48}:", data, re.S)

    img_rows: list[NDArray[uint8]] = []
    for line in lines:
        line = bytearray(line[5:-1])
        line.reverse()

        img_line: NDArray[uint8] = np.array([int(byte) for byte in line], dtype=uint8)
        img_rows.append(np.unpackbits(img_line))

    image = np.multiply(np.vstack(img_rows), 255, dtype=uint8)
    cv.imwrite("test.png", image)
