import os
from pathlib import Path

import cocotb_test.simulator


def test_uart_transmitter():
    src: list[str] = ["uart_transmitter.sv"]
    src_dir = Path(os.path.dirname(__file__), "uart_transmitter")

    src_path: list[Path] = [Path(src_dir, s) for s in src]

    cocotb_test.simulator.run(
        verilog_sources=src_path,
        toplevel="uart_transmitter",
        module="uart_transmitter.uart_transmitter_tb",
        sim_build="./sim_build/uart_transmitter",
    )


def test_fifo_buffer():
    src: list[str] = ["fifo_buffer.sv"]
    src_dir = Path(os.path.dirname(__file__), "fifo_buffer")

    src_path: list[Path] = [Path(src_dir, s) for s in src]

    cocotb_test.simulator.run(
        verilog_sources=src_path,
        toplevel="fifo_buffer",
        module="fifo_buffer.fifo_buffer_tb",
        defines="TEST_NAME=fifo_buffer",
        sim_build="./sim_build/fifo_buffer",
    )


def test_shift_register_sipo():
    src: list[str] = ["shift_register_sipo.sv"]
    src_dir = Path(os.path.dirname(__file__), "shift_register_sipo")

    src_path: list[Path] = [Path(src_dir, s) for s in src]

    cocotb_test.simulator.run(
        verilog_sources=src_path,
        toplevel="shift_register_sipo",
        module="shift_register_sipo.shift_register_sipo_tb",
        sim_build="./sim_build/shift_register_sipo",
    )


# def test_print_mechanism():
#     src_dir = Path(os.path.dirname(__file__))

#     src: list[str] = [
#         "print_mechanism/print_mechanism.sv",
#     ]
#     src_path: list[Path] = [Path(src_dir, s) for s in src]

#     inc: list[Path] = [Path(src_dir, "./fifo_buffer")]

#     cocotb_test.simulator.run(
#         verilog_sources=src_path,
#         includes=inc,
#         toplevel="print_mechanism",
#         module="print_mechanism.print_mechanism_tb",
#         sim_build="./sim_build/print_mechanism",
#     )


def test_main():
    src_dir = Path(os.path.dirname(__file__))

    src: list[str] = [
        "main/main.sv",
    ]
    src_path: list[Path] = [Path(src_dir, s) for s in src]

    inc: list[Path] = [
        Path(src_dir, "./fifo_buffer"),
        Path(src_dir, "./print_mechanism"),
        Path(src_dir, "./uart_transmitter"),
    ]

    cocotb_test.simulator.run(
        verilog_sources=src_path,
        includes=inc,
        toplevel="main",
        module="main.main_tb",
        sim_build="./sim_build/main",
    )
