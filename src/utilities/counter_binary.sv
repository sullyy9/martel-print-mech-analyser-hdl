`ifndef COUNTER_BINARY_SV
`define COUNTER_BINARY_SV

`timescale 1ns / 1ps

module counter_binary #(
    parameter logic [31:0] MAX_VALUE = 255,
    parameter logic [31:0] INCREMENT = 1
) (
    input logic clk,
    input logic reset,
    input logic enable,

    output logic [$clog2(MAX_VALUE+1)-1:0] count
);
    logic [$clog2(MAX_VALUE+1)-1:0] count_reg, count_next;

    incrementer #(
        .MAX_VALUE(MAX_VALUE),
        .INCREMENT(INCREMENT)

    ) count_incrementer (
        .data_in (count_reg),
        .data_out(count_next)
    );

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            count_reg <= 0;

        end else if (enable) begin
            count_reg <= count_next;
        end
    end

    assign count = count_reg;

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, counter_binary);
        #1;
    end
`endif

endmodule

`endif
