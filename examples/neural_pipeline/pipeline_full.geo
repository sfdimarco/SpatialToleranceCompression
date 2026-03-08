NAME neural_pipeline_full

# ── Pattern Recognition Pipeline: Complete Integrated System ─────
#
# Simplified version compatible with .geo parser limitations.
# Python handles weight computation, .geo handles state propagation.
#
# Execution Flow:
#   tick%4=0: Input present, feature map reads inputs
#   tick%4=1: Feature map computes distances (via Python)
#   tick%4=2: Winner selected, memory loads
#   tick%4=3: Memory converges, output displayed

# ── Input Layer Rules ─────────────────────────────────────────────
RULE IF own_prog=pixel AND mask=1111
     THEN HOLD + SET_VAR active 100 AS pixel_on

RULE IF own_prog=pixel AND mask=0000
     THEN HOLD + SET_VAR active 0 AS pixel_off

# ── Feature Map Rules (SOM) ───────────────────────────────────────
# Accumulate input from neighbors

RULE IF own_prog=feature AND tick%4=0
     THEN HOLD + SET_VAR dist 0
          + ACCUM_VAR dist N active 1
          + ACCUM_VAR dist S active 1
          + ACCUM_VAR dist E active 1
          + ACCUM_VAR dist W active 1
          AS feat_accum

RULE IF own_prog=feature AND tick%4=1
     THEN HOLD + CLAMP_VAR dist 0 500 AS feat_clamp

# Winner selection

RULE IF own_prog=feature AND tick%4=2 AND var_dist<100
     THEN HOLD + SET_VAR winner 1 + EMIT winner_found AS feat_winner

RULE IF own_prog=feature AND tick%4=2 AND var_dist>=100
     THEN HOLD + SET_VAR winner 0 AS feat_loser

# Weight update (simplified - Python handles actual weight math)

RULE IF own_prog=feature AND tick%4=3 AND var_winner=1
     THEN HOLD + INCR_VAR gen_counter 1 AS feat_update

RULE IF own_prog=feature AND tick%4=3
     THEN HOLD AS feat_hold

# ── Memory Layer Rules (Hopfield) ─────────────────────────────────

RULE IF own_prog=memory AND tick%4=0
     THEN HOLD + SET_VAR sum 0
          + ACCUM_VAR sum W state 1
          + ACCUM_VAR sum E state 1
          + ACCUM_VAR sum N state 1
          + ACCUM_VAR sum S state 1
          AS mem_accum

RULE IF own_prog=memory AND tick%4=1 AND var_sum>=50
     THEN HOLD + SET_VAR state 100 AS mem_on

RULE IF own_prog=memory AND tick%4=1 AND var_sum<50
     THEN HOLD + SET_VAR state 0 AS mem_off

RULE IF own_prog=memory AND tick%4=2 AND var_state>=100
     THEN SWITCH Y_LOOP AS mem_vis_on

RULE IF own_prog=memory AND tick%4=2 AND var_state<100
     THEN GATE_OFF AS mem_vis_off

RULE IF own_prog=memory AND tick%4=3
     THEN HOLD AS mem_hold

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
