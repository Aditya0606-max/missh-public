# PHI_PROTOCOL.md — committed before any phi is estimated

## Who
- Calibration split only: missh.split_reg1, split = 'calibration' (4c8012d)
- First analysable ICU stay per patient only
- Stable: no vasopressor, no invasive ventilation, alive at discharge

## Which hours
- Treatment-free stretches only
- At least 8 consecutive hourly readings per channel
- No carry-forward of missing readings

## How
- Per channel (HR, MAP, RR, SpO2), per stretch:
  remove linear trend, then lag-1 autocorrelation of residuals

## Report
- 10th, median, 90th percentile per channel
- Spread between patients (tight = one ruler rule; wide = per-patient)
- Results split by stretch length (8h, 12h, 16h+)

## Known pulls on phi
- Hidden deterioration pushes phi up; stable-only selection limits it
- Short stretches and detrending push phi down; stretch-length split shows it

## Not looked at in this pass
- No displacement, D_pre-NEWS, coupling, or any escalation-linked measure
- No test-split patient
