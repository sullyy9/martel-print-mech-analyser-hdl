`ifndef SHIFT_REGISTER_SV
`define SHIFT_REGISTER_SV

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

module shift_register #(
    parameter logic [31:0] DEPTH = 8
) (
    input logic clk,
    input logic reset,

    input logic data_in,
    input logic enable,

    output logic [DEPTH-1:0] data_out
);

    logic [DEPTH-1:0] data_reg, data_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_reg <= '0;

        end else if (enable) begin
            data_reg <= data_next;
        end
    end

    assign data_out  = data_reg;
    assign data_next = {data_reg[DEPTH-2:0], data_in};


endmodule

`endif
