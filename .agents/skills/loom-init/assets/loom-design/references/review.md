# Review the actual application

Record a short receipt under `docs/generation/receipts/`: target alias, source and
catalog revisions, role, synthetic scenario, viewport, screenshot references,
observed result, severity, correction and remaining gaps. Do not capture secrets or
real customer data. Screenshots show appearance; interaction checks show behavior.

For each representative role journey:

1. Can a user identify where to begin, the current record and the next action from
   the initial view? Does navigation reflect their work and permissions?
2. Complete the task by keyboard and pointer, including save, reload and return.
   Check focus, labels, validation, persistence and duplicate-action handling.
3. Inspect with realistic long names, varied amounts, missing optional values and
   enough synthetic rows to exercise density/pagination. Check loading, empty,
   filtered-empty, failed-save and denied-action states when safely reproducible.
4. Inspect desktop and narrow widths; include zoom/reflow. Look for clipping,
   competing primary actions, unreadable contrast, hidden errors, excess whitespace,
   noisy borders/cards and inconsistent spacing/type/status treatment.
5. Compare against `generation/design.md`, not personal taste. Record deviations
   and whether they come from implementation, a native limit or a deliberate decision.

Fix order: blocked or unsafe task → confusing journey/state → accessibility barrier
→ inconsistent hierarchy/density → cosmetic detail. Capture a fresh view and repeat
the affected interaction after a fix. Do not reapply whole UI batches blindly.

Acceptance means the sampled tasks work, their states are clear, agreed visual
patterns are consistent and evidence exists. List unsampled pages/roles and known
limits. A peer should review the representative journey before its pattern is reused
widely; automated checks alone do not establish intuitive or beautiful design.
