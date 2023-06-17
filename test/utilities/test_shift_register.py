from typing import Final
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ReadWrite, ReadOnly, ClockCycles

import cocotb_test.simulator

from .. import config
from ..clock_driver import ClockDriver
from ..reset_driver import ResetDriver


def test_counter_gray():
    output_directory: Path = Path(config.BUILD_DIRECTORY, "shift_register")

    cocotb_test.simulator.run(
        verilog_sources=config.VERLIOG_SOURCES,
        toplevel="shift_register",
        module="test.utilities.test_shift_register",
        sim_build=output_directory,
        extra_args=config.SIM_ARGS,
    )


##################################################


@cocotb.test()  # type: ignore
async def run_test(dut):
    clock_driver = ClockDriver(dut.clk)
    reset_driver = ResetDriver(dut.clk, dut.reset)

    dut.data_in.value = 0
    dut.enable.value = 0
    clock_driver.start(frequency=100_000_000)
    await reset_driver.reset(2)

    for _ in range(4):
        await FallingEdge(dut.clk)
        await ReadWrite()
        dut.data_in.value = 1
        dut.enable.value = 1

    await FallingEdge(dut.clk)
    await ReadWrite()
    dut.data_in.value = 0
    dut.enable.value = 0

    await RisingEdge(dut.clk)
    await ReadOnly()
    expect_value: int = 0b00001111
    actual_value: int = dut.data_out.value
    assert actual_value == expect_value, (
        "Unexpected shift register output.\n"
        f"Expected: {expect_value}\n"
        f"Actual:   {actual_value}"
    )

    for _ in range(4):
        await FallingEdge(dut.clk)
        await ReadWrite()
        dut.data_in.value = 0
        dut.enable.value = 1

    for _ in range(2):
        await FallingEdge(dut.clk)
        await ReadWrite()
        dut.data_in.value = 1
        dut.enable.value = 1

    await FallingEdge(dut.clk)
    await ReadWrite()
    dut.data_in.value = 0
    dut.enable.value = 0

    await RisingEdge(dut.clk)
    await ReadOnly()
    expect_value = 0b11000011
    actual_value = dut.data_out.value
    assert actual_value == expect_value, (
        "Unexpected shift register output.\n"
        f"Expected: {expect_value}\n"
        f"Actual:   {actual_value}"
    )

    await ClockCycles(dut.clk, 8)
