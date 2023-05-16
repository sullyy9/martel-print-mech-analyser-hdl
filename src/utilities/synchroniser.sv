`ifndef SYNCHRONISER_SV
`define SYNCHRONISER_SV

`timescale 1ns / 1ps

module synchroniser #(
    parameter logic [31:0] WIDTH = 1
) (
    input logic clk,
    input logic reset,

    input  logic [WIDTH-1:0] d_in,
    output logic [WIDTH-1:0] d_out
);

    logic [WIDTH-1:0] d_buf;

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            d_buf <= '0;
            d_out <= '0;
        end else begin
            d_buf <= d_in;
            d_out <= d_buf;
        end
    end

endmodule

`endif
