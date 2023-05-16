`ifndef CONVERTER_BIN2GRAY_SV
`define CONVERTER_BIN2GRAY_SV

`timescale 1ns / 1ps

module converter_bin2gray #(
    parameter logic [31:0] DATA_WIDTH = 8

) (
    input  logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH-1:0] data_out
);
    assign data_out = {data_in[DATA_WIDTH-1], data_in[DATA_WIDTH-1:1] ^ data_in[DATA_WIDTH-2:0]};

endmodule

`endif
