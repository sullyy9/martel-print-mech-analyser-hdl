`ifndef INCREMENTER_SV
`define INCREMENTER_SV

`timescale 1ns / 1ps

module incrementer #(
    parameter logic [31:0] MAX_VALUE = 255,
    parameter logic [31:0] INCREMENT = 1
) (
    input  logic [$clog2(MAX_VALUE+1)-1:0] data_in,
    output logic [$clog2(MAX_VALUE+1)-1:0] data_out
);
    localparam logic [$clog2(INCREMENT+1)-1:0] Increment = INCREMENT;
    localparam logic [$clog2(MAX_VALUE+1)-1:0] MaxValue = MAX_VALUE;

    always_comb begin
        data_out = data_in + Increment;

        if (data_in > (MaxValue - Increment)) begin
            data_out = '0;
        end
    end

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, incrementer);
        #1;
    end
`endif

endmodule

`endif
