from typing import Final
from pathlib import Path

import cocotb
from cocotb.triggers import ClockCycles

from .. import config
from ..clock_domain import ClockDomainDriver

from .stepper_motor_driver import StepperMotorDriver
from .stepper_motor_monitor import StepperMotorMonitor

##################################################


def test_stepper_motor():
    config.run_test(
        toplevel="stepper_motor",
        output_directory=Path(config.OUTPUT_DIRECTORY, "stepper_motor"),
        test_module="test.print_mechanism.test_stepper_motor",
    )


##################################################


@cocotb.test()  # type: ignore
async def run_test(dut):
    clock_domain: Final = ClockDomainDriver(dut.clk, dut.reset)

    motor_driver: Final = StepperMotorDriver(
        name="MotorDriver",
        clock=dut.clk,
        phase_a=dut.motor_phase_a,
        phase_b=dut.motor_phase_b,
        phase_na=dut.motor_phase_na,
        phase_nb=dut.motor_phase_nb,
    )

    monitor: Final = StepperMotorMonitor(
        name="MotorMonitor",
        line_advance_tick=dut.line_advance_tick,
        line_reverse_tick=dut.line_reverse_tick,
    )

    clock_domain.start(100_000_000)
    await clock_domain.reset(2)
    await motor_driver.step_forward(1)

    monitor.start()

    # Test forward
    await motor_driver.step_forward(20)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == 5
    monitor.reset()

    # Test backward
    await motor_driver.step_backward(20)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == -5
    monitor.reset()

    # Test mixed
    await motor_driver.step_forward(3)
    await motor_driver.step_backward(1)
    await motor_driver.step_forward(2)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == 1
    monitor.reset()

    await motor_driver.step_forward(6)
    await motor_driver.step_backward(5)
    await motor_driver.step_forward(7)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == 2
    monitor.reset()

    # Test forward double steps
    await motor_driver.step_forward(3)
    await motor_driver.step_forward(2, double_step=True)
    await motor_driver.step_forward(1)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == 2
    monitor.reset()

    # Test mixed double steps
    await motor_driver.step_forward(1)
    await motor_driver.step_backward(1, double_step=True)
    await motor_driver.step_forward(2, double_step=True)
    await motor_driver.step_forward(1)
    await ClockCycles(dut.clk, 8)
    assert monitor.lines_moved == 1
    monitor.reset()
