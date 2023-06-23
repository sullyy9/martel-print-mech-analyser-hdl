from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.task import Task
from cocotb.handle import SimHandleBase
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles


class ClockDomainDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        reset: SimHandleBase,
        enable: Optional[SimHandleBase] = None,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._reset: Final[SimHandleBase] = reset
        self._enable: Final[SimHandleBase | None] = enable

        self._coroutine: Optional[Task] = None

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

    def start(self, frequency: float = 1_000_000) -> None:
        if self._coroutine is not None:
            return

        period_ns: Final = int((1 / frequency) * 1_000_000_000)
        clock: Final = Clock(self._clock, period_ns, units="ns")

        self._coroutine = cocotb.start_soon(clock.start())

        if self._log is not None:
            self._log.info(f"Starting clock with frequency: {frequency}Hz")

    def stop(self) -> None:
        if self._log is not None:
            self._log.info("Stopping clock")

        if self._coroutine is not None:
            self._coroutine.kill()
            self._coroutine = None

    async def reset(self, clock_cycles: int) -> None:
        if self._log is not None:
            self._log.info(f"Holding clock domain in reset for {clock_cycles} cycles")

        await RisingEdge(self._clock)
        self._reset.value = 0
        await ClockCycles(self._clock, clock_cycles)
        self._reset.value = 1

        if self._log is not None:
            self._log.info("Released clock domain from reset")
