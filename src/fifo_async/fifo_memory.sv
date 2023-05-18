`ifndef FIFO_MEMORY_SV
`define FIFO_MEMORY_SV

`timescale 1ns / 1ps

module fifo_memory #(
    parameter logic [31:0] DATA_WIDTH = 8,
    parameter logic [31:0] DEPTH = 8
) (
    input logic reset,

    input logic write_clk,
    input logic write_enable,
    input logic [$clog2(DATA_WIDTH*(DEPTH-1))-1:0] write_address,
    input logic [DATA_WIDTH-1:0] write_data,

    input logic [$clog2(DATA_WIDTH*(DEPTH-1))-1:0] read_address,
    output logic [DATA_WIDTH-1:0] read_data

);
    logic [(DATA_WIDTH*DEPTH)-1:0] buffer;

    always @(posedge write_clk or negedge reset) begin
        if (!reset) begin
            buffer <= '0;

        end else if (write_enable) begin
            buffer[write_address+:DATA_WIDTH] <= write_data;
        end
    end

    assign read_data = buffer[read_address+:DATA_WIDTH];

endmodule

`endif
