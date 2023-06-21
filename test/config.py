from typing import Final
from pathlib import Path

from cocotb import runner

VERLIOG_SOURCES: Final[list[Path]] = [
    Path("src/fifo_async/fifo_async.sv"),
    Path("src/fifo_async/fifo_counter.sv"),
    Path("src/fifo_async/fifo_memory.sv"),
    Path("src/fifo_async/fifo_pointer_synchroniser.sv"),
    Path("src/fifo_buffer/fifo_buffer.sv"),
    Path("src/print_mechanism/stepper_decoder.sv"),
    Path("src/print_mechanism/stepper_motor.sv"),
    Path("src/print_mechanism/thermal_head.sv"),
    Path("src/print_mechanism/print_mechanism.sv"),
    Path("src/uart_transmitter/uart_transmitter.sv"),
    Path("src/utilities/counter_gray.sv"),
    Path("src/utilities/counter_binary.sv"),
    Path("src/utilities/converter_bin2gray.sv"),
    Path("src/utilities/converter_gray2bin.sv"),
    Path("src/utilities/shift_register.sv"),
    Path("src/utilities/synchroniser.sv"),
    Path("src/utilities/incrementer.sv"),
]

MODULES: Final = [
    "fifo_async",
    "stepper_motor",
    "thermal_head",
    "counter_binary",
    "counter_gray",
    "shift_register",
]

OUTPUT_DIRECTORY: Final = Path("sim_build")
BUILD_DIRECTORY: Final[Path] = Path(OUTPUT_DIRECTORY, "build")

SIMULATOR: Final = runner.get_runner("verilator")
SIM_ARGS: Final[list[str]] = [
    "--build-jobs",
    "8",
    "--verilate-jobs",
    "8",
    "--trace-fst",
    "--trace-structs",
    "-O2",
    "--x-assign",
    "fast",
    "--x-initial",
    "fast",
    "--noassert",
    "--output-split",
    "10000",
]


def run_test(
    toplevel: str, output_directory: Path, test_module: str, parameters: dict[str, int] | None = None
) -> None:
    if parameters:
        SIMULATOR.build(
            verilog_sources=VERLIOG_SOURCES,
            hdl_toplevel=toplevel,
            build_dir=output_directory,
            build_args=SIM_ARGS,
            parameters=parameters,
        )
    else:
        SIMULATOR.build(
            verilog_sources=VERLIOG_SOURCES,
            hdl_toplevel=toplevel,
            build_dir=output_directory,
            build_args=SIM_ARGS,
        )
    
    SIMULATOR.test(
        hdl_toplevel_lang="verilog",
        hdl_toplevel=toplevel,
        test_module=test_module,
        build_dir=output_directory,
        test_dir=output_directory,
    )


def build_sources(toplevel: str, parameters: dict[str, int] | None = None) -> None:
    if parameters:
        SIMULATOR.build(
            verilog_sources=VERLIOG_SOURCES,
            hdl_toplevel=toplevel,
            build_dir=Path(OUTPUT_DIRECTORY, toplevel),
            build_args=SIM_ARGS,
            parameters=parameters,
        )
    else:
        SIMULATOR.build(
            verilog_sources=VERLIOG_SOURCES,
            hdl_toplevel=toplevel,
            build_dir=Path(OUTPUT_DIRECTORY, toplevel),
            build_args=SIM_ARGS,
        )
