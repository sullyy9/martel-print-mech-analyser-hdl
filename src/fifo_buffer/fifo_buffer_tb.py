import random
from queue import Queue
from typing import Final

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly


class FIFOBufferTB:
    def __init__(self, dut) -> None:
        self.rst: Final = dut.reset

        self.write_clk: Final = dut.write_clk
        self.write_enable: Final = dut.write_enable
        self.write_data: Final = dut.write_data

        self.read_clk: Final = dut.read_clk
        self.read_enable: Final = dut.read_enable
        self.read_data: Final = dut.read_data

        self.empty: Final = dut.empty
        self.full: Final = dut.full

        self.capacity: Final[int] = dut.CAPACITY.value

        self.rst.value = 1

        self.write_clk.value = 0
        self.write_enable.value = 0
        self.write_data.value = 0
        
        self.read_clk.value = 0
        self.read_enable.value = 0

    async def reset(self) -> None:
        await RisingEdge(self.write_clk)
        self.rst.value = 0
        await ClockCycles(self.write_clk, 1)
        self.rst.value = 1
        await ClockCycles(self.write_clk, 1)

    async def write(self, byte: int) -> None:
        await RisingEdge(self.write_clk)
        self.write_data.value = byte
        self.write_enable.value = 1
        await ClockCycles(self.write_clk, 1)
        self.write_data.value = 0
        self.write_enable.value = 0

    async def read(self) -> int:
        await RisingEdge(self.read_clk)
        self.read_enable.value = 1
        await ReadOnly()
        byte = self.read_data.value
        await RisingEdge(self.read_clk)
        self.read_enable.value = 0
        
        return byte

    async def is_full(self) -> bool:
        await ReadOnly()
        return True if self.full.value == 1 else False

    async def is_empty(self) -> bool:
        await ReadOnly()
        return True if self.empty.value == 1 else False



@cocotb.test()  # type: ignore
async def run_test(dut):
    fifo_tb: Final[FIFOBufferTB] = FIFOBufferTB(dut)

    cocotb.start_soon(Clock(fifo_tb.write_clk, 1, units="ns").start())
    cocotb.start_soon(Clock(fifo_tb.read_clk, 1, units="ns").start())

    await fifo_tb.reset()

    model: Queue[int] = Queue(maxsize=fifo_tb.capacity)

    random.seed()

    for _ in range(10):
        bytes_to_write: int = random.randrange(0, fifo_tb.capacity)
        bytes_to_read: int = random.randrange(0, fifo_tb.capacity)

        for _ in range(bytes_to_write):
            byte: int = random.randint(0, 255)
            await fifo_tb.write(byte)
            model.put(byte)

            if(model.full()):
                assert await fifo_tb.is_full(), "Expected fifo to be full."
                break
        
        for _ in range(bytes_to_read):
            byte: int = await fifo_tb.read()

            assert byte == model.get(), "Mismatch between read bytes"

            if(model.empty()):
                assert await fifo_tb.is_empty(), "Expected fifo to be empty."
                break
    
    for _ in range(model.qsize()):
        byte: int = await fifo_tb.read()
        assert byte == model.get(), "Mismatch between read bytes"

    assert await fifo_tb.is_empty(), "Expected fifo to be empty."
