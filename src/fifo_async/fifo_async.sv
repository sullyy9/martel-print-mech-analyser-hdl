`ifndef FIFO_ASYNC_SV
`define FIFO_ASYNC_SV

`timescale 1ns / 1ps

module fifo_async #(
    parameter logic [31:0] DATA_WIDTH = 8,
    parameter logic [31:0] DEPTH = 8
) (
    input logic reset,

    input logic write_clk,
    input logic write_enable,
    input logic [DATA_WIDTH-1:0] write_data,

    input logic read_clk,
    input logic read_enable,
    output logic [DATA_WIDTH-1:0] read_data,

    output logic full,
    output logic empty
);

    logic [$clog2(DATA_WIDTH*DEPTH)-1:0] write_address, read_address;
    logic [$clog2(DEPTH)-1:0] write_ptr_async, read_ptr_async;
    logic [$clog2(DEPTH)-1:0] write_ptr_sync, read_ptr_sync;

    //////////////////////////////////////////////////
    // Counters.
    //////////
    fifo_counter #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)

    ) write_counter (
        .clk(write_clk),
        .reset,
        .enable(write_enable & !full),

        .address(write_address),
        .pointer(write_ptr_async)
    );

    fifo_counter #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)

    ) read_counter (
        .clk(read_clk),
        .reset,
        .enable(read_enable & !empty),

        .address(read_address),
        .pointer(read_ptr_async)
    );

    //////////////////////////////////////////////////
    // Synchronisers.
    //////////
    fifo_pointer_synchroniser #(
        .POINTER_WIDTH($clog2(DEPTH))

    ) write_pointer_synchroniser (
        .clk(read_clk),
        .reset,
        .pointer_async(write_ptr_async),
        .pointer_sync(write_ptr_sync)
    );

    fifo_pointer_synchroniser #(
        .POINTER_WIDTH($clog2(DEPTH))

    ) read_pointer_synchroniser (
        .clk(write_clk),
        .reset,
        .pointer_async(read_ptr_async),
        .pointer_sync(read_ptr_sync)
    );

    //////////////////////////////////////////////////
    // Empty / full logic.
    //////////
    logic [$clog2(DEPTH)-1:0] write_ptr_async_next;

    incrementer #(
        .MAX_VALUE(DEPTH - 1),
        .INCREMENT(1)

    ) write_ptr_async_bin_incrementer (
        .data_in (write_ptr_async),
        .data_out(write_ptr_async_next)
    );


    assign empty = (write_ptr_sync == read_ptr_async);
    assign full  = (write_ptr_async_next == read_ptr_sync);

    //////////////////////////////////////////////////
    // Buffer read / write.
    //////////

    fifo_memory #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)

    ) memory (
        .reset,

        .write_clk,
        .write_enable(write_enable & !full),
        .write_address,
        .write_data,

        .read_address,
        .read_data
    );

endmodule

`endif
