# Smart Reading List — JEPA World Models for Robotic Manipulation

Papers are organized by **project phase**, not publication date. Each stream feeds a specific implementation goal from your proposal.

---

## Stream A: THE ENCODER (G1 prerequisite)
> *What produces your `z_t ∈ R³⁸⁴` and why should you trust it?*

### Essential
| # | Paper | Key question answered | Read for |
|---|-------|----------------------|----------|
| A1 | **DINOv2** (Oquab et al., 2023) | Why frozen DINOv2 features work as a visual backbone | Understanding CLS token semantics, ViT-S vs B tradeoffs |
| A2 | **MAE** (He et al., CVPR 2022) | Why masked autoencoders learn good representations | Background contrast: pixel vs latent prediction |
| A3 | **Robomimic** (Mandlekar et al., CoRL 2021) | What matters for BC on Lift/Can/Square | Task details, expert data characteristics, baseline BC numbers |

### Strategy
Read A1 first (DINOv2), skim A2 for contrast, keep A3 open as reference during implementation.

---

## Stream B: THE PREDICTOR (G1, G2, G8)
> *How do you build `f_θ(z_t, a_t) → ẑ_{t+k}` and make it good?*

### Essential (read in order)
| # | Paper | Key question answered | Read for |
|---|-------|----------------------|----------|
| B1 | **I-JEPA** (Assran et al., ICCV 2023) | What is JEPA and why predict in latent space? | The core paradigm: context→target prediction, EMA target encoder, why not pixel reconstruction |
| B2 | **V-JEPA** (Bardes et al., 2024) | How does JEPA extend to video/temporal data? | Temporal masking, motion features — direct precursor to your predictor |
| B3 | **MC-JEPA** (Bardes et al., 2023) | How to separate motion from content features? | Motion-sensitive representations — useful for understanding action grounding |
| B4 | **DINO-WM** (Zhou et al., 2024) | How to build world models on frozen DINO features for zero-shot planning | **Most directly relevant**: architecture, CEM planning, your closest template |
| B5 | **JEPA-WMs** (Terver et al., 2025) | What factors drive success in JEPA world model planning? | Ablation insights: encoder choice, horizon, CEM hyperparams |
| B6 | **REPA** (Yu et al., ICLR 2025) | How does intermediate alignment with frozen encoder features help training? | Your G8: adapting REPA from diffusion to dynamics predictors |

### Strategy
B1→B2→B3 establish JEPA fundamentals. B4 is your main architecture template — read it carefully. B5 tells you what to ablate. B6 is for your REPA contribution (G8).

---

## Stream C: HIERARCHICAL PLANNING & SUBGOALS (G3, G4)
> *How to decompose long-horizon planning into subgoal-conditioned short-horizon problems?*

### Essential (read in order)
| # | Paper | Key question answered | Read for |
|---|-------|----------------------|----------|
| C1 | **V-JEPA 2** (Assran et al., 2025) | How to add action-conditioning to JEPA for planning? | Action-conditioned architecture, planning loop design |
| C2 | **FF-JEPA** (Masip et al., 2026) | How to do hierarchical JEPA with a latent planner? | Action-free latent subgoal planning, what they do wrong (no demo structure) |
| C3 | **Zhang et al. Hierarchical** (Zhang et al., 2026) | How to do multi-temporal-scale hierarchical planning? | Multi-scale approach, what they evaluate on (not Robomimic) |
| C4 | **PiJEPA** (Chahe et al., 2026) | How to combine policy guidance with JEPA planning? | Policy-guided world model, language-conditioned variant |

### Strategy
C1 gives you action-conditioning baseline. C2 and C3 are your direct competitors — understand their approaches and identify gaps your demo-guided subgoals fill. C4 is optional inspiration.

---

## Stream D: BEHAVIOR CLONING & AUGMENTATION (G5, G7)
> *How to train BC from frozen embeddings and augment with synthetic data?*

### Essential
| # | Paper | Key question answered | Read for |
|---|-------|----------------------|----------|
| D1 | **R3M** (Nair et al., CoRL 2022) | Can frozen visual representations enable BC for manipulation? | Frozen-encoder BC paradigm, Vikash setup |
| D2 | **MVP** (Xiao et al., CoRL 2022) | Does multimodal pretraining help robot manipulation? | Multimodal pretraining comparison |
| D3 | **VC-1** (Majumdar et al., 2023) | Where do different visual representations rank on embodied tasks? | Your external baseline: frozen DINOv2 BC numbers on Robomimic |

### Strategy
D3 is your primary benchmark reference — find the DINOv2 BC numbers. D1 gives the paradigm. D2 is context. Read D3 first, then D1.

---

## Stream E: COMPETING PARADIGMS (G7 context)
> *What alternative approaches exist, and why is JEPA better for your setup?*

### Essential
| # | Paper | Key question answered | Read for |
|---|-------|----------------------|----------|
| E1 | **Dreamer** (Hafner et al., 2019) | How to learn behaviors by latent imagination? | World model learning with reconstruction — contrast with JEPA |
| E2 | **TD-MPC** (Hansen et al., ICML 2022) | How to combine TD learning with MPC in latent space? | Alternative planning approach, requires live simulator |

### Strategy
Skim E1 and E2 for Related Work. The key difference: Dreamer/TD-MPC need online interaction; you evaluate offline.

---

## How to Use This List

### If you have 2 weeks: Priority order
```
B1 → A1 → B4 → C1 → C2 → B6 → D3 → A3 → B5 → C3 → D1 → B2 → B3 → E1 → E2 → D2 → C4 → A2
```

### If you have 1 week: Minimum viable reading
```
A1(DINOv2) → B1(I-JEPA) → B4(DINO-WM) → C1(V-JEPA2) → B6(REPA) → D3(VC-1)
```

### If you're implementing today: Open on the side
- `B4` DINO-WM (architecture template)
- `A3` Robomimic (task reference)
- `B6` REPA (alignment implementation)
- `C2` FF-JEPA (hierarchical competitor)

---

## Paper Map

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR PROJECT                              │
│  Demo-Guided Hierarchical JEPA + BC Augmentation            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌──────────────┐   ┌───────────────────┐   │
│  │ ENCODER  │──▶│  PREDICTOR   │──▶│   PLANNER + BC    │   │
│  │ A1, A2   │   │  B1-B6       │   │   C1-C4, D1-D3    │   │
│  └──────────┘   └──────────────┘   └───────────────────┘   │
│                        │                    │                │
│                        ▼                    ▼                │
│                 ┌──────────────┐   ┌───────────────────┐   │
│                 │  ALIGNMENT   │   │   COMPETITORS     │   │
│                 │  B6 (REPA)   │   │   E1, E2          │   │
│                 └──────────────┘   └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Key Insight per Stream

| Stream | The "aha" you need |
|--------|-------------------|
| A | DINOv2 CLS token is a 384d semantic summary — predicting it is easier than predicting pixels, and it's already a good representation |
| B | JEPA = predict representations, not pixels. Adding action conditioning turns it into a "simulator" in embedding space. REPA alignment prevents the predictor from collapsing to identity on slow-motion data |
| C | Hierarchical = break one hard K-step problem into M easy h-step problems. Demo structure gives you natural breakpoints that uniform stride misses |
| D | Frozen DINOv2 + simple MLP BC already works decently (VC-1 baseline). Your JEPA augmentation can improve it without simulator access |
| E | Dreamer/TD-MPC need online env interaction. Your approach works offline — this is the key practical advantage |
