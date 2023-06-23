from logging import Logger
from typing import Final, Optional

import cocotb
from cocotb.task import Task
from cocotb.handle import SimHandleBase
from cocotb.triggers import RisingEdge, ClockCycles


class ResetDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        reset: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._reset: Final[SimHandleBase] = reset

        self._coroutine: Optional[Task] = None

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

    async def reset(self, clock_cycles: int) -> None:
        if self._log is not None:
            self._log.warning(f"Reset for {clock_cycles} cycles")

        await RisingEdge(self._clock)
        self._reset.value = 0
        await ClockCycles(self._clock, clock_cycles)
        self._reset.value = 1
