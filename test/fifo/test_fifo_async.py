from typing import Final
from pathlib import Path

import cocotb

from .fifo_driver import FifoReadDriver, FifoWriteDriver, FifoEmpty, FifoFull
from .fifo_monitor import FifoDataMonitor
from .fifo_model import FifoModel

from .. import config
from ..clock_domain import ClockDomainDriver
from ..signal_monitor import ExclusiveSignalMonitor

##################################################


def test_fifo_async():
    config.run_test(
        toplevel="fifo_async",
        output_directory=Path(config.OUTPUT_DIRECTORY, "fifo_async"),
        test_module="test.fifo.test_fifo_async",
    )


##################################################


@cocotb.test()  # type: ignore
async def run_test(dut):
    read_clock_domain: Final = ClockDomainDriver(
        dut.read_clk, dut.reset, name="ReadClockDomain"
    )
    write_clock_domain: Final = ClockDomainDriver(
        dut.write_clk, dut.reset, name="WriteClockDomain"
    )

    read_driver: Final[FifoReadDriver] = FifoReadDriver(
        name="ReadDriver", clock=dut.read_clk, enable=dut.read_enable, empty=dut.empty
    )

    write_driver: Final[FifoWriteDriver] = FifoWriteDriver(
        name="WriteDriver",
        clock=dut.write_clk,
        enable=dut.write_enable,
        data=dut.write_data,
        full=dut.full,
    )

    read_monitor: Final[FifoDataMonitor] = FifoDataMonitor(
        clock=dut.read_clk,
        enable=dut.read_enable,
        data=dut.read_data,
        name="ReadMonitor",
    )
    write_monitor: Final[FifoDataMonitor] = FifoDataMonitor(
        clock=dut.write_clk,
        enable=dut.write_enable,
        data=dut.write_data,
        name="WriteMonitor",
    )

    empty_read_monitor: Final[ExclusiveSignalMonitor] = ExclusiveSignalMonitor(
        clock=dut.write_clk,
        signal1=dut.empty,
        signal2=dut.read_enable,
        name="EmptyReadMonitor",
    )

    full_write_monitor: Final[ExclusiveSignalMonitor] = ExclusiveSignalMonitor(
        clock=dut.write_clk,
        signal1=dut.empty,
        signal2=dut.read_enable,
        name="FullWriteMonitor",
    )

    model: Final[FifoModel] = FifoModel(dut.DEPTH.value)

    read_clock_domain.start(frequency=1_000_000)
    write_clock_domain.start(frequency=2_000_000)
    await read_clock_domain.reset(2)
    await write_clock_domain.reset(2)

    read_monitor.start()
    write_monitor.start()

    empty_read_monitor.start()
    full_write_monitor.start()

    ##################################################
    operations: Final[list[tuple]] = [
        ("Write", bytes([i for i in range(4)])),
        ("Read", 2),
        ("Write", bytes([i for i in range(8)])),
        ("Read", 10),
    ]

    for op, values in operations:
        if op == "Write":
            for byte in values:
                try:
                    await write_driver.write(byte)
                    model.write(byte)
                except FifoFull:
                    assert (
                        model.is_full()
                    ), f"DUT is full but model has {model.count()} bytes"

        elif op == "Read":
            for _ in range(values):
                try:
                    await read_driver.read()
                    expected: Final[int] = model.read()
                    actual: Final[int] = read_monitor.transactions.get_nowait()

                    assert actual == expected, (
                        "Byte Read from DUT doesn't match byte read from model\n"
                        f"DUT: {actual}\n"
                        f"Model: {expected}"
                    )
                except FifoEmpty:
                    assert (
                        model.is_empty()
                    ), f"DUT is empty but model has {model.count()} bytes"

        else:
            assert False, f"Unexpected operation: {op}"

    ##################################################

    read_monitor.stop()
    write_monitor.stop()

    read_clock_domain.stop()
    write_clock_domain.stop()
