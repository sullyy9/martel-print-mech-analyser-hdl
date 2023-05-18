`ifndef FIFO_POINTER_SYNCHRONISER_SV
`define FIFO_POINTER_SYNCHRONISER_SV

`timescale 1ns / 1ps

module fifo_pointer_synchroniser #(
    parameter logic [31:0] POINTER_WIDTH = 8
) (
    input logic clk,
    input logic reset,

    input logic [POINTER_WIDTH-1:0] pointer_async,
    output logic [POINTER_WIDTH-1:0] pointer_sync
);
    logic [POINTER_WIDTH-1:0] pointer_async_gray;
    logic [POINTER_WIDTH-1:0] pointer_sync_gray;

    converter_bin2gray #(
        .DATA_WIDTH(POINTER_WIDTH)
    ) async_converter (
        .data_in (pointer_async),
        .data_out(pointer_async_gray)
    );

    synchroniser #(
        .WIDTH(POINTER_WIDTH)

    ) write_ptr_synchroniser (
        .clk,
        .reset,

        .d_in (pointer_async_gray),
        .d_out(pointer_sync_gray)
    );

    converter_gray2bin #(
        .DATA_WIDTH(POINTER_WIDTH)
    ) sync_converter (
        .data_in (pointer_sync_gray),
        .data_out(pointer_sync)
    );

endmodule

`endif
