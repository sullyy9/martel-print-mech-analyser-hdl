`ifndef CONVERTER_GRAY2BIN_SV
`define CONVERTER_GRAY2BIN_SV

`timescale 1ns / 1ps

module converter_gray2bin #(
    parameter logic [31:0] DATA_WIDTH = 8

) (
    input  logic [DATA_WIDTH-1:0] data_in,
    output logic [DATA_WIDTH-1:0] data_out
);

    generate
        genvar i;
        for (i = 0; i < DATA_WIDTH; i = i + 1) begin : gen_bin
            assign data_out[i] = ^data_in[DATA_WIDTH-1:i];
        end
    endgenerate

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, converter_gray2bin);
        #1;
    end
`endif

endmodule

`endif
