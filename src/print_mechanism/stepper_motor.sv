`ifndef STEPPER_MOTOR_SV
`define STEPPER_MOTOR_SV

`timescale 1ns / 1ps

module stepper_motor (
    input logic clk,
    input logic reset,

    input logic motor_phase_a,
    input logic motor_phase_b,

    output logic line_advance_tick
);

    logic [1:0] motor_state_reg, motor_state_next;
    logic [3:0] motor_step_reg, motor_step_next;

    logic line_advance_reg, line_advance_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            motor_state_reg  <= '0;
            motor_step_reg   <= '0;
            line_advance_reg <= '0;

        end else begin
            motor_state_reg  <= motor_state_next;
            motor_step_reg   <= motor_step_next;

            line_advance_reg <= line_advance_next;
        end
    end

    always_comb begin
        motor_state_next  = motor_state_reg;
        motor_step_next   = motor_step_reg;

        line_advance_next = '0;

        // Motor logic
        if (motor_state_reg != {motor_phase_a, motor_phase_b}) begin
            motor_state_next = {motor_phase_a, motor_phase_b};
            motor_step_next  = motor_step_reg + 4'd2;
        end

        if (motor_step_reg >= 4) begin
            motor_step_next   = '0;
            line_advance_next = 1'b1;
        end
    end

    assign line_advance_tick = line_advance_reg;

endmodule

`endif
