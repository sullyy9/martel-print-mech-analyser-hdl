import logging
from logging import Logger
from typing import Final, Optional

from cocotb.triggers import FallingEdge, ReadWrite
from cocotb.handle import SimHandleBase

SEQUENCE: Final = [
    0b1001,
    0b0001,
    0b0011,
    0b0010,
    0b0110,
    0b0100,
    0b1100,
    0b1000,
]


class StepperMotorDriver:
    def __init__(
        self,
        clock: SimHandleBase,
        phase_a: SimHandleBase,
        phase_b: SimHandleBase,
        phase_na: SimHandleBase,
        phase_nb: SimHandleBase,
        name: Optional[str] = None,
    ) -> None:
        self._clock: Final[SimHandleBase] = clock
        self._phase_a: Final[SimHandleBase] = phase_a
        self._phase_b: Final[SimHandleBase] = phase_b
        self._phase_na: Final[SimHandleBase] = phase_na
        self._phase_nb: Final[SimHandleBase] = phase_nb

        self._step: int = 0

        self._log: Final[Optional[Logger]] = logging.getLogger(name) if name else None

        self._clock.value = 1
        self._phase_a.value = 0
        self._phase_b.value = 0
        self._phase_na.value = 0
        self._phase_nb.value = 0

    async def step_forward(self, steps: int, double_step: bool = False) -> None:
        for _ in range(steps):
            await FallingEdge(self._clock)
            await ReadWrite()

            self._step += 2 if double_step else 1
            self._step %= len(SEQUENCE)

            step_value: Final = SEQUENCE[self._step]

            self._phase_a.value = (step_value >> 0) & 0b1
            self._phase_b.value = (step_value >> 1) & 0b1
            self._phase_na.value = (step_value >> 2) & 0b1
            self._phase_nb.value = (step_value >> 3) & 0b1

    async def step_backward(self, steps: int, double_step: bool = False) -> None:
        for _ in range(steps):
            await FallingEdge(self._clock)
            await ReadWrite()

            self._step -= 2 if double_step else 1
            if self._step < 0:
                self._step = len(SEQUENCE) + self._step

            step_value: Final = SEQUENCE[self._step]

            self._phase_a.value = (step_value >> 0) & 0b1
            self._phase_b.value = (step_value >> 1) & 0b1
            self._phase_na.value = (step_value >> 2) & 0b1
            self._phase_nb.value = (step_value >> 3) & 0b1
