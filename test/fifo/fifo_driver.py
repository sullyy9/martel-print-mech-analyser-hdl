from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge


class FifoFull(Exception):
    pass


class FifoEmpty(Exception):
    pass


class FifoReadDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        enable: SimHandleBase,
        empty: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._enable: Final[SimHandleBase] = enable
        self._empty: Final[SimHandleBase] = empty

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

        self._enable.value = 0

    async def read(self) -> None:
        if self._log is not None:
            self._log.info("Read word")

        await RisingEdge(self._clock)

        if self._empty.value == 1:
            raise FifoEmpty

        self._enable.value = 1

        await RisingEdge(self._clock)
        self._enable.value = 0


class FifoWriteDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        enable: SimHandleBase,
        data: SimHandleBase,
        full: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._enable: Final[SimHandleBase] = enable
        self._data: Final[SimHandleBase] = data
        self._full: Final[SimHandleBase] = full

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

        self._enable.value = 0
        self._data.value = 0

    async def write(self, word: int) -> None:
        if self._log is not None:
            self._log.info(f"Write word: {word}")

        await RisingEdge(self._clock)

        if self._full.value == 1:
            raise FifoFull

        self._enable.value = 1
        self._data.value = word

        await RisingEdge(self._clock)
        self._enable.value = 0
        self._data.value = 0
