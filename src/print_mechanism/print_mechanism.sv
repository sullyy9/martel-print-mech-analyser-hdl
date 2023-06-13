`ifndef PRINT_MECHANISM_SV
`define PRINT_MECHANISM_SV

`timescale 1ns / 1ps

module print_mechanism #(
    parameter logic [31:0] HEAD_WIDTH = 384
) (
    input logic clk,
    input logic reset,

    input logic mech_clk,
    input logic mech_data,
    input logic mech_latch,
    input logic mech_dst,

    input logic motor_phase_a,
    input logic motor_phase_b,
    input logic motor_phase_na,
    input logic motor_phase_nb,

    output logic print_line_ready,
    output logic [HEAD_WIDTH-1:0] print_line

);

    logic print_line_ready_reg, print_line_ready_next;
    logic [HEAD_WIDTH-1:0] print_line_reg, print_line_next;

    logic [HEAD_WIDTH-1:0] burn_line_reg, burn_line_next;

    logic head_active;
    logic [HEAD_WIDTH-1:0] head_active_dots;
    logic line_advance_tick, line_reverse_tick;

    thermal_head #(
        .HEAD_WIDTH(HEAD_WIDTH)
    ) thermal_head (
        .clk,
        .reset,
        .mech_clk,
        .mech_data,
        .mech_latch,
        .mech_dst,

        .head_active,
        .head_active_dots
    );

    stepper_motor stepper_motor (
        .clk,
        .reset,
        .motor_phase_a,
        .motor_phase_b,
        .motor_phase_na,
        .motor_phase_nb,
        .line_advance_tick,
        .line_reverse_tick
    );

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            print_line_ready_reg <= '0;
            print_line_reg <= '0;
            burn_line_reg <= '0;

        end else begin
            print_line_ready_reg <= print_line_ready_next;
            print_line_reg <= print_line_next;
            burn_line_reg <= burn_line_next;
        end
    end

    always_comb begin
        print_line_next = print_line_reg;
        print_line_ready_next = '0;
        burn_line_next = burn_line_reg;

        if (head_active) begin
            burn_line_next = burn_line_reg | head_active_dots;
        end

        if (line_advance_tick) begin
            print_line_next = burn_line_reg;
            print_line_ready_next = 1'b1;
            burn_line_next = '0;
        end
    end

    assign print_line_ready = print_line_ready_reg;
    assign print_line = print_line_reg;

endmodule

`endif
