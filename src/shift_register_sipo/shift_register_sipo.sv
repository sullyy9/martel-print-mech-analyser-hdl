`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
///
//////////////////////////////////////////////////////////////////////////////////

module shift_register_sipo #(
    parameter logic [31:0] DEPTH = 8
) (
    input logic clk,
    input logic reset,
    input logic write_data,
    input logic write_enable,
    output logic [DEPTH-1:0] read_data
);

    logic [DEPTH-1:0] buffer, buffer_next;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            buffer <= '0;

        end else begin
            buffer <= buffer_next;
        end
    end

    always_comb begin
        buffer_next = buffer;

        if (write_enable) begin
            buffer_next = {buffer[DEPTH-1:1], write_data};
        end
    end

    assign read_data = buffer;


`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, shift_register_sipo);
        #1;
    end
`endif

endmodule
