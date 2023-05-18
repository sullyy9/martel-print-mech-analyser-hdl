import logging
from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.decorators import Task
from cocotb.handle import SimHandleBase


class ThermalHeadMonitor:
    def __init__(
        self,
        head_active: SimHandleBase,
        head_active_dots: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._head_active: Final[SimHandleBase] = head_active
        self._head_active_dots: Final[SimHandleBase] = head_active_dots

        self._coroutine: Optional[Task] = None

        self.burns: Queue = Queue()

        self._log: Final[Optional[Logger]] = logging.getLogger(name) if name else None

    def start(self) -> None:
        if self._log is not None:
            self._log.warning("Start")

        if self._coroutine is None:
            self._coroutine = cocotb.start_soon(self._monitor())

    def stop(self) -> None:
        if self._log is not None:
            self._log.warning("Stop")

        if self._coroutine is not None:
            self._coroutine.kill()

    async def _monitor(self) -> None:
        while True:
            await RisingEdge(self._head_active)
            await ReadOnly()

            burn_line: Final[str] = self._head_active_dots.value.binstr

            if self._log is not None:
                self._log.warning(f"Burn line: {burn_line}")

            self.burns.put_nowait(burn_line)
