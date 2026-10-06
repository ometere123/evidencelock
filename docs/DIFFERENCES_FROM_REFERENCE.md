# Focused improvements over the reviewed reference design

The project was intentionally not redesigned into another use case. The useful lifecycle remains recognizable: structured claim → public evidence → neutral consensus → deterministic verdict → auditable state → optional bounty settlement.

The changes are limited to the review ceilings:

1. **Authority is no longer caller-supplied.** Publisher role is a consensus output of source capture.
2. **Evidence is immutable before judgment.** A later adjudication sees stored bytes, not a newly fetched page.
3. **Claim framing is narrower.** The protocol renders the adjudication statement and owns thresholds.
4. **Audit surface is split.** Web capture and economic settlement are separate ICs.
5. **UI routes reflect the two-stage model.** Capture and claim adjudication are visibly separate actions rather than one page pretending a URL is already evidence.
