from logging import Logger
from typing import Final, Optional
from decimal import Decimal

import cocotb
from cocotb.triggers import Timer, FallingEdge, RisingEdge
from cocotb.task import Task
from cocotb.handle import SimHandleBase
from cocotb.clock import Clock
from cocotb.binary import BinaryValue


class ThermalHeadDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        data: SimHandleBase,
        latch: SimHandleBase,
        dst: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._data: Final[SimHandleBase] = data
        self._latch: Final[SimHandleBase] = latch
        self._dst: Final[SimHandleBase] = dst

        self._mech_clock: Final = Clock(
            self._clock, int((1 / 24_000_000) * 1_000_000_000), "ns"
        )

        self._log: Final[Optional[Logger]] = cocotb.log.getChild(name) if name else None

        self._clock.value = 1
        self._data.value = 0
        self._latch.value = 1
        self._dst.value = 0
    
    def write(self, clock: int, data: int, latch: int, dst: int) -> None:
        self._clock.value = clock
        self._data.value = data
        self._latch.value = latch
        self._dst.value = dst

    async def write_bit_stream(self, data: BinaryValue) -> None:
        if self._log is not None:
            self._log.info(f"Write data: {data}")

        clock_task: Final[Task] = cocotb.start_soon(self._mech_clock.start())

        for bit in data.binstr:
            await FallingEdge(self._clock)
            self._data.value = 0 if bit == "0" else 1

        await RisingEdge(self._clock)
        clock_task.kill()

    async def latch_data(self) -> None:
        if self._log is not None:
            self._log.info("Latch data")

        self._latch.value = 0
        await Timer(Decimal(25), "ns")
        self._latch.value = 1

    async def burn(self, time: float) -> None:
        if self._log is not None:
            self._log.info(f"Burn for {time}s")

        self._dst.value = 1
        await Timer(Decimal(time * 1_000_000_000), "ns")
        self._dst.value = 0
