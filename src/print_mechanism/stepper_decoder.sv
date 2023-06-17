`ifndef STEPPER_DECODER_SV
`define STEPPER_DECODER_SV

`timescale 1ns / 1ps

module stepper_decoder (
    input logic clk,
    input logic reset,

    input logic motor_phase_a,
    input logic motor_phase_b,
    input logic motor_phase_na,
    input logic motor_phase_nb,

    output logic [2:0] step,
    output logic invalid

);
    localparam logic [3:0] Step[8] = {
        4'b1000, 4'b1100, 4'b0100, 4'b0110, 4'b0010, 4'b0011, 4'b0001, 4'b1001
    };

    localparam logic [3:0] InterStep[8] = {
        4'b1000, 4'b1110, 4'b0100, 4'b0111, 4'b0010, 4'b1011, 4'b0001, 4'b1101
    };

    logic invalid_reg, invalid_next;
    logic [2:0] step_reg, step_next;

    logic [3:0] step_code;
    assign step_code = {motor_phase_a, motor_phase_b, motor_phase_na, motor_phase_nb};


    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            step_reg <= '0;
            invalid_reg <= '0;

        end else begin
            step_reg <= step_next;
            invalid_reg <= invalid_next;
        end
    end

    always_comb begin
        step_next = step_reg;
        invalid_next = '0;

        unique case (step_code)
            Step[0]:               step_next = 3'd0;
            Step[1], InterStep[1]: step_next = 3'd1;
            Step[2]:               step_next = 3'd2;
            Step[3], InterStep[3]: step_next = 3'd3;
            Step[4]:               step_next = 3'd4;
            Step[5], InterStep[5]: step_next = 3'd5;
            Step[6]:               step_next = 3'd6;
            Step[7], InterStep[7]: step_next = 3'd7;
            default:               invalid_next = 1'b1;

        endcase

    end

    assign step = step_reg;
    assign invalid = invalid_reg;

endmodule

`endif
