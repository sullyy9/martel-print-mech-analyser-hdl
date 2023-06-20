`ifndef GLITCH_FILTER_SV
`define GLITCH_FILTER_SV

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

module glitch_filter #(
    parameter logic [31:0] SAMPLES = 4
) (
    input logic clk,
    input logic reset,

    input  logic data_in,
    output logic data_out
);

    logic data_reg, data_next;
    logic [SAMPLES-1:0] samples;

    shift_register #(
        .DEPTH(SAMPLES)
    ) shift_register_dut (
        .clk,
        .reset,

        .data_in,
        .enable  (1'b1),
        .data_out(samples)
    );


    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_reg <= '0;

        end else begin
            data_reg <= data_next;
        end
    end

    always_comb begin
        data_next = data_reg;

        if (samples == '1) begin
            data_next = 1'b1;
        end

        if (samples == '0) begin
            data_next = '0;
        end

    end

    assign data_out = data_reg;


endmodule

`endif
