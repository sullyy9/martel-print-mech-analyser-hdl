`ifndef TB_PRINT_MECHANISM
`define TB_PRINT_MECHANISM

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

`include "../fifo_buffer/fifo_buffer.sv"

module print_mechanism #(
    parameter logic [31:0] HEAD_WIDTH = 384
) (
    input logic clk,
    input logic reset,
    input logic mech_clk,
    input logic mech_data,
    input logic mech_latch,
    input logic mech_dst,
    input logic mech_motor_phase_a,
    input logic mech_motor_phase_b,

    output logic line_advance_tick,
    output logic [HEAD_WIDTH - 1:0] print_line

);

    logic [HEAD_WIDTH - 1:0] data_buffer_reg, data_buffer_next;
    logic [HEAD_WIDTH - 1:0] latch_buffer_reg, latch_buffer_next;
    logic [HEAD_WIDTH - 1:0] burn_buffer_reg, burn_buffer_next;
    logic [HEAD_WIDTH - 1:0] line_buffer_reg, line_buffer_next;

    logic latch_armed_reg, latch_armed_next;

    logic [1:0] motor_state_reg, motor_state_next;
    logic [3:0] motor_step_reg, motor_step_next;

    logic line_ready_reg, line_ready_next;

    logic mech_buffer_write_enable;
    logic mech_buffer_read_enable;
    logic mech_buffer_read_data;
    logic mech_buffer_full;
    logic mech_buffer_empty;

    fifo_buffer #(
        .DATA_WIDTH(1),
        .CAPACITY  (64)
    ) mech_data_buffer (
        .reset,

        .write_clk(mech_clk),
        .write_enable(mech_buffer_write_enable),
        .write_data(mech_data),

        .read_clk(clk),
        .read_enable(mech_buffer_read_enable),
        .read_data(mech_buffer_read_data),

        .empty(mech_buffer_empty),
        .full (mech_buffer_full)
    );

    //////////////////////////////////////////////////
    // Data buffer logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_buffer_reg <= '0;
            mech_buffer_write_enable <= '0;

        end else begin
            mech_buffer_write_enable <= '1;

            if (mech_buffer_read_enable) begin
                data_buffer_reg <= data_buffer_next;
            end
        end
    end

    assign mech_buffer_read_enable = !mech_buffer_empty;
    assign data_buffer_next = {data_buffer_reg[HEAD_WIDTH-2:0], mech_buffer_read_data};

    //////////////////////////////////////////////////
    // Latch buffer logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            latch_buffer_reg <= '0;
            latch_armed_reg  <= '0;

        end else begin
            latch_buffer_reg <= latch_buffer_next;
            latch_armed_reg  <= latch_armed_next;

        end
    end

    always_comb begin
        latch_buffer_next = latch_buffer_reg;
        latch_armed_next  = '0;

        if (mech_latch) begin
            latch_armed_next = '1;
        end

        if (!mech_latch && latch_armed_reg) begin
            latch_buffer_next = data_buffer_reg;
            latch_armed_next  = '0;
        end
    end

    //////////////////////////////////////////////////
    // DST / burn buffer logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            burn_buffer_reg <= '0;

        end else begin
            burn_buffer_reg <= burn_buffer_next;

        end
    end

    always_comb begin
        burn_buffer_next = burn_buffer_reg;

        if (mech_dst) begin
            burn_buffer_next = burn_buffer_reg | latch_buffer_reg;
        end

        if (motor_step_reg >= 4) begin
            burn_buffer_next = '0;
        end
    end

    //////////////////////////////////////////////////
    // Motor logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            line_buffer_reg <= '0;

            motor_state_reg <= 0;
            motor_step_reg  <= 0;

            line_ready_reg  <= 0;

        end else begin
            line_buffer_reg <= line_buffer_next;

            motor_state_reg <= motor_state_next;
            motor_step_reg  <= motor_step_next;

            line_ready_reg  <= line_ready_next;
        end
    end

    always_comb begin
        line_buffer_next = line_buffer_reg;

        motor_state_next = motor_state_reg;
        motor_step_next  = motor_step_reg;

        line_ready_next  = '0;

        // Motor logic
        if (motor_state_reg != {mech_motor_phase_a, mech_motor_phase_b}) begin
            motor_state_next = {mech_motor_phase_a, mech_motor_phase_b};
            motor_step_next  = motor_step_reg + 2;
        end

        if (motor_step_reg >= 4) begin
            motor_step_next  = 0;
            line_buffer_next = burn_buffer_reg;
            line_ready_next  = '1;
        end

    end

    assign print_line = line_buffer_reg;
    assign line_advance_tick = line_ready_reg;

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, print_mechanism);
        #1;
    end
`endif

endmodule

`endif
