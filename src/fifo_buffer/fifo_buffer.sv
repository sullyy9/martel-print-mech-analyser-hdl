`ifndef TB_FIFO_BUFFER
`define TB_FIFO_BUFFER

`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

module fifo_buffer #(
    parameter logic [ 8:0] DATA_WIDTH = 8,
    parameter logic [31:0] CAPACITY   = 256
) (
    input logic reset,

    input logic                    write_clk,
    input logic                    write_enable,
    input logic [DATA_WIDTH - 1:0] write_data,

    input  logic                    read_clk,
    input  logic                    read_enable,
    output logic [DATA_WIDTH - 1:0] read_data,

    output logic empty,
    output logic full
);
    logic [CAPACITY - 1:0][DATA_WIDTH - 1:0] buffer;
    logic [$clog2(CAPACITY) - 1:0] write_ptr_reg, write_ptr_next;
    logic [$clog2(CAPACITY) - 1:0] read_ptr_reg, read_ptr_next;
    logic [$clog2(CAPACITY):0] count_reg;

    // Write logic.
    always_ff @(posedge write_clk or negedge reset) begin
        if (!reset) begin
            buffer <= '0;
            write_ptr_reg <= '0;
            count_reg <= '0;

        end else begin
            if (write_enable) begin
                buffer[write_ptr_reg] <= write_data;
                count_reg <= count_reg + 1;
            end

            write_ptr_reg <= write_ptr_next;
        end
    end

    // Read logic.
    always_ff @(posedge read_clk or negedge reset) begin
        if (!reset) begin
            // read_data <= '0;
            read_ptr_reg <= '0;

            count_reg <= '0;

        end else begin
            if (read_enable) begin
                // read_data <= buffer[read_ptr_reg];
                count_reg <= count_reg - 1;
            end

            read_ptr_reg <= read_ptr_next;
        end
    end

    always_comb begin
        read_data = '0;

        write_ptr_next = write_ptr_reg;
        read_ptr_next = read_ptr_reg;

        if (write_enable && read_enable) begin
            read_data = buffer[read_ptr_reg];

            write_ptr_next = write_ptr_reg + 1;
            read_ptr_next = read_ptr_reg + 1;

        end else if (write_enable) begin
            write_ptr_next = write_ptr_reg + 1;

        end else if (read_enable) begin
            read_data = buffer[read_ptr_reg];
            read_ptr_next = read_ptr_reg + 1;
        end
    end

    assign empty = write_ptr_reg == read_ptr_reg;
    assign full  = count_reg == CAPACITY;

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, fifo_buffer);
        #1;
    end
`endif

endmodule

`endif
