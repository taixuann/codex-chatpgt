# IV analysis contract

| Output | Numerical definition | Axis/label |
|---|---|---|
| Linear IV | pointwise mean of signed current | `Current I (µA)`; linear y-axis |
| Semi-log IV | `ln(abs(current_A))` after A conversion | `ln |I| (A)`; linear y-axis |
| Arrhenius | fit `ln(abs(I_A))` vs `1000/T` | `ln |I| (A)` vs `1000/T (K⁻¹)` |

## Pointwise averaging

For same-protocol cycle arrays `(V_k, I_k)` of equal length, calculate:

```text
V_mean[j] = mean_k V_k[j]
I_mean[j] = mean_k I_k[j]
SD[j]     = sample_sd_k I_k[j]
```

Reject or separately report unequal-length/protocol traces. Do not align them by array index and do not interpolate them unless the user explicitly authorizes protocol harmonization.

## Required provenance fields

Record raw root, parser version/path, temperature, device, cycle IDs, trace count, kept/excluded cycle IDs, exclusion reasons, voltage range, compliance flags, current unit, branch definition, and output filename.

## Common failure modes

- Taking `log` after converting A to µA shifts every value by `ln(1e6)`.
- A log-scaled axis is not the same as plotting `ln|I|`; use a linear y-axis for transformed `ln|I|`.
- Averaging heterogeneous trace lengths creates artificial shapes.
- Pooling cycles across devices gives devices with more cycles excessive weight.
- Selecting cycles by their resulting Arrhenius `R²` is circular.
