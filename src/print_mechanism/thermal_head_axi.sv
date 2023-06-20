`ifndef THERMAL_HEAD_AXI_SV
`define THERMAL_HEAD_AXI_SV

`timescale 1ns / 1ps

module thermal_head_axi #(
    parameter logic [31:0] HEAD_WIDTH = 384
) (
    input logic clk,
    input logic reset,

    input logic mech_clk,
    input logic mech_data,
    input logic mech_latch,
    input logic mech_dst,

    input logic axi_ready,
    output logic axi_valid,
    output logic [HEAD_WIDTH-1:0] axi_data
);

    logic head_active, head_active_sync;
    logic [HEAD_WIDTH-1:0] head_active_dots;

    logic head_data_sent_reg, head_data_sent_next;

    thermal_head #(
        .HEAD_WIDTH(HEAD_WIDTH)
    ) thermal_head (
        .clk(mech_clk),
        .reset,

        .data (mech_data),
        .latch(mech_latch),
        .dst  (mech_dst),

        .head_active,
        .head_active_dots
    );

    // Synchronise the head active signal to ensure the data will be valid.
    synchroniser head_active_synchroniser (
        .clk,
        .reset,

        .d_in (head_active),
        .d_out(head_active_sync)
    );

    logic axi_valid_reg, axi_valid_next;
    logic [HEAD_WIDTH-1:0] axi_data_reg, axi_data_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            axi_valid_reg <= '0;
            axi_data_reg  <= '0;
            head_data_sent_reg <= '0;

        end else begin
            axi_valid_reg <= axi_valid_next;
            axi_data_reg  <= axi_data_next;
            head_data_sent_reg <= head_data_sent_next;
        end
    end

    always_comb begin
        axi_valid_next = axi_valid_reg;
        axi_data_next  = axi_data_reg;
        head_data_sent_next = head_data_sent_reg;

        // De-assert valid after transfer complete.
        if (axi_valid && axi_ready) begin
            axi_valid_next = '0;
            axi_data_next  = '0;
        end

        // Buffer next data if we're not waiting to transfer.
        if (head_active_sync && !axi_valid && !head_data_sent_reg) begin
            axi_valid_next = 1'b1;
            axi_data_next  = head_active_dots;
            head_data_sent_next = 1'b1;
        end

        if (!head_active_sync) begin
            head_data_sent_next = '0;
        end
    end

    assign axi_valid = axi_valid_reg;
    assign axi_data  = axi_data_reg;

endmodule

`endif
