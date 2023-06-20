`ifndef SYNCHRONISER_SV
`define SYNCHRONISER_SV

`timescale 1ns / 1ps

module synchroniser #(
    parameter logic [31:0] WIDTH  = 1,
    parameter logic [31:0] STAGES = 2
) (
    input logic clk,
    input logic reset,

    input  logic [WIDTH-1:0] d_in,
    output logic [WIDTH-1:0] d_out
);

    (* ASYNC_REG = "TRUE" *) logic [(WIDTH*STAGES)-1:0] data_reg, data_next;

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_reg <= '0;
        end else begin
            data_reg <= data_next;
        end
    end

    assign data_next = {data_reg[((WIDTH*STAGES)-1)-WIDTH:0], d_in};

    assign d_out = data_reg[((WIDTH*STAGES)-1)-:WIDTH];

endmodule

`endif
