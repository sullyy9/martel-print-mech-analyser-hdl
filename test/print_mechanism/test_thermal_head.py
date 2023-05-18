from typing import Final
from pathlib import Path

import cocotb
from cocotb.binary import BinaryValue

import cocotb_test.simulator

from .. import config
from ..clock_driver import ClockDriver
from ..reset_driver import ResetDriver

from .thermal_head_driver import ThermalHeadDriver
from .thermal_head_monitor import ThermalHeadMonitor

##################################################


def test_thermal_head():
    output_directory: Path = Path(config.BUILD_DIRECTORY, "thermal_head")

    cocotb_test.simulator.run(
        verilog_sources=config.VERLIOG_SOURCES,
        toplevel="thermal_head",
        module="test.print_mechanism.test_thermal_head",
        sim_build=output_directory,
        extra_args=config.SIM_ARGS,
        parameters={"HEAD_WIDTH": 16},
    )


##################################################

TEST_DATA: Final[list[str]] = [
    "0000000000000000",
    "0000011111000000",
    "0000010001101100",
    "0000011001011000",
    "0000000110110000",
    "0000011111100000",
    "0000100110000000",
    "0001100110000000",
    "0011000110000000",
    "0000000110000000",
    "0000000110000000",
    "0000011001100000",
    "0000110000110000",
    "0001100000011000",
    "0001100000011000",
    "0001100000011000",
]


@cocotb.test()  # type: ignore
async def run_test(dut):
    clock_driver: Final[ClockDriver] = ClockDriver(dut.clk, "Clock")
    reset_driver: Final[ResetDriver] = ResetDriver(dut.clk, dut.reset)

    head_driver: Final = ThermalHeadDriver(
        name="HeadDriver",
        clock=dut.mech_clk,
        data=dut.mech_data,
        latch=dut.mech_latch,
        dst=dut.mech_dst,
    )

    head_monitor: Final = ThermalHeadMonitor(
        name="HeadMonitor",
        head_active=dut.head_active,
        head_active_dots=dut.head_active_dots,
    )

    clock_driver.start(180_000_000)
    await reset_driver.reset(2)

    head_monitor.start()

    for line in TEST_DATA:
        await head_driver.write_bit_stream(BinaryValue(line))
        await head_driver.latch_data()
        await head_driver.burn(0.000001)
