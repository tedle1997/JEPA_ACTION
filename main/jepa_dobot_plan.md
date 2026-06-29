# JEPA × DOBOT Integration Plan

> Conversation summary — picked up later for implementation.

## Context

- **Project**: Action-conditioned JEPA world models for robotic manipulation (CV course, 3-person team). Trained on Robomimic (Lift, Can, Square) using frozen DINOv2 ViT-S/14 embeddings. Pipeline lives entirely in embedding space — no simulator required for core eval.
- **Physical system**: DOBOT arm with suction gripper + Kinect camera. Already performing scripted pick-and-place: YOLO detects box on conveyor → REST API sends location to DOBOT → DOBOT executes Lua motion primitive → places box at assembly station.
- **Goal**: Combine the JEPA pipeline with the real robot to produce a genuine autonomous-manipulation result and validate the "no live simulator" claim in the real world.

## Key architectural insight

DINOv2 is a generic RGB encoder — robot-agnostic. The JEPA pipeline (predictor, subgoal extraction, CEM, BC head, all eval metrics) operates in DINOv2 embedding space, so the *embedding-side machinery* transfers zero-shot to real Kinect frames. Only the **action-conditioned parts** (predictor's Action MLP, BC head) need retraining because the DOBOT action vector differs in dimension and semantics from Robomimic's 7-DoF joint velocities.

## What transfers vs. what needs retraining

| Pipeline component | DOBOT usable? | Why |
|---|---|---|
| DINOv2 encoder | Yes, zero-shot | Image → 384-D, robot-agnostic |
| Predictor target side (ẑ ∈ R³⁸⁸) | Yes, same space | All predictors output into the same DINOv2 manifold |
| Predictor action input (Action MLP) | Retrain (cheap) | DOBOT action dim differs; ~10K params |
| Subgoal extractor | Yes, as-is | Suction on/off is an even cleaner gripper-transition signal than `gripper_qpos` |
| CEM planner | Yes, as-is | Operates purely in embedding space |
| BC policy head | Retrain on DOBOT actions | Maps z→a, action space baked in |
| Eval metrics (cos_sim, MRR, Success@K, drift) | Yes, as-is | Computed in embedding space |

Roughly **~80% of the pipeline transfers directly**; the predictor's Action MLP and the BC head need a small retrain on DOBOT data.

## DOBOT control architecture (as currently built)

```
YOLO (Kinect RGB) → object location → REST API → DOBOT executes Lua motion primitive
```

This is **high-level, event-driven** control — one command per phase ({target_xyz, suction}), not dense 10 Hz joint velocities like Robomimic.

### Consequences

1. **Action vector semantics change.** It's `{target_x, target_y, target_z, suction}` issued once per phase, not `a_t ∈ R⁷` every 100 ms. Action MLP input dim becomes ~4–5.
2. **"K-step" prediction becomes cross-phase prediction.** One Lua primitive = ~1–3 s. K-step on DOBOT maps more naturally onto the **subgoal predictor** (Module B) than onto the fine-grained Module A predictor.
3. **Natural integration is hierarchical, not flat.** JEPA/CEM sits *above* the Lua layer:
   - DINOv2(Kinect RGB) → `z_t`
   - Subgoal predictor → `ẑ_sg` (next phase embedding, e.g. "box at assembly station")
   - CEM outputs a **high-level command** `{target, suction}` minimizing embedding distance to `ẑ_sg`
   - Send that one command via REST → Lua executes → Kinect re-observes → loop
   - Lua = low-level executor; JEPA/CEM = high-level planner. Matches Module B's decomposition.

## What the pipeline can make the DOBOT do

Full closed-loop autonomous pick-and-place of a **known box type** to a **known station**, driven by either BC or hierarchical CEM, using Kinect frames through frozen DINOv2. Single-task, constrained policy — not a general manipulator.

### Ranked by risk

| Tier | Behavior | Realistic success |
|---|---|---|
| A — Constrained autonomous pick-and-place (BC, closed-loop) | One box type, belt → fixed station. BC trained on ~30–50 real demos + JEPA-augmented synthetic. | Plausible 50–80% |
| B — Same task with hierarchical CEM instead of BC | Subgoal predict → short-horizon CEM → execute → re-perceive. More novel, higher risk. | Uncertain — publishable either way |
| C — Open-loop plan execution | CEM plans full trajectory offline, verify in embedding space, replay once. | High success, but barely "autonomous" |

### What it will NOT do

- Generalize to new objects / poses / placement targets without retraining.
- Guarantee success — CEM and BC are both probabilistic/regressive.
- Run zero-shot from Lift-trained weights — action-input parts must be retrained on DOBOT demos.

### Real-robot failure modes (don't exist in sim eval)

1. **CEM may sample physically-infeasible actions** — embedding distance ignores joint limits, collisions, suction timing. Need workspace bounds + proximity gate before suction commands.
2. **Off-distribution predictor inputs** — CEM samples broadly but predictor trained only on demo actions. Constrain CEM samples to demo-action distribution.

## Data collection — what to log

### Per decision point (primary training data)

At each REST command issuance:

```
frame_t       : Kinect RGB at command issue moment (84×84 after crop/downsize to match sim)
command_t     : REST payload sent to DOBOT {target_xyz, suction}   ← this is a_t
suction_t     : 0/1
q_t           : DOBOT joint pose polled via REST at same instant   ← for reconstruction
done_t        : 0/1
```

### In parallel (background, fallback / inspection)

10 Hz continuous Kinect RGB stream → separate HDF5 group, in case denser triplets are wanted later.

### Output format

HDF5 per episode (via `h5py`), schema matching Robomimic conventions (`obs/agentview_image`, `obs/robot0_joint_pos`, `actions`, `donelast`). Drops straight into the existing `data/embeddings/` + triplet pipeline.

### Quantity targets

- **Minimum viable (predictor retrains, BC barely works):** ~20 demos, ~800 frames.
- **Comfortable (Module C α-sweep meaningful on real data):** ~50 demos, ~2000 frames.
- **Subgoal figure:** just 3–5 clean episodes with visible reach→suction→lift→place phases.

Each pick-and-place ~30–60 s at 10 Hz → ~300–600 frames per demo. Sparse decision-point logging yields ~5–10 tuples per episode, so target **~80–100 episodes** to land in the same triplet-count regime as Robomimic training. Half a day of automated collection if conveyor is auto-fed.

### Derived data (no new collection)

| Component | Derived from |
|---|---|
| Predictor (Action MLP + fine-tune) | Triplets `(I_t, a_t, I_{t+k})` for k∈{1,5,10}; DINOv2-embed offline → cache `.pt` |
| BC head | Pairs `(I_t, a_t)` from demos |
| Subgoal extractor | Episode-level `suction_t` transitions + ‖a_t‖ peaks (existing `extract_subgoals()`) |
| Subgoal predictor | Subgoal embeddings from extracted subgoals |
| JEPA-augmented BC | Uses retrained predictor to roll out synthetic `(z', a)` pairs — no new real data |

## Logging architecture (passive tap on existing pipeline)

```
[Kinect stream] ──┬──> YOLO (existing) ──> REST ──> DOBOT/Lua
                  │
                  └──> Logger (new, passive)
                          ├── grabs RGB frame on each REST send event
                          ├── polls DOBOT joint state via REST status endpoint
                          ├── writes one row to HDF5 (h5py) per decision point
                          └── also writes 10 Hz background frames to a separate group
```

Logger is a **passive tap on the REST channel** — does not alter existing pick-and-place behavior. Collect training data with zero changes to the working YOLO→Lua pipeline; train offline; later swap in JEPA planner as an alternative to the YOLO→REST path.

## Recommended recording tools

- **`h5py`** — canonical Python HDF5 library; Robomimic datasets use it, so byte-compatible output.
- **`hdf5plugin`** — compression (BLOSC/ZFP) for RGB frames.
- **LeRobot `record`** — HuggingFace robotics framework the project already uses for Parquet side; built-in teleop-and-record loop streaming camera + motor + action into LeRobot v2.1 format. Best fit *if* DOBOT SDK integrates cleanly.
- **Rerun.io** — live visualization/logging overlay (Kinect RGB + joints + suction + action in sync) for verifying demo cleanliness during collection. Saves `.rrd`; export to HDF5 after.
- **Foxglove Studio** — WebSocket GUI alternative.

**Recommended two-layer:** collect with `h5py` (or LeRobot `record` if DOBOT Python integration is clean); inspect/debug with Rerun overlaid on the same stream.

## Highest-value addition to the paper (proposed Goal G9)

Add **G9 — Real-robot transfer validation**:

1. Script/teleop ~30–50 DOBOT pick-and-place demos. Log Kinect RGB (84×84) + DOBOT joint pos + suction state at ~10 Hz.
2. Pre-compute DINOv2 embeddings → cache as `.pt`, same format as `data/embeddings/`.
3. **Zero-shot transfer**: run the Lift predictor on DOBOT triplets, report cos_sim + drift curve next to Lift/Can/Square curves. One new column in the D3 transfer heatmap.
4. **Subgoal figure**: one real episode with detected subgoals overlaid on Kinect frames — high-impact figure grounding the phase-structure claim in the real world.
5. **(Stretch)** JEPA-augmented BC on small real dataset with α sweep.

~1–2 days of work; turns "no live simulator" from a claim into a demonstration.

## Honest constraints to flag in the paper

- **Action-space mismatch**: Robomimic 7-DoF joint vel vs DOBOT ~4-DoF + binary suction. Action MLP must retrain; predictor cannot be used zero-shot across action spaces — only encoder + prediction target transfer zero-shot.
- **Visual domain gap**: 84×84 sim renders vs real Kinect RGB. DINOv2 is fairly domain-robust, but expect lower cos_sim on DOBOT than on Can/Square. That's a *result* — it quantifies the sim-to-real gap *in embedding space*, which is itself novel.
- **Control frequency**: Robomimic 20 Hz (subsampled to 10). Kinect capture + DINOv2 inference + DOBOT command dispatch slower; subsample to ~5 Hz and pick K accordingly. No algorithm change needed.
- **Safety for closed-loop**: workspace bounds + gate suction activation on proximity to detected box. Don't let CEM sample outside DOBOT's reachable envelope.

## Open questions to resolve before implementation

1. **Does the DOBOT REST API expose a "query current joint pose / status" endpoint?** Decides whether `q_t` is free or inferred from commanded targets alone.
2. **Is the Lua side one parameterized script (target_xyz → full pick-and-place) or several primitives (go-to, grasp, lift, place) that the REST caller sequences?** Decides whether a "decision point" is once per episode or several times per episode — directly changes training tuples per demo.
3. **Can the REST endpoint accept a new target *while* a previous Lua motion is still executing** (close the loop at high level), or must each Lua primitive finish before the next command is accepted? Decides whether closed-loop CEM is feasible or limited to one-command-per-phase open-loop planning.
4. **Where does the Kinect stream currently live** — same PC as YOLO, or a separate node? Determines whether logger taps frame buffer in-process or subscribes over a socket.
5. **Roughly how many pick-and-place cycles can be run unattended** (conveyor auto-fed or manual placement)? Sets whether 80–100 episodes is a half-day or a week.
6. **Which DOBOT model**, and how many DoF does the action vector end up being (joints only, or joints + suction as an extra dim)?
7. **Can ~50 demos realistically be collected**, or is 20 the ceiling? Determines whether BC is a real experiment or a stretch goal, and whether to plan the real-robot arm around CEM-only.

## What to avoid

- Don't make the DOBOT a *replacement* for Robomimic or retrain the predictor from scratch on real data — not enough real data, and would lose the sim benchmarking story.
- Don't feed raw 1080p Kinect frames into DINOv2 — embedding manifold will shift. Downsize to 84×84 to match sim training distribution.
- Don't attempt closed-loop CEM without workspace bounds + proximity gating on suction.

Treat the DOBOT as a **fifth transfer target and real-world validation column**, reusing the embedding-space machinery already built. Story: *"train in sim, evaluate zero-shot on a real robot through a shared frozen encoder, show the JEPA predictor + phase-based subgoals generalize to real manipulation."*
