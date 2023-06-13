import logging
from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.triggers import RisingEdge, ReadOnly, First
from cocotb.decorators import Task
from cocotb.handle import SimHandleBase


class StepperMotorMonitor:
    def __init__(
        self,
        line_advance_tick: SimHandleBase,
        line_reverse_tick: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._adv_tick: Final[SimHandleBase] = line_advance_tick
        self._rev_tick: Final[SimHandleBase] = line_reverse_tick

        self._coro: Optional[Task] = None

        self._lines_moved: int = 0

        self._log: Final[Optional[Logger]] = logging.getLogger(name) if name else None

    def start(self) -> None:
        if self._log is not None:
            self._log.warning("Start")

        if self._coro is None:
            self._coro = cocotb.start_soon(self._monitor())

    def stop(self) -> None:
        if self._log is not None:
            self._log.warning("Stop")

        if self._coro is not None:
            self._coro.kill()

    @property
    def lines_moved(self) -> int:
        return self._lines_moved

    def reset(self) -> None:
        self._lines_moved = 0

    async def _monitor(self) -> None:
        while True:
            await First(RisingEdge(self._adv_tick), RisingEdge(self._rev_tick))
            await ReadOnly()
            if self._adv_tick.value == 1:
                self._lines_moved += 1

            if self._rev_tick.value == 1:
                self._lines_moved -= 1
