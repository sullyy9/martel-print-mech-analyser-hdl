`ifndef FIFO_COUNTER_SV
`define FIFO_COUNTER_SV

`timescale 1ns / 1ps

module fifo_counter #(
    parameter logic [31:0] DATA_WIDTH = 8,
    parameter logic [31:0] DEPTH = 8
) (
    input logic clk,
    input logic reset,
    input logic enable,

    output logic [$clog2(DATA_WIDTH*DEPTH)-1:0] address,
    output logic [$clog2(DEPTH)-1:0] ptr
);
    counter_gray #(
        .MAX_VALUE(DEPTH - 1),
        .INCREMENT(1)
    ) pointer_counter (
        .clk,
        .reset,
        .enable,
        .count(ptr)
    );

    counter_binary #(
        .MAX_VALUE(DATA_WIDTH * (DEPTH - 1)),
        .INCREMENT(DATA_WIDTH)
    ) address_counter (
        .clk,
        .reset,
        .enable,
        .count(address)
    );

endmodule

`endif
