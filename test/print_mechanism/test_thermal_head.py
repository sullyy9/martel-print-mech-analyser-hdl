from typing import Final
from pathlib import Path

import cocotb
from cocotb.binary import BinaryValue

from .. import config

from .thermal_head_driver import ThermalHeadDriver
from .thermal_head_monitor import ThermalHeadMonitor

##################################################


def test_thermal_head():
    config.run_test(
        toplevel="thermal_head",
        output_directory=Path(config.OUTPUT_DIRECTORY, "thermal_head"),
        test_module="test.print_mechanism.test_thermal_head",
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
    head_driver: Final = ThermalHeadDriver(
        name="HeadDriver",
        clock=dut.clk,
        data=dut.data,
        latch=dut.latch,
        dst=dut.dst,
    )

    head_monitor: Final = ThermalHeadMonitor(
        name="HeadMonitor",
        head_active=dut.head_active,
        head_active_dots=dut.head_active_dots,
    )

    dut.reset.value = 1
    head_monitor.start()

    for line in TEST_DATA:
        await head_driver.write_bit_stream(BinaryValue(line))
        await head_driver.latch_data()
        await head_driver.burn(0.000001)

    for line in TEST_DATA:
        assert head_monitor.burns.get_nowait() == line
