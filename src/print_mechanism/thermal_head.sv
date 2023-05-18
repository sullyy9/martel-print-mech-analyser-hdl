`ifndef THERMAL_HEAD_SV
`define THERMAL_HEAD_SV

`timescale 1ns / 1ps

module thermal_head #(
    parameter logic [31:0] HEAD_WIDTH = 384
) (
    input logic clk,
    input logic reset,

    input logic mech_clk,
    input logic mech_data,
    input logic mech_latch,
    input logic mech_dst,

    output logic head_active,
    output logic [HEAD_WIDTH-1:0] head_active_dots

);

    logic [HEAD_WIDTH-1:0] data_buffer_reg, data_buffer_next;
    logic [HEAD_WIDTH-1:0] latch_buffer_reg, latch_buffer_next;
    logic [HEAD_WIDTH-1:0] head_buffer_reg, head_buffer_next;

    logic latch_armed_reg, latch_armed_next;
    logic head_active_reg, head_active_next;

    //////////////////////////////////////////////////
    // Data fifo.
    //////////
    logic data_fifo_write_enable;
    logic data_fifo_read_enable;
    logic data_fifo_read_data;
    logic data_fifo_full;
    logic data_fifo_empty;

    fifo_async #(
        .DATA_WIDTH(1),
        .DEPTH(64)
    ) mech_data_buffer (
        .reset,

        .write_clk(mech_clk),
        .write_enable(data_fifo_write_enable),
        .write_data(mech_data),

        .read_clk(clk),
        .read_enable(data_fifo_read_enable),
        .read_data(data_fifo_read_data),

        .empty(data_fifo_empty),
        .full (data_fifo_full)
    );

    assign data_fifo_read_enable = !data_fifo_empty;

    //////////////////////////////////////////////////
    // Data buffer logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            data_buffer_reg <= '0;
            data_fifo_write_enable <= '0;

        end else begin
            data_fifo_write_enable <= '1;
            data_buffer_reg <= data_buffer_next;

        end
    end

    always_comb begin
        data_buffer_next = data_buffer_reg;

        if (!data_fifo_empty) begin
            data_buffer_next = {data_buffer_reg[HEAD_WIDTH-2:0], data_fifo_read_data};
        end
    end

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
            latch_armed_next = 1'b1;
        end

        if (!mech_latch && latch_armed_reg) begin
            latch_buffer_next = data_buffer_reg;
            latch_armed_next  = '0;
        end
    end

    //////////////////////////////////////////////////
    // DST / head buffer logic.
    //////////
    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            head_active_reg <= '0;
            head_buffer_reg <= '0;

        end else begin
            head_active_reg <= head_active_next;
            head_buffer_reg <= head_buffer_next;
        end
    end

    assign head_active_next = mech_dst;
    assign head_buffer_next = latch_buffer_reg;

    assign head_active = head_active_reg;
    assign head_active_dots = head_buffer_reg;

endmodule

`endif
