`ifndef MAIN_SV
`define MAIN_SV 


`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

module main (
    input logic clk,
    input logic reset,

    output logic led1,
    output logic led2,

    input logic mech_clk,
    input logic mech_data,
    input logic mech_latch,
    input logic mech_dst,
    input logic motor_phase_a,
    input logic motor_phase_b,
    input logic motor_phase_na,
    input logic motor_phase_nb,

    output logic mech_clk_out,
    output logic mech_data_out,
    output logic mech_latch_out,
    output logic mech_dst_out,
    output logic motor_phase_a_out,
    output logic motor_phase_b_out,
    output logic motor_phase_na_out,
    output logic motor_phase_nb_out,

    output logic uart_tx_pin_1,
    output logic uart_tx_pin_2
);
    localparam logic [31:0] MechHeadWidth = 384;

    //////////////////////////////////////////////////
    // UART.
    //////////
    logic uart_buffer_write_enable_reg, uart_buffer_write_enable_next;
    logic [7:0] uart_buffer_write_data_reg, uart_buffer_write_data_next;

    logic uart_buffer_read_enable;
    logic [7:0] uart_buffer_read_data;

    logic uart_buffer_empty;
    logic uart_buffer_full;

    fifo_buffer #(
        .DATA_WIDTH(8),
        .CAPACITY  (256)
    ) uart_tx_buffer (
        .reset,

        .write_clk(clk),
        .write_enable(uart_buffer_write_enable_reg),
        .write_data(uart_buffer_write_data_reg),

        .read_clk(clk),
        .read_enable(uart_buffer_read_enable),
        .read_data(uart_buffer_read_data),

        .empty(uart_buffer_empty),
        .full (uart_buffer_full)
    );

    logic uart_enable;
    logic [7:0] uart_data;
    logic uart_active;
    logic uart_ready;

    uart_transmitter #(
        .CLKS_PER_BIT(180_000_000 / 460_800)
    ) uart_tx (
        .clk,
        .reset,

        .enable(uart_enable),
        .data  (uart_data),
        .port  (uart_tx_pin_1),
        .active(uart_active),
        .ready (uart_ready)
    );

    assign uart_enable = !uart_buffer_empty;
    assign uart_data = uart_buffer_read_data;
    assign uart_buffer_read_enable = uart_ready && !uart_buffer_empty;

    //////////////////////////////////////////////////
    // Print mechanism.
    //////////
    logic mech_line_ready;
    logic [MechHeadWidth-1:0] mech_print_line;

    print_mechanism #(
        .HEAD_WIDTH(MechHeadWidth)
    ) print_mech (
        .clk,
        .reset,

        .mech_clk,
        .mech_data,
        .mech_latch,
        .mech_dst,
        .motor_phase_a,
        .motor_phase_b,
        .motor_phase_na,
        .motor_phase_nb,

        .line_advance_tick(mech_line_ready),
        .print_line(mech_print_line)
    );

    //////////////////////////////////////////////////
    // .
    //////////
    typedef enum logic [2:0] {
        STATE_IDLE,

        STATE_BUFFER_LINE_CMD_START,
        STATE_BUFFER_LINE_CMD_RUN,
        STATE_BUFFER_LINE_CMD_END,

        STATE_TRANSMISSION_START,
        STATE_TRANSMISSION_END

    } state_t;

    state_t state_reg, state_next;

    localparam logic [31:0] LineCMDLen = (6 * 8) + MechHeadWidth;
    localparam logic [LineCMDLen-1:0] LineCMDDefault = {":", 384'd0, ":", "E", "N", "I", "L"};

    logic [LineCMDLen-1:0] line_cmd_reg, line_cmd_next;

    logic [31:0] line_cmd_ptr_reg, line_cmd_ptr_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state_reg <= STATE_IDLE;

            line_cmd_reg <= LineCMDDefault;
            line_cmd_ptr_reg <= 0;

            uart_buffer_write_enable_reg <= '0;
            uart_buffer_write_data_reg <= '0;

        end else begin
            state_reg <= state_next;

            line_cmd_reg <= line_cmd_next;
            line_cmd_ptr_reg <= line_cmd_ptr_next;

            uart_buffer_write_enable_reg <= uart_buffer_write_enable_next;
            uart_buffer_write_data_reg <= uart_buffer_write_data_next;
        end
    end

    always_comb begin
        state_next = STATE_IDLE;

        line_cmd_next = line_cmd_reg;
        line_cmd_ptr_next = '0;

        uart_buffer_write_enable_next = '0;
        uart_buffer_write_data_next = '0;

        unique case (state_reg)
            STATE_IDLE: begin
                if (mech_line_ready) begin
                    state_next = STATE_BUFFER_LINE_CMD_START;
                end
            end

            STATE_BUFFER_LINE_CMD_START: begin
                // Load the payload into the command reg.
                line_cmd_next = {":", mech_print_line, ":", "E", "N", "I", "L"};

                state_next = STATE_BUFFER_LINE_CMD_RUN;
            end

            STATE_BUFFER_LINE_CMD_RUN: begin
                // Write the command into the buffer.
                uart_buffer_write_enable_next = '1;
                uart_buffer_write_data_next = line_cmd_reg[line_cmd_ptr_reg+:8];
                line_cmd_ptr_next = line_cmd_ptr_reg + 8;

                if (line_cmd_ptr_next >= LineCMDLen) begin
                    state_next = STATE_BUFFER_LINE_CMD_END;

                end else begin
                    state_next = STATE_BUFFER_LINE_CMD_RUN;

                end
            end

            STATE_BUFFER_LINE_CMD_END: begin
                state_next = STATE_IDLE;
            end

            STATE_TRANSMISSION_START: begin

            end

            STATE_TRANSMISSION_END: begin

            end

            default: begin

            end

        endcase
    end

    assign mech_clk_out = mech_clk;
    assign mech_data_out = mech_data;
    assign mech_latch_out = mech_latch;
    assign mech_dst_out = mech_dst;
    assign motor_phase_a_out = motor_phase_a;
    assign motor_phase_b_out = motor_phase_b;
    assign motor_phase_na_out = motor_phase_na;
    assign motor_phase_nb_out = motor_phase_nb;

    assign uart_tx_pin_2 = uart_tx_pin_1;

    assign led1 = 1'b1;
    assign led2 = 1'b1;

endmodule

`endif
