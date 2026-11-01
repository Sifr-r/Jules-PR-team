# User-facing web performance

**Intent:** Connect the requested browser experience to a measurable loading, interaction or layout-stability problem. Activate for a demonstrated slow flow, requested performance budget, or a rendering/asset change with plausible user impact.

**Questions, top down:** Which user action and page state matter? Is the delay before useful content, during input handling, or caused by moving content? Which resource, render task, server response or asset lies on that path? What device/network/cache conditions represent the task? Does existing evidence come from real visits, a controlled local trace or a simulation?

**Evidence:** Use LCP for major content loading, INP for interaction responsiveness and CLS for unexpected layout movement where relevant to the actual flow. Record browser/tool, viewport, CPU/network conditions, warm/cold cache, build mode, sample count and candidate. Field measurements reflect real usage; lab traces reproduce selected conditions and cannot certify the field distribution. A Lighthouse navigation run does not measure INP: its Total Blocking Time may be a diagnostic proxy, never proof of real interaction latency. Prefer existing project metrics/budgets; do not impose universal thresholds or add telemetry automatically.

**Bounded action and proof:** Profile before changing code. Within owned paths, address the evidenced critical resource, unnecessary work or unstable geometry while preserving functional behavior, accessible interaction and truthful loading feedback. Compare the same workload and conditions before/after; distinguish reduced bytes/work from measured timing. Use existing browser tools and recorded field data without initiating live-service calls or installing dependencies by default.

**Stop/handoff:** Stop when the requested experience has comparable evidence and known limitations. Send visual/focus consequences to Palette, blocking logic to Scalpel and behavioral regression checks to Harness. Missing field data limits the claim rather than blocking an otherwise local implementation.
