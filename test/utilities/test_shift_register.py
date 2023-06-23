from pathlib import Path

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ReadWrite, ReadOnly, ClockCycles

from .. import config
from ..clock_domain import ClockDomainDriver


def test_counter_gray() -> None:
    config.run_test(
        toplevel="shift_register",
        output_directory=Path(config.OUTPUT_DIRECTORY, "shift_register"),
        test_module="test.utilities.test_shift_register",
    )


##################################################


@cocotb.test()  # type: ignore
async def run_test(dut):
    clock_domain = ClockDomainDriver(dut.clk, dut.reset)

    dut.data_in.value = 0
    dut.enable.value = 0
    clock_domain.start(frequency=100_000_000)
    await clock_domain.reset(2)

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
