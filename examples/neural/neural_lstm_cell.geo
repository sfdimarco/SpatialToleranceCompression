NAME neural_lstm_cell

# ── LSTM-style Gated Recurrent Unit ──────────────────────────────
#
# A simplified LSTM cell with forget gate, input gate, and output gate.
# Demonstrates sequential memory and gating mechanisms.
#
# Grid layout (4x3):
#       col0       col1        col2
# row3: [XT]       [pad]       [HT-1]   - Input and previous hidden
# row2: [FT]       [IT]        [OT]     - Gates (forget, input, output)
# row1: [CELL]     [pad]       [CAND]   - Cell state and candidate
# row0: [pad]      [HT]        [pad]    - New hidden state
#
# Computation (simplified LSTM):
#   ft = sigmoid(Wf·[ht-1, xt] + bf)  - Forget gate
#   it = sigmoid(Wi·[ht-1, xt] + bi)  - Input gate
#   ct_cand = tanh(Wc·[ht-1, xt] + bc) - Candidate
#   ct = ft * ct-1 + it * ct_cand     - Cell state update
#   ot = sigmoid(Wo·[ht-1, xt] + bo)  - Output gate
#   ht = ot * tanh(ct)                - New hidden
#
# Execution phases (tick%8):
#   Phase 0: Inputs present xt and ht-1
#   Phase 1-2: Compute gates (ft, it, ot)
#   Phase 3-4: Compute candidate ct_cand
#   Phase 5: Update cell state ct
#   Phase 6-7: Compute output ht

# ── Phase 0: Inputs ───────────────────────────────────────────────
RULE IF own_prog=input_xt AND tick%8=0
     THEN HOLD + SET_VAR xt (100 if mask=1111 else 0) AS in_xt

RULE IF own_prog=input_ht AND tick%8=0
     THEN HOLD + SET_VAR ht_prev (100 if family=Y_LOOP else 0) AS in_ht

# ── Phase 1-2: Forget gate ────────────────────────────────────────
# ft = sigmoid(w·[ht-1, xt]) ≈ threshold at 100

RULE IF own_prog=forget AND tick%8=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E ht_prev 1
          + ACCUM_VAR sum W xt 1
          + CLAMP_VAR sum 0 200 AS ft_accum

RULE IF own_prog=forget AND tick%8=2 AND var_sum>=100
     THEN HOLD + SET_VAR ft 100 AS ft_on

RULE IF own_prog=forget AND tick%8=2 AND var_sum<100
     THEN HOLD + SET_VAR ft 0 AS ft_off

# ── Phase 1-2: Input gate ─────────────────────────────────────────
RULE IF own_prog=input_gate AND tick%8=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E ht_prev 1
          + ACCUM_VAR sum W xt 1
          + CLAMP_VAR sum 0 200 AS it_accum

RULE IF own_prog=input_gate AND tick%8=2 AND var_sum>=100
     THEN HOLD + SET_VAR it 100 AS it_on

RULE IF own_prog=input_gate AND tick%8=2 AND var_sum<100
     THEN HOLD + SET_VAR it 0 AS it_off

# ── Phase 1-2: Output gate ────────────────────────────────────────
RULE IF own_prog=output_gate AND tick%8=1
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E ht_prev 1
          + ACCUM_VAR sum W xt 1
          + CLAMP_VAR sum 0 200 AS ot_accum

RULE IF own_prog=output_gate AND tick%8=2 AND var_sum>=100
     THEN HOLD + SET_VAR ot 100 AS ot_on

RULE IF own_prog=output_gate AND tick%8=2 AND var_sum<100
     THEN HOLD + SET_VAR ot 0 AS ot_off

# ── Phase 3-4: Candidate cell state ───────────────────────────────
RULE IF own_prog=candidate AND tick%8=3
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum E ht_prev 1
          + ACCUM_VAR sum W xt 1
          + CLAMP_VAR sum 0 200 AS cand_accum

# Tanh approximation: map [0,200] → [-100,100]
RULE IF own_prog=candidate AND tick%8=4
     THEN HOLD + SET_VAR ct_cand (var_sum - 100) AS cand_tanh

# ── Phase 5: Cell state update ────────────────────────────────────
# ct = ft * ct_prev + it * ct_cand

RULE IF own_prog=cell AND tick%8=5
     THEN HOLD + SET_VAR ct_new 0
          + ACCUM_VAR ct_new N ft (var_ct_prev / 100)  # ft * ct_prev
          + ACCUM_VAR ct_new E it (var_ct_cand / 100)  # it * ct_cand
          + CLAMP_VAR ct_new -100 100 AS cell_update

# ── Phase 6-7: Hidden state output ────────────────────────────────
# ht = ot * tanh(ct)

RULE IF own_prog=hidden AND tick%8=6
     THEN HOLD + SET_VAR ct_tanh var_ct_new
          + INCR_VAR ct_tanh -100 if var_ct_tanh>0 else 0 AS ht_tanh

RULE IF own_prog=hidden AND tick%8=7 AND var_ot>=100
     THEN SWITCH Y_LOOP + SET_VAR ht var_ct_tanh AS ht_on

RULE IF own_prog=hidden AND tick%8=7 AND var_ot<100
     THEN GATE_OFF + SET_VAR ht 0 AS ht_off

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
