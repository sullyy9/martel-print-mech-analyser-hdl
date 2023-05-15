from typing import Final
from pathlib import Path

VERLIOG_SOURCES: Final[list[Path]] = [
    Path("src/fifo_async/fifo_async.sv"),
    Path("src/fifo_async/fifo_counter.sv"),
    Path("src/fifo_async/fifo_memory.sv"),
    
    Path("src/fifo_buffer/fifo_buffer.sv"),

    Path("src/main/main.sv"),
    
    Path("src/print_mechanism/print_mechanism.sv"),

    Path("src/shift_register_sipo/shift_register_sipo.sv"),

    Path("src/uart_transmitter/uart_transmitter.sv"),

    Path("src/utilities/counter_gray.sv"),
    Path("src/utilities/counter_binary.sv"),
    Path("src/utilities/converter_bin2gray.sv"),
    Path("src/utilities/converter_gray2bin.sv"),
    Path("src/utilities/synchroniser.sv"),
    Path("src/utilities/incrementer.sv"),
]

OUTPUT_DIRECTORY: Final[Path] = Path("sim_build")
