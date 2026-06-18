# Reading Checklist — JEPA World Models for Robotic Manipulation

Tick papers as you finish reading. Each paper has a **focus prompt** to guide you toward what matters for your project.

---

## Stream A: THE ENCODER — Understanding `z_t`

> **Goal:** Know why DINOv2 works, what the CLS token captures, and how to evaluate frozen encoders.

- [ ] **A1 — DINOv2** (Oquab et al., 2023)
  > Focus: What does the CLS token represent? ViT-S/14 vs ViT-B/14 tradeoff. Why is it "frozen" in downstream tasks?
  *arXiv: 2304.07193*

- [ ] **A2 — MAE** (He et al., CVPR 2022)
  > Focus: Why pixel reconstruction works for pretraining but is expensive for world models. Contrast with JEPA.
  *arXiv: 2111.06377*

- [ ] **A3 — Robomimic** (Mandlekar et al., CoRL 2021)
  > Focus: Task definitions (Lift, Can, Square). Proficient-Human data characteristics. BC baseline methodology. What metrics matter?
  *arXiv: 2108.03298*

---

## Stream B: THE PREDICTOR — Building `f_θ(z_t, a_t) → ẑ_{t+k}`

> **Goal:** Implement a latent dynamics predictor with REPA alignment. This is your core contribution.

- [ ] **B1 — I-JEPA** (Assran et al., ICCV 2023) ⭐ *START HERE*
  > Focus: Context→target prediction paradigm. Why predict in representation space? EMA target encoder trick. Loss design.
  *arXiv: 2301.08243*

- [ ] **B2 — V-JEPA** (Bardes et al., 2024)
  > Focus: Temporal extension of JEPA. How does masking change for video? Motion vs appearance features.
  *arXiv: 2404.08471*

- [ ] **B3 — MC-JEPA** (Bardes et al., 2023)
  > Focus: Separating motion and content features. Why this matters for action-conditioned prediction.
  *arXiv: 2307.12698*

- [ ] **B4 — DINO-WM** (Zhou et al., 2024) ⭐ *YOUR TEMPLATE*
  > Focus: Architecture for action-conditioned world model on frozen DINO. CEM planning loop. How do they handle multi-step rollouts?
  *arXiv: 2411.04983*

- [ ] **B5 — JEPA-WMs** (Terver et al., 2025)
  > Focus: Systematic ablation of JEPA world model design choices. Which hyperparams matter most? Encoder choice, horizon, planning budget.
  *arXiv: 2512.24497*

- [ ] **B6 — REPA** (Yu et al., ICLR 2025) ⭐ *YOUR G8*
  > Focus: How does intermediate layer alignment work? Projection head design. How much speedup? Adapting from diffusion to dynamics.
  *arXiv: 2310.06940*

---

## Stream C: HIERARCHICAL PLANNING — Subgoal-conditioned CEM

> **Goal:** Understand existing hierarchical approaches and identify the gap your demo-guided subgoals fill.

- [ ] **C1 — V-JEPA 2** (Assran et al., 2025)
  > Focus: How is action-conditioning added to V-JEPA? Planning loop design. What tasks do they evaluate on?
  *arXiv: 2506.09985*

- [ ] **C2 — FF-JEPA** (Masip et al., 2026) ⭐ *DIRECT COMPETITOR*
  > Focus: Latent subgoal planner (action-free). What is their subgoal generation strategy? Why doesn't it use demo structure? What benchmark (Push-T only)?
  *arXiv: 2606.09311*

- [ ] **C3 — Zhang et al. Hierarchical** (Zhang et al., 2026) ⭐ *DIRECT COMPETITOR*
  > Focus: Multi-temporal-scale approach. How do they decompose horizons? What do they evaluate on vs. what you evaluate on?
  *arXiv: 2604.03208*

- [ ] **C4 — PiJEPA** (Chahe et al., 2026)
  > Focus: Policy-guided world model. Language-conditioned variant. Optional but inspirational.
  *arXiv: 2603.25981*

---

## Stream D: BEHAVIOR CLONING — Frozen-Encoder BC + Augmentation

> **Goal:** Establish BC baselines and understand how your JEPA-augmented BC compares.

- [ ] **D1 — R3M** (Nair et al., CoRL 2022)
  > Focus: Frozen visual representations for BC. How to train policies on frozen features. What tasks?
  *arXiv: 2203.12601*

- [ ] **D2 — MVP** (Xiao et al., CoRL 2022)
  > Focus: Multimodal pretraining (language + vision). How does it compare to vision-only? Context for BC approaches.
  *arXiv: 2203.06173*

- [ ] **D3 — VC-1** (Majumdar et al., 2023) ⭐ *YOUR BASELINE*
  > Focus: Where does frozen DINOv2 BC rank on Robomimic? What are the exact numbers for Lift, Can, Square? This is your comparison point.
  *arXiv: 2311.12118*

---

## Stream E: COMPETING PARADIGMS — Why JEPA?

> **Goal:** Position your work against Dreamer/TD-MPC. Understand the offline vs online distinction.

- [ ] **E1 — Dreamer** (Hafner et al., 2019)
  > Focus: Latent imagination for control. World model with reconstruction loss. Why does it need online interaction?
  *arXiv: 1912.01603*

- [ ] **E2 — TD-MPC** (Hansen et al., ICML 2022)
  > Focus: Temporal difference + model predictive control. Latent planning with value learning. Simulator requirement.
  *arXiv: 2203.04955*

---

## Summary

| Stream | Papers | Core for your project |
|--------|--------|----------------------|
| A | 3 | Know your encoder and benchmark |
| B | 6 | **Your predictor (G1, G2, G8)** |
| C | 4 | **Your hierarchical planner (G3, G4)** |
| D | 3 | **Your BC baseline and augmentation (G5, G7)** |
| E | 2 | Position your work |
| **Total** | **18** | |

---

### Reading Order by Project Week

**Week 1 (Foundation):** `B1 → A1 → B4 → B2 → B3 → A3`
> Build the predictor. Understand JEPA and DINOv2 inside-out.

**Week 2 (Hierarchical + BC):** `C2 → C3 → C1 → C4 → D3 → D1 → D2`
> Design subgoal extraction and BC augmentation. Know your competitors.

**Week 3 (Write-up):** `B5 → B6 → E1 → E2 → A2`
> Fill gaps for ablation discussion, Related Work, and positioning.

---

### Quick-Start: 5 Papers to Read Tonight

1. **B1** I-JEPA — Understand the paradigm
2. **A1** DINOv2 — Understand your encoder
3. **B4** DINO-WM — Your architecture template
4. **C2** FF-JEPA — Your closest competitor
5. **B6** REPA — Your novel contribution (G8)
