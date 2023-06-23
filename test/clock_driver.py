from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.task import Task
from cocotb.handle import SimHandleBase
from cocotb.clock import Clock


class ClockDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock

        self._coroutine: Optional[Task] = None

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

    def start(self, frequency: float = 1_000_000) -> None:
        if self._coroutine is None:
            period_ns: Final[int] = int((1 / frequency) * 1_000_000_000)
            clock: Final[Clock] = Clock(self._clock, period_ns, units="ns")

            self._coroutine = cocotb.start_soon(clock.start())

            if self._log is not None:
                self._log.info(f"Start with frequency: {frequency}Hz")

    def stop(self) -> None:
        if self._log is not None:
            self._log.info("Stop")

        if self._coroutine is not None:
            self._coroutine.kill()
            self._coroutine = None
