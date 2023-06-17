`ifndef STEPPER_MOTOR_SV
`define STEPPER_MOTOR_SV

`timescale 1ns / 1ps

module stepper_motor (
    input logic clk,
    input logic reset,

    input logic motor_phase_a,
    input logic motor_phase_b,
    input logic motor_phase_na,
    input logic motor_phase_nb,

    output logic line_advance_tick,
    output logic line_reverse_tick,

    output logic invalid_step,
    output logic invalid_state
);
    logic [1:0] motor_adv_step_reg, motor_adv_step_next;  // 4 steps per dot line.
    logic [1:0] motor_rev_step_reg, motor_rev_step_next;  // 4 steps per dot line.
    logic line_advance_reg, line_advance_next;
    logic line_reverse_reg, line_reverse_next;

    logic invalid_step_reg, invalid_step_next;
    logic invalid_state_reg, invalid_state_next;
    logic [2:0] step_reg, step_next;

    stepper_decoder decoder (
        .clk,
        .reset,

        .motor_phase_a,
        .motor_phase_b,
        .motor_phase_na,
        .motor_phase_nb,

        .step(step_next),
        .invalid(invalid_state_next)
    );


    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            motor_adv_step_reg <= '0;
            motor_rev_step_reg <= '0;
            line_advance_reg <= '0;
            line_reverse_reg <= '0;

            step_reg <= '0;
            invalid_step_reg <= '0;
            invalid_state_reg <= '0;

        end else begin
            motor_adv_step_reg <= motor_adv_step_next;
            motor_rev_step_reg <= motor_rev_step_next;
            line_advance_reg <= line_advance_next;
            line_reverse_reg <= line_reverse_next;

            step_reg <= step_next;
            invalid_step_reg <= invalid_step_next;
            invalid_state_reg <= invalid_state_next;
        end
    end

    always_comb begin
        motor_adv_step_next = motor_adv_step_reg;
        motor_rev_step_next = motor_rev_step_reg;
        line_advance_next   = '0;
        line_reverse_next   = '0;

        invalid_step_next   = '0;

        unique case (step_next)
            (step_reg + 3'd1): motor_adv_step_next = motor_adv_step_reg + 2'd1;
            (step_reg + 3'd2): motor_adv_step_next = motor_adv_step_reg + 2'd2;

            (step_reg - 3'd1): motor_rev_step_next = motor_rev_step_reg + 2'd1;
            (step_reg - 3'd2): motor_rev_step_next = motor_rev_step_reg + 2'd2;

            default: invalid_step_next = 1'b1;
        endcase

        // Rollover
        if (motor_adv_step_next < motor_adv_step_reg) begin
            line_advance_next = 1'b1;
        end else if (motor_rev_step_next < motor_rev_step_reg) begin
            line_reverse_next = 1'b1;
        end

        if (motor_adv_step_next < motor_rev_step_next) begin
            motor_rev_step_next -= motor_adv_step_next;
            motor_adv_step_next = '0;

        end else if (motor_rev_step_next < motor_adv_step_next) begin
            motor_adv_step_next -= motor_rev_step_next;
            motor_rev_step_next = '0;

        end else if (motor_rev_step_next == motor_adv_step_next) begin
            motor_adv_step_next = '0;
            motor_rev_step_next = '0;
        end


    end

    assign line_advance_tick = line_advance_reg;
    assign line_reverse_tick = line_reverse_reg;

    assign invalid_step = invalid_step_reg;
    assign invalid_state = invalid_state_reg;

endmodule

`endif
