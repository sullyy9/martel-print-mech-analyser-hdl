import logging
from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.decorators import Task
from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge, ReadOnly


class ExclusiveSignalMonitor:
    def __init__(
        self,
        clock: SimHandleBase,
        signal1: SimHandleBase,
        signal2: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._signal1: Final[SimHandleBase] = signal1
        self._signal2: Final[SimHandleBase] = signal2

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

            signal1_active: Final[bool] = self._signal1.value == 1
            signal2_active: Final[bool] = self._signal2.value == 1

            assert not (
                signal1_active and signal2_active
            ), "Exclusive signals both active"
