# Q1 viability re-check, 19 September 2026 (literature verified, not assumed)

Method: targeted searches on SFDA + bearing-wise evaluation, leakage benchmarks, shallow-vs-deep under leakage-free protocols,
and MSSP appetite for evaluation papers. Every claim below was read from the source page, not inferred.

## 1. Is the headline still unoccupied?

| Work | What it does | Overlap with us | Delta |
|---|---|---|---|
| Vieira et al., **MSSP 258:114640 (2026)** — verified published, DOI 10.1016/j.ymssp.2026.114640; CWRU, PU, UORED, **HUST** | supervised bearing-wise partitioning, multi-label reformulation, 100 evaluation splits | our splitting principle | supervised only; domain adaptation and source-free explicitly out of scope |
| Knap, Jachymczyk & Lalik, **PHM Europe 9(1):1–8 (2026)**, code github.com/1Sensor/pdm-bench | leakage-safe cross-domain benchmark, CWRU + PU, six source–target scenarios, ML and DL baselines | leakage framing, cross-domain | **recording-level** separation only (same physical bearing may appear on both sides); no source-free methods; no mechanism analysis |
| Wheat et al., IEEE Access (2024), doi 10.1109/ACCESS.2024.3497716 | run-to-run / day-to-day / **part-to-part** splits, PCA/SPCA/LDA + envelope features | bearing-level (part-to-part) leakage | no adaptation, no SFDA, no pseudo-label analysis |
| Song & Ren, *Machines* (submitted), repo SFDA-Collapse-Detection | audit of SHOT/TENT/NRC/SAR + collapse detector under industrial **noise**, ~960 runs | "SFDA collapses" wording | collapse from noise, not from bearing overlap; no bearing-disjoint protocol stated |

**Conclusion: the specific contribution is still unoccupied** — no published work evaluates source-free adaptation with
bearing-disjoint targets, measures the memorisation mechanism, or bounds what pseudo-label filtering can recover.

## 2. Risks found, and the decisions taken

1. **Same-journal proximity (Vieira, MSSP 2026).** A reviewer may read us as "Vieira for SFDA". *Decision:* lead with what is
   SFDA-specific and absent there — adaptation refines the source model's own decisions, so identity memorisation is
   self-reinforcing; plus the oracle decomposition and the gating ceiling. Keep Vieira as the adopted methodology, cited as such.
2. **Leakage framing is becoming crowded (two 2026 papers).** *Decision:* cite both in related work with an explicit delta
   sentence each (done, this commit). Recording-level ≠ bearing-disjoint is the key distinction and is now stated.
3. **Shallow-baseline result is the strongest card.** No published work reports a non-adaptive shallow model beating a published
   SFDA method under bearing-disjoint evaluation. *Decision:* promote C91/C92 from "flag" to a results subsection and a highlight
   once all 10 splits are in.
4. **Venue.** MSSP publishes exactly this genre (Vieira 2026; Hendriks 2022). *Decision:* MSSP stays primary. No change.

## 3. Verdict

Q1-viable at MSSP, on the strength of: a leakage-controlled SFDA evaluation (2 folds + 10 pre-registered random splits), a
measured mechanism (within-class bearing identity decodable 507/508), a decomposition that bounds any pseudo-label filter, safety
data for physics gates on 480 real healthy recordings, and a non-adaptive baseline that matches or beats the adapted method.
Weakest points remain single-rig scope and one primary SFDA method with SHOT as the second.
