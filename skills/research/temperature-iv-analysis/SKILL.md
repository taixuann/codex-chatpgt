---
name: temperature-iv-analysis
description: Reproducible temperature-dependent I-V analysis from raw sweep files, including protocol-safe pointwise cycle averaging, device and temperature ensembles, mandatory linear and ln|I(A)| plots, cycle QC, branch handling, and Arrhenius fits. Use when analyzing, plotting, QCing, or extracting activation energy from temperature-dependent memristor I-V data.
---

# Temperature-dependent IV analysis

Use this skill whenever a task involves temperature-dependent I-V sweeps, `_proc` selections, cycle/device error bars, linear or semi-log overlays, or Arrhenius activation energy.

## Non-negotiable data contract

1. Treat `data/raw/<date>/` as the source of truth. Never use PNG pixels as numerical input. Record the exact raw root and source file count before plotting.
2. Parse every filename into `(temperature_K, device_id, cycle_id)`. A blank temperature label means 300 K only when the project parser declares that rule.
3. Inspect trace lengths, voltage grids, voltage spans, parser failures, and compliance behavior before averaging. Do not silently mix protocols.
4. Pointwise cycle averaging means averaging point `j` with point `j` across cycles of the same device/temperature/protocol. Preserve the voltage vector by averaging pointwise too. Do not interpolate heterogeneous protocols into a common grid unless the user explicitly requests interpolation.
5. Average cycles within each device first, then average device curves within a temperature. Keep cycle SD and between-device SD separate. Never let a device with more cycles receive more temperature-level weight.
6. Keep user-selected `_proc` choices as metadata, not as permission to optimize for a higher R².

## Mandatory figure pair

For every IV overlay, produce or clearly identify both:

- Linear: signed current `I` in µA versus voltage, with `I` label.
- Semi-log: compute `ln(abs(I_A))` after converting current to amperes; plot the transformed values on a **linear y-axis**. Label it `ln |I| (A)`. Do not call a log-scaled y-axis `ln I`.

For sampled positive-voltage figures, use explicit points such as `0.0, 0.1, ..., 1.0 V` when requested. Use solid lines; distinguish forward/backward with markers or panel separation, not arbitrary dashed lines. State whether each marker is forward or backward.

## Branch and Arrhenius rules

- Define forward as the acquisition path from the starting voltage to the positive maximum and backward as the return path from that maximum.
- For Arrhenius, fit `ln(abs(I_A))` versus `1000/T (K^-1)`. Never fit µA values when reporting an activation energy in the same analysis.
- Report `E_a`, standard error, `R²`, number of temperatures, voltage points, and excluded/compliance points for every voltage.
- Do not choose cycles or voltage regions because they maximize `R²`. First apply independent QC (structure, span, missing values, robust within-device deviations, compliance plateau); then fit and report sensitivity.
- Keep 300 K included or excluded only as an explicit analysis choice. Show how that choice changes fit quality; do not hide it.

## Validation checklist

Before presenting a figure, verify:

- raw root and parsed count are printed;
- selected device/cycle mapping matches the user's current `_proc` names;
- no accidental index averaging across different trace lengths or voltage protocols;
- linear and `ln|I(A)|` units are correct;
- x-axis range and step match the request;
- legend identifies temperature and sweep branch;
- output image was visually inspected;
- tables preserve provenance, QC status, and fit statistics.

See `references/iv-analysis-contract.md` for the compact audit table and failure examples.
