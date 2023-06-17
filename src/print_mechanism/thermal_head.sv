`ifndef THERMAL_HEAD_SV
`define THERMAL_HEAD_SV

`timescale 1ns / 1ps

module thermal_head #(
    parameter logic [31:0] HEAD_WIDTH = 384
) (
    input logic clk,
    input logic reset,

    input logic data,
    input logic latch,
    input logic dst,

    output logic head_active,
    output logic [HEAD_WIDTH-1:0] head_active_dots
);

    logic [HEAD_WIDTH-1:0] data_reg;
    logic [HEAD_WIDTH-1:0] latch_reg;
    logic [HEAD_WIDTH-1:0] head_reg;

    //////////////////////////////////////////////////
    // Data logic.
    //////////

    shift_register #(
        .DEPTH(HEAD_WIDTH)
    ) data_shift_register (
        .clk,
        .reset,

        .data_in(data),
        .enable (reset),

        .data_out(data_reg)
    );

    //////////////////////////////////////////////////
    // Latch & DST logic.
    //////////
    always_latch begin
        if (!reset) begin
            latch_reg = '0;

        end else if (!latch) begin
            latch_reg = data_reg;
        end
    end

    always_latch begin
        if (!reset) begin
            head_reg = '0;

        end else if (dst) begin
            head_reg = latch_reg;

        end
    end

    assign head_active = dst;
    assign head_active_dots = head_reg;

endmodule

`endif
