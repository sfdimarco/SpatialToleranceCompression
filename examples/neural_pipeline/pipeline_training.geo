NAME neural_pipeline_training

# ── Pattern Recognition Pipeline: Training System ────────────────
#
# Implements self-organizing learning rules for the pipeline.
# Combines competitive learning (SOM) with Hebbian learning (memory).
#
# Training Modes:
#   1. UNSUPERVISED: Feature map self-organizes from input statistics
#   2. SUPERVISED: Memory stores specific patterns
#   3. HYBRID: Both layers learn together
#
# Execution phases (tick%32 - extended for training):
#   Phase 0-1: Present input pattern
#   Phase 2-3: Feature map computes distances
#   Phase 4-5: Feature map finds winner
#   Phase 6-7: Feature map updates weights (SOM learning)
#   Phase 8-9: Memory loads feature activation
#   Phase 10-13: Memory recurrent dynamics
#   Phase 14-15: Memory outputs result
#   Phase 16-17: Compute error/reinforcement
#   Phase 18-21: Hebbian learning (memory weight updates)
#   Phase 22-31: Reset and prepare for next pattern
#
# Learning Rate Schedules:
#   Early training: high lr (fast learning)
#   Late training: low lr (fine-tuning)

# ── Training Control Variables ───────────────────────────────────
# Global training state (set externally)
#   var_train_mode: 0=none, 1=unsupervised, 2=supervised, 3=hybrid
#   var_epoch: current training epoch
#   var_lr_base: base learning rate

# ── Phase 0-1: Present Pattern ────────────────────────────────────
RULE IF own_prog=trainer AND tick%32=0 AND var_train_mode>=1
     THEN HOLD + SET_VAR pattern_presented 1 + EMIT present_pattern AS train_start

RULE IF own_prog=trainer AND tick%32=0 AND var_train_mode=0
     THEN HOLD + SET_VAR pattern_presented 0 AS train_idle

# ── Phase 2-5: Feature Map Processing ─────────────────────────────
# (Handled by pipeline_feature_map.geo)
# Trainer monitors and modulates

RULE IF own_prog=trainer AND tick%32=3 AND signal=winner_found
     THEN HOLD + SET_VAR feature_computed 1 AS train_feature_done

# ── Phase 6-7: SOM Weight Update ──────────────────────────────────
# Modulate learning rate based on epoch

RULE IF own_prog=trainer AND tick%32=6
     THEN HOLD
          # Learning rate decay: lr = base_lr / (1 + epoch * 0.1)
          + SET_VAR lr_effective (var_lr_base * 100 / (100 + var_epoch * 10))
          + EMIT set_learning_rate var_lr_effective AS train_set_lr

# ── Phase 8-13: Memory Processing ─────────────────────────────────
# (Handled by pipeline_memory.geo)
# Trainer monitors convergence

RULE IF own_prog=trainer AND tick%32=12 AND var_memory_converged=0
     THEN HOLD + SET_VAR memory_converged 1 AS train_memory_done

# ── Phase 14-15: Output Readout ───────────────────────────────────
RULE IF own_prog=trainer AND tick%32=14
     THEN HOLD + SET_VAR output_read 1
          + SET_VAR classification var_memory_state AS train_read_output

# ── Phase 16-17: Error Computation (Supervised Mode) ─────────────
RULE IF own_prog=trainer AND tick%32=16 AND var_train_mode=2
     THEN HOLD
          # error = target - output
          + SET_VAR error (var_target_class - var_classification)
          + SET_VAR error_abs (abs var_error)
          AS train_compute_error

RULE IF own_prog=trainer AND tick%32=16 AND var_train_mode=1
     THEN HOLD + SET_VAR error 0 AS train_unsupervised_no_error

# ── Phase 18-21: Hebbian Learning ─────────────────────────────────
# Strengthen connections between co-active neurons
# Rule: Δw_ij = η * pre_i * post_j

RULE IF own_prog=trainer AND tick%32=18 AND var_train_mode>=1
     THEN HOLD + EMIT hebbian_update AS train_hebbian_start

# For each memory neuron pair (simplified for demo)
RULE IF own_prog=trainer AND tick%32=19 AND signal=hebbian_update
     THEN HOLD
          # If both neurons active, strengthen connection
          + SET_VAR delta_w (var_lr_effective * var_pre_state * var_post_state / 10000)
          + EMIT update_weight var_delta_w AS train_update_weights

# ── Phase 20-21: Weight Consolidation ─────────────────────────────
RULE IF own_prog=trainer AND tick%32=20
     THEN HOLD + SET_VAR weights_updated 1 AS train_weights_done

# ── Phase 22-31: Reset ────────────────────────────────────────────
RULE IF own_prog=trainer AND tick%32=22
     THEN HOLD + SET_VAR pattern_presented 0
          + SET_VAR feature_computed 0
          + SET_VAR memory_converged 0
          + SET_VAR output_read 0
          + INCR_VAR epoch 1
          AS train_reset

RULE IF own_prog=trainer AND tick%32>=23
     THEN HOLD AS train_wait

# ── Training Progress Tracking ────────────────────────────────────
# Track accuracy, convergence time, etc.

RULE IF own_prog=trainer AND tick%32=15 AND var_classification=var_target
     THEN HOLD + INCR_VAR correct_count 1
          + INCR_VAR total_count 1
          AS train_track_correct

RULE IF own_prog=trainer AND tick%32=15 AND var_classification!=var_target
     THEN HOLD + INCR_VAR total_count 1
          AS train_track_wrong

# Compute running accuracy
RULE IF own_prog=trainer AND tick%32=21 AND var_total_count>0
     THEN HOLD + SET_VAR accuracy (var_correct_count * 100 / var_total_count)
          AS train_compute_accuracy

# ── Default ───────────────────────────────────────────────────────
DEFAULT HOLD
