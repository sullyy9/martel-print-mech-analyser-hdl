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
    output logic line_reverse_tick
);
    localparam logic [3:0] Step[8] = {
        4'b1000, 4'b1100, 4'b0100, 4'b0110, 4'b0010, 4'b0011, 4'b0001, 4'b1001
    };

    logic [3:0] motor_state, motor_state_last;
    assign motor_state = {motor_phase_a, motor_phase_b, motor_phase_na, motor_phase_nb};

    logic [1:0] motor_adv_step_reg, motor_adv_step_next;  // 4 steps per dot line.
    logic [1:0] motor_rev_step_reg, motor_rev_step_next;  // 4 steps per dot line.
    logic line_advance_reg, line_advance_next;
    logic line_reverse_reg, line_reverse_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            motor_state_last   <= motor_state;
            motor_adv_step_reg <= '0;
            motor_rev_step_reg <= '0;
            line_advance_reg   <= '0;
            line_reverse_reg   <= '0;

        end else begin
            motor_state_last   <= motor_state;
            motor_adv_step_reg <= motor_adv_step_next;
            motor_rev_step_reg <= motor_rev_step_next;
            line_advance_reg   <= line_advance_next;
            line_reverse_reg   <= line_reverse_next;
        end
    end

    always_comb begin
        motor_adv_step_next = motor_adv_step_reg;
        motor_rev_step_next = motor_rev_step_reg;
        line_advance_next   = '0;
        line_reverse_next   = '0;

        unique case (motor_state_last)
            Step[0]: begin
                if (motor_state == Step[1]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[2]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[7]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[6]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[1]: begin
                if (motor_state == Step[2]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[3]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[0]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[7]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[2]: begin
                if (motor_state == Step[3]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[4]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[1]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[0]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[3]: begin
                if (motor_state == Step[4]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[5]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[2]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[1]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[4]: begin
                if (motor_state == Step[5]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[6]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[3]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[2]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[5]: begin
                if (motor_state == Step[6]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[7]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[4]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[3]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[6]: begin
                if (motor_state == Step[7]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[0]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[5]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[4]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            Step[7]: begin
                if (motor_state == Step[0]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd1;
                end else if (motor_state == Step[1]) begin
                    motor_adv_step_next = motor_adv_step_reg + 2'd2;
                end else if (motor_state == Step[6]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd1;
                end else if (motor_state == Step[5]) begin
                    motor_rev_step_next = motor_rev_step_reg + 2'd2;
                end
            end

            default: begin
                motor_adv_step_next = '0;
                motor_rev_step_next = '0;
            end

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

endmodule

`endif
