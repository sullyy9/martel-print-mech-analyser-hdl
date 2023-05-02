`ifndef TB_UART_TRANSMITTER
`define TB_UART_TRANSMITTER

`timescale 1ns / 1ps

module uart_transmitter #(
    parameter logic [31:0] CLKS_PER_BIT = 12000000 / 115200
) (
    input  logic       clk,
    input  logic       reset,
    input  logic       enable,
    input  logic [7:0] data,
    output logic       port,
    output logic       active,
    output logic       ready
);

    typedef enum logic [2:0] {
        STATE_IDLE,
        STATE_TX_START,
        STATE_TX_DATA,
        STATE_TX_STOP,
        STATE_IDLE_HOLDOFF
    } state_t;

    state_t state, next_state;

    integer unsigned       clock_count;
    logic            [7:0] data_buffer;
    logic            [2:0] bit_index;
    logic                  bit_clocked;

    always_ff @(posedge clk or negedge reset) begin
        if (!reset) begin
            state       <= STATE_IDLE;
            clock_count <= '0;
            data_buffer <= '0;
            bit_index   <= '0;
        end else begin
            state <= next_state;

            if (active && bit_clocked) begin
                clock_count <= '0;
            end else if (active) begin
                clock_count <= clock_count + 1;
            end

            if (state == STATE_TX_DATA && bit_clocked) begin
                bit_index <= bit_index + 1;
            end

            if (state == STATE_IDLE && enable) begin
                data_buffer <= data;
            end
        end
    end

    // State behaviour.
    always_comb begin
        unique case (state)
            STATE_IDLE: begin
                port = '1;
            end

            STATE_TX_START: begin
                port = '0;
            end

            STATE_TX_DATA: begin
                port = data_buffer[bit_index];
            end

            STATE_TX_STOP: begin
                port = '1;
            end

            STATE_IDLE_HOLDOFF: begin
                port = '1;
            end

            default: begin
                port = '1;
            end
        endcase

    end

    // State switching.
    always_comb begin
        unique case (state)
            STATE_IDLE: begin
                if (enable) begin
                    next_state = STATE_TX_START;
                end else begin
                    next_state = state;
                end
            end

            STATE_TX_START: begin
                if (bit_clocked) begin
                    next_state = STATE_TX_DATA;
                end else begin
                    next_state = state;
                end
            end

            STATE_TX_DATA: begin
                if (bit_clocked && bit_index >= 7) begin
                    next_state = STATE_TX_STOP;
                end else begin
                    next_state = state;
                end
            end

            STATE_TX_STOP: begin
                if (bit_clocked) begin
                    next_state = STATE_IDLE_HOLDOFF;
                end else begin
                    next_state = state;
                end
            end

            STATE_IDLE_HOLDOFF: begin
                next_state = STATE_IDLE;
            end

            default: begin
                next_state = STATE_IDLE;
            end
        endcase
    end

    assign bit_clocked = clock_count >= CLKS_PER_BIT - 1;
    assign active = state == STATE_TX_START || state == STATE_TX_DATA || state == STATE_TX_STOP;
    assign ready = state == STATE_IDLE;

`ifdef COCOTB_SIM
    initial begin
        $dumpfile("waveforms.vcd");
        $dumpvars(0, uart_transmitter);
        #1;
    end
`endif

endmodule

`endif
