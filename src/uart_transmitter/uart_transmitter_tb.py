import random
from typing import Final

import cocotb
import cocotb.utils
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, ReadOnly


class UARTTransmitterTB:
    def __init__(self, dut) -> None:
        self.clk: Final = dut.clk
        self.rst: Final = dut.reset
        self.enable: Final = dut.enable
        self.data: Final = dut.data
        self.port: Final = dut.port
        self.active: Final = dut.active

        self.clks_per_bit: Final[int] = dut.CLKS_PER_BIT.value

        self.clk.value = 0
        self.rst.value = 1
        self.enable.value = 0
        self.data.value = 0

    async def reset(self) -> None:
        await RisingEdge(self.clk)
        self.rst.value = 0
        await ClockCycles(self.clk, 1)
        self.rst.value = 1

    async def transmit(self, byte: int) -> None:
        await RisingEdge(self.clk)
        self.data.value = byte
        self.enable.value = 1
        await ClockCycles(self.clk, 1)
        self.data.value = 0
        self.enable.value = 0

    async def monitor(self) -> int:
        await RisingEdge(self.enable)

        data_bits: list[int] = []

        # Check the start bit.
        for cycle in range(self.clks_per_bit):
            await RisingEdge(self.clk)
            await ReadOnly()

            assert self.active.value == 1, "Expected active signal to be active"
            assert self.port.value == 0, (
                f"Expected continuation of start bit in cycle: "
                f"{cycle}/{self.clks_per_bit}"
            )

        # Check each data bit.
        for i in range(8):
            await RisingEdge(self.clk)
            await ReadOnly()

            assert self.active.value == 1, "Expected active signal to be active"

            data_bits.append(self.port.value)
            for cycle in range(self.clks_per_bit - 1):
                await RisingEdge(self.clk)
                await ReadOnly()

                assert self.active.value == 1, "Expected active signal to be active"
                assert self.port.value == data_bits[-1], (
                    f"Expected continuation of data bit {i} in cycle: "
                    f"{cycle}/{self.clks_per_bit}"
                )

        # Check the stop bit.
        for cycle in range(self.clks_per_bit):
            await RisingEdge(self.clk)
            await ReadOnly()

            assert self.active.value == 1, "Expected active signal to be active"
            assert self.port.value == 1, (
                f"Expected continuation of stop bit in cycle: "
                f"{cycle}/{self.clks_per_bit}"
            )

        await RisingEdge(self.clk)
        await ReadOnly()
        assert self.active.value == 0, "Expected active signal to be inactive"

        data: int = 0
        for i, bit in enumerate(data_bits):
            data += bit << i

        return data


@cocotb.test()  # type: ignore
async def run_test(dut):
    uart_tx = UARTTransmitterTB(dut)

    cocotb.start_soon(Clock(uart_tx.clk, 1, units="ns").start())
    await uart_tx.reset()
    await ClockCycles(uart_tx.clk, 1)

    # Start transmission
    for _ in range(20):
        monitor = cocotb.start_soon(uart_tx.monitor())

        data_in: int = random.randint(0, 255)
        await uart_tx.transmit(data_in)
        data_out: int = await monitor

        assert data_out == data_in

    dut._log.info("enable is %s", uart_tx.enable.value)
