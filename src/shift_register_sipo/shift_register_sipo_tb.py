import random
from typing import Final

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly


class ShiftRegisterSIPOTB:
    def __init__(self, dut):
        self.clk: Final = dut.clk
        self.rst: Final = dut.reset
        self.write_data: Final = dut.write_data
        self.write_enable: Final = dut.write_enable
        self.read_data: Final = dut.read_data

        self.depth: Final[int] = dut.DEPTH.value

        self.clk.value = 0
        self.rst.value = 1
        self.write_data.value = 0
        self.write_enable.value = 0

    async def reset(self) -> None:
        await RisingEdge(self.clk)
        self.rst.value = 0
        await ClockCycles(self.clk, 1)
        self.rst.value = 1
        await ClockCycles(self.clk, 1)

    async def write(self, bit_stream: list[int]) -> None:
        for bit in bit_stream:
            await RisingEdge(self.clk)
            self.write_enable.value = 1
            self.write_data.value = bit

        await RisingEdge(self.clk)
        self.write_enable.value = 0

    async def read(self) -> list[int]:
        await RisingEdge(self.clk)
        await ReadOnly()
        data: int = self.read_data.value
        return [1 if digit == "1" else 0 for digit in bin(data)[2:]]


@cocotb.test()  # type: ignore
async def run_test(dut):
    bench: Final[ShiftRegisterSIPOTB] = ShiftRegisterSIPOTB(dut)
    cocotb.start_soon(Clock(bench.clk, 1, units="ns").start())
    await bench.reset()

    model: list[int] = [0] * bench.depth

    random.seed()

    for _ in range(10):
        bits: int = random.randrange(0, bench.depth * 2)

        bit_stream_in: list[int] = random.choices((0, 1), k=bits)

        for bit in bit_stream_in:
            model.pop()
            model.insert(0, bit)

        await bench.write(bit_stream_in)

        bit_stream_out: list[int] = await bench.read()

        for i, bit in enumerate(bit_stream_out):
            assert bit == model[i], "Mismatch between written and read data"
