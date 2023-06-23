from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.task import Task
from cocotb.handle import SimHandleBase


class PrintMechMonitor:
    def __init__(
        self,
        print_line_ready: SimHandleBase,
        print_line: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._print_line_ready: Final[SimHandleBase] = print_line_ready
        self._print_line: Final[SimHandleBase] = print_line

        self._coroutine: Optional[Task] = None

        self.lines: Queue = Queue()

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

    def start(self) -> None:
        if self._log is not None:
            self._log.info("Start")

        if self._coroutine is None:
            self._coroutine = cocotb.start_soon(self._monitor())

    def stop(self) -> None:
        if self._log is not None:
            self._log.info("Stop")

        if self._coroutine is not None:
            self._coroutine.kill()

    async def _monitor(self) -> None:
        while True:
            await RisingEdge(self._print_line_ready)
            await ReadOnly()
            self.lines.put_nowait(self._print_line.value.binstr)

            if self._log is not None:
                self._log.info("Got line")
