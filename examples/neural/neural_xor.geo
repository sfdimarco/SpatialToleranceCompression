NAME neural_xor

# ── 2-Layer Perceptron solving XOR ──────────────────────────────────
#
# Grid layout (3x3):
#
#       col0     col1    col2
# row2: [IN0]    [H0]    [IN1]
# row1: [pad]    [OUT]   [pad]
# row0: [IN0c]   [H1]    [IN1c]
#
# IN0, IN1:   Input neurons. GATE_ON=1, GATE_OFF=0.
#             Store activation in var "a" (100=on, 0=off).
# IN0c,IN1c: Relay copies — mirror their column's input var "a".
# H0:  Hidden neuron 0 — OR gate (threshold=1).
#      Reads W=IN0.a and E=IN1.a, fires if sum >= 100.
# H1:  Hidden neuron 1 — AND gate (threshold=2).
#      Reads W=IN0c.a and E=IN1c.a, fires if sum >= 200.
# OUT: Output — H0 AND NOT H1 = XOR.
#      Reads N=H0.a and S=H1.a, fires if H0-H1 > 0.
#
# XOR truth table:
#   IN0=0, IN1=0 → H0=0, H1=0 → OUT=0
#   IN0=1, IN1=0 → H0=1, H1=0 → OUT=1
#   IN0=0, IN1=1 → H0=1, H1=0 → OUT=1
#   IN0=1, IN1=1 → H0=1, H1=1 → OUT=0
#
# Execution phases (tick modulo 4):
#   Phase 0: Inputs write var "a" from their mask state
#   Phase 1: Relays copy input "a" via signals (or just hold — set by init)
#   Phase 2: Hidden neurons accumulate and activate
#   Phase 3: Output reads hidden activations and decides

# ── Phase 0: Inputs set var "a" ─────────────────────────────────────
# Inputs are identified by own_prog. They set a=100 if ON, a=0 if OFF.

RULE IF own_prog=input AND mask=1111 AND tick%4=0
     THEN HOLD + SET_VAR a 100 AS in_on

RULE IF own_prog=input AND mask=0000 AND tick%4=0
     THEN HOLD + SET_VAR a 0 AS in_off

# ── Phase 0: Relays copy from their north neighbor's "a" ───────────
# IN0c at (0,0) copies from IN0 at (2,0) — but they're not adjacent.
# Instead, relays are initialized with same mask as their input and
# use the same logic to set var "a".

RULE IF own_prog=relay AND mask=1111 AND tick%4=0
     THEN HOLD + SET_VAR a 100 AS relay_on

RULE IF own_prog=relay AND mask=0000 AND tick%4=0
     THEN HOLD + SET_VAR a 0 AS relay_off

# ── Phase 2: Hidden neuron H0 — OR gate (threshold >= 100) ─────────
# H0 at (2,1): W neighbor = IN0, E neighbor = IN1

RULE IF own_prog=h0 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W a 1
          + ACCUM_VAR sum E a 1
          + CLAMP_VAR sum 0 200 AS h0_accum

RULE IF own_prog=h0 AND tick%4=3 AND var_sum>=100
     THEN HOLD + SET_VAR a 100 AS h0_fire

RULE IF own_prog=h0 AND tick%4=3 AND var_sum<100
     THEN HOLD + SET_VAR a 0 AS h0_quiet

# ── Phase 2: Hidden neuron H1 — AND gate (threshold >= 200) ────────
# H1 at (0,1): W neighbor = IN0c, E neighbor = IN1c

RULE IF own_prog=h1 AND tick%4=2
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W a 1
          + ACCUM_VAR sum E a 1
          + CLAMP_VAR sum 0 200 AS h1_accum

RULE IF own_prog=h1 AND tick%4=3 AND var_sum>=200
     THEN HOLD + SET_VAR a 100 AS h1_fire

RULE IF own_prog=h1 AND tick%4=3 AND var_sum<200
     THEN HOLD + SET_VAR a 0 AS h1_quiet

# ── Phase 3: Output — XOR = H0 AND NOT H1 ──────────────────────────
# OUT at (1,1): N neighbor = H0, S neighbor = H1
# Fires when H0.a >= 100 AND H1.a < 100  →  H0.a - H1.a > 0
# We accumulate: sum = H0.a * 1 + H1.a * (-1), fire if sum >= 100

RULE IF own_prog=output AND tick%4=0
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum N a 1
          + ACCUM_VAR sum S a -1
          + CLAMP_VAR sum -100 100 AS out_accum

RULE IF own_prog=output AND tick%4=1 AND var_sum>=100
     THEN SWITCH Y_LOOP + SET_VAR a 100 AS out_fire

RULE IF own_prog=output AND tick%4=1 AND var_sum<100
     THEN GATE_OFF + SET_VAR a 0 AS out_quiet

# Keep output visual state stable on non-decision ticks
RULE IF own_prog=output AND var_a>=100
     THEN HOLD AS out_hold_on

RULE IF own_prog=output
     THEN HOLD AS out_hold_off

# ── Default ─────────────────────────────────────────────────────────
DEFAULT HOLD
