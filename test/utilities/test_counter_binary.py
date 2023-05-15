from typing import Final
from pathlib import Path

import pytest

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, ClockCycles

import cocotb_test.simulator

from .. import config

##################################################


@pytest.mark.parametrize(
    "parameters",
    [
        {"MAX_VALUE": "255", "INCREMENT": "1"},
        {"MAX_VALUE": "1", "INCREMENT": "1"},
        {"MAX_VALUE": "8", "INCREMENT": "2"},
        {"MAX_VALUE": "256", "INCREMENT": "13"},
    ],
)
def test_counter_binary(parameters: dict):
    output_directory: Path = Path(
        config.OUTPUT_DIRECTORY,
        "counter_binary/max_value={MAX_VALUE}-increment={INCREMENT}".format(
            **parameters
        ),
    )

    cocotb_test.simulator.run(
        verilog_sources=config.VERLIOG_SOURCES,
        toplevel="counter_binary",
        module="test.utilities.test_counter_binary",
        sim_build=output_directory,
        parameters=parameters,
    )


##################################################


class Driver:
    def __init__(self, dut) -> None:
        self._dut = dut

        self._dut.clk.value = 0
        self._dut.reset.value = 1
        self._dut.enable.value = 0

    async def start(self) -> None:
        cocotb.start_soon(Clock(self._dut.clk, 1, "ns").start())

    async def reset(self, clock_cycles: int = 1) -> None:
        await RisingEdge(self._dut.clk)
        self._dut.reset.value = 0
        await ClockCycles(self._dut.clk, clock_cycles)
        self._dut.reset.value = 1

    async def enable(self) -> None:
        await RisingEdge(self._dut.clk)
        self._dut.enable.value = 1


##################################################


async def check_count_value(dut, expected_value: int) -> None:
    actual_value: int = dut.count.value

    assert actual_value == expected_value, (
        f"expected={expected_value}",
        f"actual={actual_value}",
    )


##################################################


@cocotb.test()  # type: ignore
async def run_test(dut):
    max_value: Final[int] = dut.MAX_VALUE.value
    increment: Final[int] = dut.INCREMENT.value

    driver = Driver(dut)

    cocotb.start_soon(driver.start())
    await driver.reset(1)

    await RisingEdge(dut.clk)
    await ReadOnly()
    await check_count_value(dut, 0)

    await driver.enable()

    for i in range(increment, (max_value + 1), increment):
        await RisingEdge(dut.clk)
        await ReadOnly()
        await check_count_value(dut, i)

    await RisingEdge(dut.clk)
    await ReadOnly()
    await check_count_value(dut, 0)
