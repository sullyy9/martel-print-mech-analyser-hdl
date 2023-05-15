import logging
from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.queue import Queue
from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.decorators import Task


class FifoDataMonitor:
    def __init__(
        self,
        clock: SimHandleBase,
        enable: SimHandleBase,
        data: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._enable: Final[SimHandleBase] = enable
        self._data: Final[SimHandleBase] = data

        self.transactions: Queue = Queue()

        self._coroutine: Optional[Task] = None

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
            await RisingEdge(self._clock)
            await ReadOnly()

            if self._enable.value != 1:
                continue

            transaction: Final[int] = self._data.value.integer
            self.transactions.put_nowait(self._data.value)

            if self._log is not None:
                self._log.warning(f"Transaction: {transaction}")
