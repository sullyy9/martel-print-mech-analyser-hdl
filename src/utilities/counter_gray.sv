`ifndef COUNTER_GRAY_SV
`define COUNTER_GRAY_SV

`timescale 1ns / 1ps

module counter_gray #(
    parameter logic [31:0] MAX_VALUE = 255,
    parameter logic [31:0] INCREMENT = 1
) (
    input logic clk,
    input logic reset,
    input logic enable,

    output logic [$clog2(MAX_VALUE+1)-1:0] count
);
    logic [$clog2(MAX_VALUE+1)-1:0] count_bin;

    counter_binary #(
        .MAX_VALUE(MAX_VALUE),
        .INCREMENT(INCREMENT)

    ) binary_counter (
        .clk,
        .reset,
        .enable,
        .count(count_bin)
    );

    converter_bin2gray #(
        .DATA_WIDTH($clog2(MAX_VALUE + 1))

    ) gray_converter (
        .data_in (count_bin),
        .data_out(count)
    );

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, counter_gray);
        #1;
    end
`endif

endmodule

`endif
