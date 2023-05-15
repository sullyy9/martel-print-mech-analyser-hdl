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
    //////////////////////////////////////////////////
    // Counters.
    //////////
    logic [$clog2(DATA_WIDTH*DEPTH)-1:0] write_address, read_address;
    logic [$clog2(DEPTH)-1:0] write_ptr_async_gray, read_ptr_async_gray;
    logic [$clog2(DEPTH)-1:0] write_ptr_async_bin, read_ptr_async_bin;

    fifo_counter #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)

    ) write_counter (
        .clk(write_clk),
        .reset,
        .enable(write_enable & !full),

        .address(write_address),
        .ptr(write_ptr_async_gray)
    );

    converter_gray2bin #(
        .DATA_WIDTH($clog2(DEPTH))
    ) write_ptr_async_converter (
        .data_in (write_ptr_async_gray),
        .data_out(write_ptr_async_bin)
    );


    fifo_counter #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)

    ) read_counter (
        .clk(read_clk),
        .reset,
        .enable(read_enable & !empty),

        .address(read_address),
        .ptr(read_ptr_async_gray)
    );

    converter_gray2bin #(
        .DATA_WIDTH($clog2(DEPTH))
    ) read_ptr_async_converter (
        .data_in (read_ptr_async_gray),
        .data_out(read_ptr_async_bin)
    );

    //////////////////////////////////////////////////
    // Synchronisers.
    //////////
    logic [$clog2(DEPTH)-1:0] write_ptr_sync_gray, read_ptr_sync_gray;
    logic [$clog2(DEPTH)-1:0] write_ptr_sync_bin, read_ptr_sync_bin;

    synchroniser #(
        .WIDTH($clog2(DEPTH))

    ) write_ptr_synchroniser (
        .clk(read_clk),
        .reset,

        .d_in (write_ptr_async_gray),
        .d_out(write_ptr_sync_gray)
    );

    converter_gray2bin #(
        .DATA_WIDTH($clog2(DEPTH))
    ) write_ptr_sync_converter (
        .data_in (write_ptr_sync_gray),
        .data_out(write_ptr_sync_bin)
    );

    synchroniser #(
        .WIDTH($clog2(DEPTH))

    ) read_ptr_synchroniser (
        .clk(write_clk),
        .reset,

        .d_in (read_ptr_async_gray),
        .d_out(read_ptr_sync_gray)
    );

    converter_gray2bin #(
        .DATA_WIDTH($clog2(DEPTH))
    ) read_ptr_sync_converter (
        .data_in (read_ptr_sync_gray),
        .data_out(read_ptr_sync_bin)
    );

    //////////////////////////////////////////////////
    // Empty / full logic.
    //////////
    logic [$clog2(DEPTH)-1:0] write_ptr_async_bin_next;

    incrementer #(
        .MAX_VALUE(DEPTH - 1),
        .INCREMENT(1)

    ) write_ptr_async_bin_incrementer (
        .data_in (write_ptr_async_bin),
        .data_out(write_ptr_async_bin_next)
    );


    assign empty = (write_ptr_sync_gray == read_ptr_async_gray);
    assign full  = (write_ptr_async_bin_next == read_ptr_sync_bin);

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

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, fifo_async);
        #1;
    end
`endif

endmodule

`endif
