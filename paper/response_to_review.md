# Response to reviewers

Two reports reached us. The first was a full peer-review report keyed as Concerns 1–7, Minor 1–10, a numerical audit and
questions to the authors; the second was an assessment of our reply to it. Our first reply merged the two reports' items
under our own numbering, which made it impossible to check item by item — the reviewer was right to object, and this
document replaces it. **Part A answers Reviewer 1 in that reviewer's own numbering. Part B answers the second-round
assessment.** Where a claim was checked against the artifacts and failed, the manuscript is corrected and the correction is
named. Where a claim did not hold, the evidence is given rather than an assertion.

**Part C answers the third-round report.** New analyses added in the second round are pre-registered as protocol entries C98–C101 and carry retained artifacts:
`experiments/c98_inloop_coverage.py`, `c99_crossrig_calibration.py`, `c100` (SHOT on the ten splits),
`c101_rf_splits.py`.

---

# Part A — Reviewer 1, by that report's numbering

## Concern 1 — Inconsistent headline clean accuracy and collapse (56.8 % / 37.3 pp vs 56.05 % / 38.1 pp)

**Accepted; the diagnosis was slightly different from the one proposed, and the cause is now removed.** The reviewer
inferred that 56.8 % was fold A's value used as if it were the mean. It was not. It is the mean of the two fold means,
but of the *fold job*: 58.36 % (fold A) and 55.31 % (fold B) average to 56.84 %, and 94.12 − 56.84 = 37.28 pp. The
apparent contradiction came from Table 3, which printed fold A's clean arm from the *gating* job (56.76 %) beside the
fold job's leaky arm. Those two numbers coincide to one decimal with the correct headline, which is what made the table
look like the source of the headline.

Table 3 now takes each fold's leaky and clean arms from the fold job (58.4 / 55.3) and pairs the gated and oracle arms
against the gating job's own ungated clean arm, with the provenance and the reference values in the table note. Section 6.2
states which job every headline number comes from, gives the gating job's own collapse (38.1 pp) beside the headline
(37.3 pp), and attributes the difference to the run-to-run spread quantified in Section 4. *[Corrected in round 3: that
attribution was wrong. Repeated executions are bit-identical (C102), so the difference is not run-to-run spread; see Part C.]* One collapse magnitude now
circulates; the other is shown once, labelled, next to it.

## Concern 2 — Source-free premise vs gate calibration on labelled target-rig data

**Accepted, and answered with a measurement rather than a caveat (C99).** Two things were conflated in our first reply and
are now separated in Section 6.6.

*What was never target supervision:* the threshold is applied to a within-recording robust z-score, so no target-rig
statistics are pooled into it, and z = 10 was fixed in the protocol before any gate was evaluated.

*What was:* the evidence that z = 10 is **safe** came from Paderborn's own healthy recordings. We therefore recalibrated
entirely off-rig. The identical rule was swept over z on 24 healthy recordings from two rigs that appear nowhere in the
adaptation experiments — 20 from UORED (geometry verified from the dataset paper's Table 2, speed measured in-file) and 4
CWRU baselines — each truncated to the sample count that reproduces Paderborn's spectral resolution, so that a z means the
same thing on every rig.

The result is not the reassuring one. **z = 10 is not safe off-rig: it accepts 4 of the 24 healthy recordings as faulty.**
Zero off-rig false acceptance requires z = 36 *[corrected in round 3 from 37.5, which was a row of the sweep
table, not its minimum; the Paderborn transfer is evaluated at z = 40, the nearest sweep point at or above it]*. The consequence for this paper is nevertheless mild, because the envelope
rule is flat in that region: transferring the off-rig operating point to Paderborn unchanged certifies 333 of 1,839 fault
recordings against 366 at z = 10 — 91 % of the detections — while healthy false acceptance improves from 1/480 to 0/480.
A gate calibrated with no target-rig data at all is thus slightly stricter and slightly less productive than the one we
report. We state plainly that the adaptation arms were **not** re-run at z = 40, so this is a verdict-level statement, not
a second accuracy measurement. Recommendation 6 in Section 8 now declares target-rig characterisation as mild supervision
and adds "calibrate where you deploy."

## Concern 3 — Gate population mis-described, artificial and real damage mixed

**Accepted (C95), and the correction went further than the request (C98).** The population is disclosed in full: 2,319
recordings, 29 physical bearings (6 healthy, 11 real-damage, 12 artificial-damage) at all four operating conditions. The
reviewer's arithmetic is confirmed exactly: 29 × 80 − 1 = 2,319, 11 × 80 = 880, 12 × 80 − 1 = 959, the missing file being
the known unreadable `N15_M01_F10_KA08_2.mat`.

Coverage is now reported separately by damage origin **and** separately for the population that actually enters adaptation.
Over four conditions the envelope rule engages 7 of 11 real-damage bearings. Over the three adaptation conditions it
certifies more than a single recording on only 4 of them (KA04 41/60, KA16 40/60, KI16 32/60, KI18 45/60; KA30 1/60,
the rest 0/60). Section 5.6 of the manuscript reports both, and says which one bounds the gating results.

## Concern 4 — Pseudo-replication and absent multiplicity control

**Accepted; this was the most serious item (C96).** Every headline comparison is recomputed with the split or fold as the
cluster: cluster bootstrap for the effect, exact sign-flip permutation over clusters for the p-value, Benjamini–Hochberg
across the family. Task-level values are retained in Tables 3 and 4, marked descriptive in the table notes and in
Section 4.

The consequence is carried through the whole manuscript, not only where it is favourable. With two clusters the
permutation floor is p = 0.25, so **every fold-only comparison now appears without a p-value**: the two-fold collapse, the
two-fold gate gains (previously 0.007 and 0.0007), SHOT and the random forests on the folds. The inference rests on the
split-level tests, which survive adjustment.

## Concern 5 — Figure/text numeric mismatches (KA04 purity; S04 at "100 %")

**Both accepted and fixed.** Purity now has one definition, stated once and used in the text, in Fig. 3 and in its caption.
Fig. 4's label was capped at 100 %; the cap is removed and S04 reads 222 %, matching Table 3, with the caret marker's
legend entry explaining the case. The reviewer's arithmetic ((92.1 − 74.0)/(82.2 − 74.0) = 221 %) is confirmed. On the
language: the oracle bounds a **keep-or-withhold** filter, which is what we implement, and the manuscript now says so
explicitly and notes that S04 — the split with the smallest collapse, 8.2 pp — makes the ratio unstable by construction.

## Concern 6 — Over-claim on "the strongest lever is the number of distinct source bearings"

**Accepted.** Downgraded to an attribution of Vieira et al.'s supervised finding, with the statement that our splits hold
the source pool fixed at three bearings per class and therefore cannot test it, and that a scaling study is the obvious
next experiment.

## Concern 7 — HUST gating omitted on questionable grounds

**Not accepted, and the second-round report withdrew it.** The HUST source publication tabulates bore, outside and ball
diameters and the ball count, but not the pitch diameter. The characteristic orders in circulation for those bearings
(3.093 for the 6204 outer race) follow from the estimate d_m ≈ (d_i + d_o)/2 = (20 + 47)/2 = 33.5 mm. Our project rule
forbids estimated geometry in a kinematic claim. Section 3 now states this with the error the estimate carries on the one
bearing where a first-party value exists for comparison: on Paderborn the same substitution gives 28.50 mm against a
documented 29.05 mm and shifts the outer-race order by 0.58 %.

## Minor concerns

1. **Rounding inconsistencies.** Accepted. Differences are computed before rounding; the table notes now say so.
2. **Fold-B 5/9 arithmetic.** Accepted and now exact. Windows are balanced per class, not per bearing: each class holds
   2,000 windows split 680/660/660. The correctly labelled fault bearings are 660-window ones, so the prediction is
   (2,000 + 660 + 660)/6,000 = 55.33 %, which is the measured value. The "one class right, two wrong" wording is gone and
   fold B's two-outer-bearing composition is stated.
3. **"Target-label selection worth 1.0–2.0 points" not traceable.** Accepted; it was wrong. Averaged over the 12 paired
   tasks it is 0.6 points on leaky and 1.0 on clean targets, with a per-task range of 0.0–4.1. Section 6.2 now says
   exactly that, and what the range is over.
4. **"Roughly half the variance."** Accepted. Replaced by the numbers: standard deviation 1.7 and 2.4 points for the
   difference against 2.8 for the accuracies, i.e. 0.4 and 0.7 of the variance, not a fixed fraction.
5. **508 vs an expected 510 probe recordings.** The 508 is not a count of recordings that should have been 510: it is the
   size of the held-out half of a deterministic hash split, which divides the 1,080 source recordings 508/572 rather than
   exactly in half. The manuscript states this where the probe is reported. Test recordings are excluded from the probe's
   training; they are not excluded from the *source model's* training windows, and that caveat is stated too.
6. **Probe lacks a baseline.** Accepted, and it changed the paper's mechanism claim — see Part B, §3.
7. **"Three declared adapters."** Accepted; there are two source-free adapters (SDALR and SHOT). The random forest is not
   an adapter. Corrected in the code-availability statement.
8. **Pre-registration not externally verifiable.** Partly accepted. There is no registry entry; the protocol is a
   version-controlled file, so the ordering is verifiable from commit history rather than asserted. Section 4 now says so
   and gives an instance: the ten-split draw was committed on 15 September 2026, more than a day before the first split
   artifact existed. The repository, including this history, is archived with a DOI on acceptance.
9. **Defend the terminology.** Accepted; Section 7 now has a paragraph distinguishing the two deployment scenarios and
   adopting Kapoor and Narayanan's definition of leakage and Geirhos et al.'s notion of a shortcut.
10. **Patent used for a claim about industrial practice.** Accepted. The standard tutorial treatment is now cited for the
    substantive point (random slip of 1–2 % makes characteristic frequencies inexact), and the patent is cited as one
    documented instance of the contrary view rather than as evidence for it.

## Numerical audit and references

Every audited value was recomputed. Two disagreements were real (Fig. 4's cap, and differences displayed after rounding);
both are fixed. On references: Lessmeier et al. is now `@inproceedings` with the Bilbao venue, Wheat et al.'s page range is
corrected, and Kapoor, Geirhos and Matania are added. On the SDALR author list, the second-round report withdrew its own
correction; we verified independently against the Crossref publisher record, which gives Wu, Zhang, Wei, Jing, Zhang and
Wu, in that order, with the published title "Both reliable and unreliable predictions matter…". The preprint carries a
different title and order. Our entry follows the publisher record and now records that provenance in a note.

On the Paderborn pitch diameter: the source is the per-specimen datasheet distributed with the data (`K001.pdf`, "Pitch
circle diameter mm 29.05"). Section 3 now cites it and says which bearings it covers — 29.05 mm for the 26 IBU and MTK
specimens, including all six healthy ones; 28.55 mm for the six FAG specimens, among them KA04, KA15, KI16 and KI21.

---

# Part B — second-round assessment

## 1. The response did not track the report

**Accepted without qualification.** This document is keyed to each reviewer's own numbering, and Part A answers every
Concern, Minor and Question of the first report, including the four that went unanswered. The reviewer is also right that
our first reply rebutted claims their report never made: the "single rig", "implausibly high 94 %", "pipeline bug" and
"mixing arms across jobs" items came from our own re-reading of the manuscript, not from the report, and presenting them as
responses was an error. The arm-mixing problem was real and is fixed (Concern 1 above), but it was ours to find, not the
reviewer's to be credited with.

## 2. Consequences of dropping fold-level p-values

**Accepted and carried through.** All four consequences the reviewer lists are now in the manuscript:

- The two-fold gate p-values are removed from Section 6.6 and the abstract; the abstract now quotes the ten-split median
  gain (4.5 points) instead of the fold-level "4–7 points in paired comparisons".
- The alias-guarded comb has no split-level evaluation, and Section 6.6 now says so explicitly and makes no general claim
  for it.
- **The random forests are now reported on all ten splits** (C101). The arms already existed in the C92 artifacts; only the
  clean arm had been used. Over ten splits the time-statistics forest loses a median 22.7 points and the combined feature
  set 32.1 points, each positive in 10/10 (exact sign-flip p = 0.001, p_BH = 0.001, the split being the unit). *[Corrected
in round 3: 0.001 was never a BH output for this family; the adjusted value is 0.002 at the final stage. See Part C.]*
- **SHOT is being run on the ten splits** (C100, pre-registered with a decision rule before the runs: the collapse
  generalises iff the median split Δ ≥ 10 pp and sign-flip p < 0.05, reported either way). Until those runs land, the SHOT
  result is stated as a two-fold effect size without a p-value. *[Round 3: all ten splits have landed; see Part C.]*

The BH family has been enlarged accordingly, so the adjusted values in the manuscript move: the ten-split collapse is now
p_BH = 0.003 and the gate gain p_BH = 0.006. *[Superseded: the final-stage values are 0.002 and 0.005; Supplementary S1
now tabulates every member at every stage.]*

## 3. Where the new evidence changes the argument

**Gate coverage vs the ceiling explanation — accepted, and the argument is rebuilt rather than patched (C98).** The
reviewer is right that 7 of 11 bearings does not support "it cannot act on bearings it never engages". Two answers.

First, the counting question: coverage is **per record**, because the adaptation hook vetoes a pseudo-label only on a target
record whose verdict is a fault class and leaves every other record untouched. Per bearing is the wrong unit, and 7/11 was
also the wrong population — it spans four operating conditions and the whole real-damage pool, whereas adaptation uses three
conditions and each experiment's own target set. Read as the loop sees it: the envelope rule speaks on a **median 24 % of
the faulty recordings of a clean target set** and engages a median 2 of that target's 5 faulty bearings.

Second, and more usefully, the claim is now empirical rather than rhetorical. Across the ten splits, coverage predicts the
gain almost perfectly: **Spearman ρ = 0.95, p = 2 × 10⁻⁵, the split being the unit.** The split where the gate speaks on
0.7 % of faulty recordings is the single split where gating costs accuracy (−1.5 points); the two splits above 40 %
coverage gain more than 22 points each. The sentence "the modest size of the gain is a property of the problem, not of the
tuning" has been replaced by this correlation, which says the same thing with evidence and yields a usable rule: coverage
is computable from the target recordings before any adaptation run.

**The probe result — accepted, and the reframing goes to the title.** The reviewer is right that 508/508 from ten
handcrafted statistics moves the mechanism. Changes made:

- The title's "bearing-identity memorisation" becomes "**bearing-identity shortcuts**".
- The abstract, Section 6.7 and the conclusions now say that identity is *present in the raw signals* and available to any
  source-trained classifier, rather than learned or memorised by the source representation. The conclusions add that a
  representation-level remedy would therefore not address the root cause — which weakens the motivation for the
  class-conditional adversary we had listed as future work, and we say so.
- The **session/mounting confound is named**: each bearing was recorded in its own session and mounting, so what the probe
  separates is the recording, not necessarily the specimen. For the paper's argument the distinction does not matter — a
  shortcut that follows the specimen through its own recordings is exactly what a bearing-disjoint target removes — but it
  matters for any remedy, and it is stated where the probe is reported.

**Non-determinism across jobs — accepted.** Section 4 already stated the 1.6 pp figure; Section 6.2 now adds that
cross-job comparisons are reliable only to about that level and identifies which comparison is cross-job. *[Round 3: the
word "non-determinism" was wrong; the cause is a change of random trajectory between code revisions. See Part C.]* The revised
Table 3 fold rows are: fold A 88.3 / 58.4 / 30.0 / 61.2 / +4.4 / 88.5 / 101 %, fold B 99.9 / 55.3 / 44.6 / 62.3 / +7.0 /
76.8 / 48 %. The reviewer is right that 56.8 and 55.3 appeared in the old table — as fold A's *gating-job* clean arm and
fold B's clean arm respectively. The changed value is fold A's clean arm, 56.8 → 58.4, and with it Δ_leak 31.5 → 30.0.

**Target-label range — accepted**; see Part A, Minor 3.

## 4. HUST gating withdrawn

Noted with thanks. On the observation: the reviewer is right that a 0.58 % pitch-diameter error is well inside the ±2 %
slip search window, so a HUST sensitivity run would probably work. We have not added it. The reason is not that it would
fail but that the project rule forbidding estimated geometry is what makes every other kinematic number in the paper
auditable, and a clearly-labelled exception still puts a number in the manuscript that no first-party source supports. We
record the reviewer's observation in the limitations as the route a follow-up should take.

## 5. Remaining requests

| # | Request | Where |
|---|---|---|
| 1 | Reconcile the headline numbers, state the source job | §6.2; Table 3 note; §4 |
| 2 | Acknowledge target-rig supervision, or calibrate cross-rig | §6.6 (C99), §8 item 6 — both |
| 3 | Rewrite the coverage ceiling argument | §6.6, §7 (C98) |
| 4 | Reframe the probe; name the session/mounting confound | title, abstract, §6.7, §10 |
| 5 | Remove fold-level p-values; add split-level RF and SHOT | abstract, §6.3, §6.6; C101 done, C100 done (10/10) |
| 6 | Name the damage-mechanism confound | §9, verified from the per-specimen datasheets |
| 7 | Answer the unanswered minors; key the response to each reviewer | Part A |

On request 6, we verified the mechanism composition from Paderborn's own damage profiles rather than from a secondary
table: of the five real outer-race bearings, KA04, KA16 and KA22 are "fatigue / Pitting" and KA15 and KA30 are "plastic
deformation / particle-caused"; all six real inner-race bearings are fatigue pitting. Section 9 names the confound, states
that our design cannot separate mechanism from identity, and notes that the inner-race class is mechanism-homogeneous and
collapses anyway, and that the HUST replication contains no plastic-deformation bearings. The same profiles show the
mechanism reaching the gate: of the two plastic-deformation bearings, one is never certified at the adaptation conditions
and the other once in 60 recordings. We agree a same-condition, bearing-disjoint control is the right way to isolate this
and name it as the cheapest experiment we did not run.

---

# Part C — third-round report

> **Note for the corresponding author:** the third-round report is not stored in the repository, so the items below are
> keyed by topic, reconstructed from the changes it prompted. Before sending, re-key them to the reviewer's own numbering,
> as Part A does for the first report.

## C1. What a gain means against run-to-run noise — the A/A floor (C102)

**Accepted, measured, and the answer is stronger than we expected.** Every retained re-execution of the gating
configuration was compared with the first: the original job, two repeats and the two C103 arms, eleven arm pairs over
66 paired tasks on both folds. All reproduce it to the last reported decimal, a floor of 0.00 points. The pipeline is
deterministic under a fixed seed and a fixed code path on the T4, so no reported difference is run-to-run noise. A zero
floor makes a ratio against it meaningless, so the manuscript instead sets effects against the between-seed range of the
ungated clean fold mean (3.2 points on fold A, 1.9 on fold B): the collapse exceeds it by an order of magnitude; the gate
gain is of the same order, which is why the gate claim rests on paired same-job arms and the ten-split distribution.

## C2. The cross-job gap — our own explanation was wrong (C103)

The measurement in C1 falsified what Section 4 said: a gap between two jobs running one configuration cannot come from
non-deterministic GPU reductions if repeats within a job are bit-identical. We pre-registered a test of the most likely
remaining explanation, source pretraining inside the adapting process versus loading a checkpoint, with a rule fixed
before the run. It is **rejected**: the two arms agree to 0.000 points. A code comparison then found the probable cause,
which we label as a post-hoc diagnosis because no run isolated it. The gate-hook revision of our runner wraps the evaluation
routine with one extra pass over the evaluation loader, for every arm including the ungated one. The networks are in
evaluation mode, so no weights or normalisation statistics change, but creating a data-loader iterator draws from the
global random generator; we confirmed on CPU that one extra unshuffled pass changes every later draw. The fold job
predates that revision. The 1.6-point gap is inside the between-seed range. Section 4 and Section 6.2 now say exactly this,
and the rule that arms are never crossed between jobs stands. We have also corrected, visibly, the two places in our
round-2 response that repeated the old explanation.

## C3. Is coverage a headroom effect in disguise? (C98)

**No.** Headroom (oracle minus ungated clean) does not predict the gain alone at n = 10 (ρ = 0.53, p = 0.12) and predicts
nothing once coverage is partialled out (ρ = −0.07, p = 0.85); coverage survives partialling headroom out (ρ = 0.98).
Section 6.6.

## C4. State the multiplicity family

**Accepted, and our own audit found an error the request exposed.** Section 4 now lists the members. Rebuilding the family
from its version history showed that the manuscript quoted adjusted values from different stages of the revision, and in one
place (the random forests, 0.001) a value the BH procedure never produced. Every adjusted value is now taken from the
final stage and generated into the tables from the stored family (`results/c96/c96_family.json`); the quality gate fails
the build if a quoted p_BH is not a member. Supplementary S1 tabulates every member, unadjusted and adjusted, at every
stage. No member was ever removed. The ten-split collapse and gate gain survive at every stage (largest p_BH 0.007).

## C5. SHOT on the ten splits (C100) — complete

All ten splits have landed. SHOT loses a median 21.7 points, positive in 10 of 10 (exact sign-flip p = 0.001,
p_BH = 0.002), meeting the rule fixed before the runs. The method-generality claim therefore rests on ten splits for SHOT
as well as for the random forests (Section 6.3, Table 4, conclusions, abstract).

## C6. References and primary sources

Wheat et al. page range, the patent record and ISO 15243 are added. Per-specimen Paderborn geometry is generated from the
32 first-party datasheets (Supplementary S3). HUST's blocked-on records are corrected against the primary publication.

## C7. Declarations

The use of an AI coding assistant as part of the research method is described in Section 4 and in the declaration, as
Elsevier's policy requires.

## C8. Corrections from our own final audit

- Section 3 said the 0.58 % pitch-diameter error was "roughly twice the whole cage-slip spread". It is about equal to the
  5–95 % range measured on that geometry (0.53 %) and ten times its median; corrected.
- The slip distribution in Section 6.8 was the IBU/MTK stratum stated as all of Paderborn; the FAG stratum is now given
  beside it.
- "Ten independent draws" was wrong: the splits share bearings. The text now says pre-registered draws, each treated as one
  cluster.
- A duplicated damage-mechanism paragraph in the Limitations was merged.
- The random-forest runs behind Table 4 had retained artifacts but no ledger rows; 336 rows are added, and the ten-split
  medians (22.7 and 32.1) recompute from the ledger alone.
- A superseded markdown draft of the manuscript had been included in the submission package; it is removed.
- The off-rig zero-false-acceptance threshold was quoted as z = 37.5; the calibration's own minimum is z = 36. The
  Paderborn transfer figures (333 of 1,839 against 366; healthy 0/480) are for z = 40, the nearest point at or above z = 36
  on the Paderborn sweep, and the text now says so. The C99 script had also described the off-rig point as "more
  permissive" when it is stricter; fixed, and the transfer is now written into the C99 result file itself.
- The partial correlation of gain on coverage was quoted as p = 1 × 10⁻⁶; the computed value is 1.5 × 10⁻⁶.
- "Right when it speaks in 96–100 % of cases" held on eleven of twelve target sets; on S03 the gate speaks on two
  recordings and is right on one. Stated.
- "No gate exceeds 24 % correct verdicts before 10 % false acceptance": the operating-curve data give 20.3 % (373 of
  1839); corrected in Section 6.6 and S2. The raw-spectrum rule's first correct verdicts appear at 11.5 % false
  acceptance, not 10.8 % (Fig. 5 caption).


---

# Part D — fourth-round report

Every item was checked against the primary source, the code or the data before it was acted on. Three checks came out
differently from the report, and they are marked **(verified otherwise)**. Section numbers refer to the revised manuscript;
"S1"–"S4" are the supplementary files `S1_protocol_changes.md`, `S2_gates.md`, `S3_datasets.md`, `S4_traceability.md`.

## What to do, in order

| # | Request | What we found | Change | Where |
|---|---|---|---|---|
| 1 | Add or delete the 18-paper claim; separate the 8-class reproduction | **(verified otherwise, in part.)** The 18-paper survey *is* Vieira et al.'s Table 1 (arXiv v5, §3.3). But our text said six papers reported 100 %; the table has five. It also presented the 18 as if they bore on SFDA; they are supervised, single-dataset papers. SDALR's Paderborn task (its own §4, read in the preprint) has eight classes, each one physical bearing: K001, KA04, KA15, KA22, KA30, KI14, KI17, KI21. | Survey sentence rewritten with the correct count, the supervised framing and a table-level citation. The eight-class, one-bearing-per-class reproduction task is stated in §2.2 and at the start of §6.1, separated from the three-class label space used everywhere else. | §1 ¶2, §2.2, §6.1 |
| 2 | Narrow every "SFDA" sentence, or add a neighbourhood and a 2026 bearing method | Adding NRC/AaD needs about 24 GPU-h of runs (two methods × ten splits × two arms) we have not made; narrowing costs nothing and is accurate. | Narrowed. The Conclusions open with "the source-free adaptation results we tested"; §9 states that every SFDA statement is about SDALR and our SHOT implementation under this protocol; NRC and AaD are cited. | §9, §10, refs |
| 3 | Run the same-condition control, or rewrite the identity claim | Run: pre-registered as C104 (commit `38ac6f1`) before any result, CPU only. | At each condition, with the condition identical on both sides, a random forest trained on half the source bearings' recordings loses a **median 29.7 points** on the complementary bearings (10/10 splits, p = 0.001, p_BH = 0.002). That is more than its 22.7-point cross-condition collapse. The identity claim is kept and strengthened: recording-level separation leaves the leak in place. Mechanism, descriptive: on unseen bearings, outer-race recall is 64 % for pitting and 23 % for plastic deformation, stated as a limit in §9. | §6.3 new ¶, §7, §9, §10, abstract; `results/c104/`, S1, S4 |
| 4 | Open the ledger to reviewers | — | The data-availability statement now says the ledger (1246 rows), scripts with checksums, protocol and artifacts go to the reviewers with the submission. | Declarations; S4 |
| 5 | Tighten the EAGLE caveat; decide on z = 40 | From the Bio-SFDA full text: the module adds teacher confidence and rescales thresholds online to bound band-activation rates; ours has fixed thresholds and fewer features. | The caveat names these differences and states that an activation-rate bound is not a false-acceptance bound. On z: z = 10 stays the operating point for every gain, and z = 40 is a verdict-only sensitivity check, now said explicitly. | §5, §6.6 |
| 6 | Fix the Benjamini citation | **(verified otherwise, in part.)** We cited Benjamini & Yekutieli (2001) for the BH procedure; the procedure is Benjamini & Hochberg (1995). BY 2001 is still needed, because it is what shows BH holds under positive dependence, and our tests share splits. | Both are cited, each for its role. We also report the BY adjustment, which holds under any dependence: every ten-split result survives it (largest 0.014), but **HUST does not (p_BY = 0.065)**, because six clusters cannot produce a raw p below 0.016. HUST is now described as replicating direction and size, not as independently significant. | §4, §6.3, Table 7; `results/c96/c96_family.json` |
| 7 | Highlights and abstract last | — | Rewritten after every other change: exact false-acceptance counts, "type-and-size-disjoint", SHOT "loses", the forest as a bar rather than a remedy, and the same-condition result. | abstract, highlights |

## Minor comments

| # | Item | Change | Where |
|---|---|---|---|
| 1 | Job reconciliation | The Table 3 note gives both pooled clean means with their fold values (fold job 56.8 from 58.4 and 55.3, carrying every collapse; gating job 56.0 from 56.8 and 55.3, carrying every gain) and says they are never subtracted. We used a note rather than a row, because a pooled row would put the two jobs side by side, which is the merge the reviewer wants to prevent. | Table 3 |
| 2 | Window hop | Measured from the built data: evenly spaced, non-overlapping starts, 33–34 windows per recording, hop about 7,700–7,900 samples. SDALR states no hop, and its preprocessed archive is not public, so it cannot be matched to the released loader; the text says so. | §4.1 |
| 3 | Balance per class, not per bearing | Stated in §4.1 (680/660/660). | §4.1 |
| 4 | Fold B has two outer-race bearings | In the Table 2 caption and §4.1 (1000 windows each, 50 per recording). | Table 2, §4.1 |
| 5 | Exact false-acceptance fractions in the abstract | 1, 0 and 9 of 480 against 214 of 480. | abstract |
| 6 | S04 = 222 % | Table 3 note: a share above 100 % means the oracle beats the leaky arm and is not an upper bound. | Table 3 |
| 7 | SHOT wording | §6.3 says SHOT "loses 22.1 points" and notes that its clean accuracy (65.1 %) is above SDALR's; "collapse" is kept only for the leaky-to-clean drop. SHOT is called "our implementation of the published template" in §4.3. | §4.3, §6.3, abstract |
| 8 | Forest result | Highlight rewritten: "A non-adaptive forest also collapses: a calibration bar, not a remedy." The abstract uses the same framing. | highlights, abstract |
| 9 | HUST "type-and-size-disjoint" | abstract, §6.3, §10, cover letter. | — |
| 10 | Survey citation | See "What to do" 1: the table is Vieira's Table 1, so the citation stays, with the count corrected to five. | §1 |
| 11 | Vieira "out of scope" | Confirmed: the phrase is not in their text. Replaced by their own sentence, "training and testing within a single testbench", plus the statement that they name inter-testbench, cross-domain evaluation as an alternative they do not pursue and do not evaluate SFDA. | §2.1 |
| 12 | Knap et al. | Kept. The C104 control now measures what recording-level separation leaves on the table. | §2.1, §6.3 |
| 13 | Checklist item on model selection | Added as item 7 in §8 and in the Conclusions list. | §8, §10 |
| 14 | Define accuracies before Eq. (1) | Done. | §4.4 |
| 15 | Figure 3 caption | Now says the direction (source fold B, clean target fold A), that purity pools all six tasks of that direction, and what each panel shows. | Fig. 3 |
| 16 | Family chronology in S1 only | §4 now only lists the members and points to S1 for their history. | §4, S1 |
| 17 | Ledger hashes cover analysis scripts | S4 now lists SHA-256 for all 91 analysis, evaluation, figure, kernel and runner scripts. | S4 |
| 18 | Title | "Bearing-wise evaluation of source-free domain adaptation: leakage and the limits of physics gating" (13 words, from 15). | title |
| 19 | Positioning paragraph | Added at the end of §1: Hendriks, Wheat, Vieira and Knap measured supervised or non-adaptive leakage; we add the paired SFDA evaluation on a shared checkpoint, the oracle ceiling, gate false-acceptance curves, and the same-condition control. | §1 |
| 20 | NRC and AaD | Cited: Yang et al., NeurIPS 34 (2021) 29393–29405 and NeurIPS 35 (2022) 5802–5815, checked on the proceedings pages. | §9, refs |
| 21 | Patent hedge | Kept as is. | §6.8 |
| 22 | 55.33 % line in Fig. 2 | **(verified otherwise; not done.)** 55.33 % is the block-labelling value for one composition only: fold B's clean target, with one correctly labelled 660-window bearing per fault class. Other splits have different compositions, so their block floors differ. A single line would be wrong for most rows of the figure. The derivation stays in §6.4, where it applies. | — |

## Literature

- **Narrow novelty.** Adopted in the form the reviewer gives; the §1 positioning paragraph states it.
- **ISO 15243.** §9 now says the datasheets give the damage descriptions and that mapping them onto ISO modes is our reading.
- **Items the reviewer could not open.** We opened three. The 18-paper list is Vieira's Table 1. Vieira contains no "out of
  scope" sentence. SDALR's eight-class task is in its §4. The Bio-SFDA full text was read for the caveat. The pre-registration
  commit of the new control is `38ac6f1`, and its result commit is `586b52a`.


---

# Part E — source-check report (round 5)

**Which PDF was checked.** The report reviewed a build created at 14:03:43Z on 29 September, from before the round-4
revision; the current build is from 15:15Z. Its statements that C104, the corrected survey count, the Vieira wording and
the BH/BY citations "are not in the PDF" describe that earlier build; all are in the current one. The report's
substantive points were checked on their merits, and are answered below.

| # | Point | Our check | Outcome |
|---|---|---|---|
| 1 | Vieira Table 1: five 100 % cells, supervised single-testbench corpus, no "out of scope" | Agrees with our own reading of arXiv v5 (Part D). One refinement from the same page: "condition-wise" there means load, rotation speed or noise level. | §1 now says "nine by condition (load, speed or noise level)". |
| 2 | Tell readers that 96.2 % (reproduction) and 94.1 % (leaky arm) measure different things | Correct. | §6.1 closes with that bridge: 96.2 % is an eight-class, same-bearing figure; 94.1 % is the three-class leaky baseline the collapse is measured against. |
| 3 | Bio-SFDA: online threshold updates belong to SPIDER, not EAGLE | **Partly correct.** The report had the abstract only. The full text (Results in Engineering 30:111105, p. 6) says both: in EAGLE's target self-calibration "a light-weight routine rescales thresholds so that band activation rates stay within a conservative range", and "SPIDER … may apply bounded multiplicative factors to adaptive_thresholds"; SPIDER also updates the acceptance thresholds (τs, τw) of the teacher–student gate (Eq. 4.11). | §5 names both mechanisms and SPIDER. |
| 4 | Multiplicity: BY for HUST at rank 1 would be far above 0.065 | **Not applicable to this family.** HUST is not rank 1. With exact sign-flip p-values (five tests at 1/1024, the gate gain at 3/1024, HUST at 1/64, three fold-level tests at 1/4) and m = 10, HUST is rank 7: p_BY = (1/64)·10·2.929/7 = 0.0654, the case the report itself lists as coherent. The largest ten-split value is the gate gain at rank 6: (3/1024)·10·2.929/6 = 0.0143. | Printed values unchanged; §4 lists the ten members, so m is explicit. |
| 5 | Damage labels are Lessmeier et al. 2016 Table 5, not only datasheets; ISO 15243 clauses 5.1 / 5.5 | Correct. Table 5 of the dataset paper reads "fatigue: pitting" for KA04, KA16, KA22 and all six KI bearings, and "Plastic deform.: Indentations" for KA15 and KA30. The ISO 15243:2017 contents list 5.1 Rolling contact fatigue and 5.5 Plastic deformation. | §9 cites Table 5 and the clause numbers; "our reading" removed. |
| 6 | C104 shows specimen and/or mechanism structure in a random forest, not pure identity, and not an SFDA result | **Correct, and we measured it further** rather than only rewording. A post-hoc per-class breakdown of the same design (C104b, labelled post-hoc in the protocol) gives median recall drops on unseen bearings of 1.7 points (healthy), **28.5 points (inner race, a single mechanism)** and 66.0 points (outer race, two mechanisms), each in 10/10 splits. The loss survives inside one mechanism, mechanism adds to it where it varies, and healthy specimens transfer. | §6.3 rewritten: the control removes condition shift, not every specimen difference; what the source set fails to cover is the specimen-level damage signature, with mechanism where it differs and possibly session. It is labelled a random-forest control, not an adaptation result. §9: session and mounting are not crossed; SDALR and SHOT were not run at a fixed condition. The comparison with the 22.7-point cross-condition loss is called forest-internal. |
| 7 | HUST publishes no pitch diameter; skipping the gate is defensible | Agrees with §3. | No change. |
| 8 | NRC and AaD citations; narrow SFDA claims to SDALR and SHOT | Already done in round 4, from the proceedings pages. | No change. |
| 9 | Run SDALR or SHOT under the same-condition arm | Not run. It would show whether adaptation amplifies or reduces the loss the forest shows. | Stated as an open measurement in §9. |


---

# Part F - internal review round 6 (2026-10-02)

A full internal referee pass (citations checked against primary sources, literature search, numbers re-derived from the
artifacts, an independent blind report, an MSSP guide check; `paper/review_2026-10-02/`) found that several claims went
beyond what the design identifies. Each item was checked before acting. New analyses are protocol entries C103b and
C105-C109 (post-hoc, descriptive) and C110-C112 (pre-registered in commit `6c160c9` before any run).

| # | Finding | What we did | Where |
|---|---|---|---|
| F1 | The SFDA-specific motivation was never tested, although the batch-0 (source-only) accuracy was in every log. | C105: source-only gap median 35.1 pp (CI 24.4-50.6, 10/10); SDALR changes it by +4.7 pp (p = 0.18) and lowers clean accuracy in 7/10 splits; SHOT narrows it by losing leaky accuracy. Title, abstract, introduction and conclusions now say the loss is in the source model and adaptation inherits it. | title, abstract, sec. 1, 6.2, 7, 10; Table 3 column, Table 4 row |
| F2 | "Attributable to bearing overlap alone" was not identified: leaky and clean targets hold different bearings. | Wording corrected; C106 within-bearing contrast (median 38.7 pp; 14 positive, 3 ties, 0 negative); per-bearing table with manufacturer, mode, extent and size from the datasheets (new Table 6). The second term of Eq. 1 is renamed "not recovered". | sec. 4.1, 6.2, Table 6, Fig. 3a |
| F3 | The identity-shortcut mechanism was not separated from under-sampling of damage signatures. | C110 (pre-registered): unseen-bearing accuracy 45.9 / 57.9 / 66.9 / 74.6 % for 1-4 source bearings per class; rule met. C111: the probe survives removing the mean, does not track within-session drift, and identifies healthy specimens that still transfer. The paper now concludes under-sampling, and the representation-level-remedy sentence that contradicted the limitations is gone. | sec. 6.4, 7, 9, 10, Fig. 3b |
| F4 | 2048-sample windows cannot carry the kinematic signature (32 ms, about 31 Hz envelope resolution). | Stated with its arithmetic (new sec. 3.2). C112 (pre-registered): a forest on 13 kinematic envelope features leaks a median 8.4 pp (rule: transfers) but is weak on both arms (65.8 / 56.1 %). | sec. 3.2, 6.4, Table 4 |
| F5 | The fold job and the gating job trained different source checkpoints (batch-0 accuracy differs by up to 9.3 pp), and the C103 diagnosis had the wrapper acting first at the pre-update evaluation. | C103b: it acts at the mid-pretraining validation call. Fig. 1 caption, sec. 4.6 and Table 3 corrected; the fold-level recoverable share, which crossed jobs, is withdrawn; the graphical abstract is rebuilt from ten-split medians computed from the artifacts. | sec. 4.6, Table 3, Fig. 1, graphical abstract |
| F6 | The coverage-gain correlation is partly built in; coverage used labels; the raw-spectrum effect hid a sign flip. | C107: certified windows +47 pp, uncovered +0.3 pp, 104 % of the gain on certified windows; label-free coverage rho 0.93, textbook partial 0.90. Raw-spectrum row added to Table 7 (+5.35 / -13.21 by fold). Gate coverage traced to damage extent: the four certifiable bearings are the largest damages. | sec. 6.6, Tables 5 and 7, Fig. 5 |
| F7 | The oracle was called an upper bound; the promised bootstrap intervals were absent. | "Oracle reference" throughout, with Schlachter et al. cited as the precedent; C109 intervals for every median and for false acceptance (bearing-cluster or Clopper-Pearson). | sec. 4.4, 6.5, Tables 3 and 5 |
| F8 | Novelty overlaps: Vieira's fixed-train design and repetition-wise split, Knap's cross-bearing scenario, concurrent held-out-bearing work. | Novelty paragraph rewritten with deltas; Vieira Table 12, Knap, Nagaswetha and Pathak, Kaya and Jobani, Schlachter et al., Jia et al. (PIUDA) and Saeb et al. cited; the false "in all of this work" sentence removed. | sec. 1, 2 |
| F9 | Factual errors. | Table 1 conditions (three for adaptation) and CWRU baseline rate (48 kHz); PCTL described correctly (confidence supervision, not a pseudo-label filter); the envelope rule's kurtogram band selection and normalisation stated; Vieira's 18th paper ("not detailed"); KA04 purity; probe pool 1020 (508/512); SHOT code statement; SDALR archive wording; UORED slip contradiction; bib DOIs, pages and issues. | throughout |
| F10 | The slip section was off-thesis, its median below the estimator accuracy, its negative slips uninterpreted. | Moved to Supplementary S5 with a corrected reading: negative values indicate kinematic offsets, and one value at +4.07 % is an estimator failure. | S5, sec. 5 |
| F11 | MSSP compliance. | Abstract 231 words with acronyms defined; AI declaration retitled, with model and version; data statement names JNU and points to a deposit. Still human-only: deposit DOI, separate highlights file, declarations .docx, author details. | abstract, declarations |


---

# Part G - two external LLM review reports (2026-10-02)

Both reports were checked against the manuscript, the artifacts and the cited sources before acting.

**Adopted:**
- Title and abstract no longer generalise from two methods to SFDA as a class. The new title is "Bearing leakage survives
  source-free adaptation: a bearing-wise evaluation of SDALR and SHOT with physics-gated pseudo-labels". The conclusions say
  "both adaptation methods".
- The 46 to 75 % source-diversity result is labelled as a random-forest result in the highlights, abstract, discussion,
  conclusions and cover letter. The discussion states that SDALR and SHOT were not run on the curve.
- HUST is described as replicating the effect "in direction and size" in the abstract and the cover letter.
- The protocol now states that window accuracy equals balanced accuracy, because every target holds 2000 windows per class.
- The discussion integrates the two readings: under-sampling makes specimen-specific features sufficient, and diversity
  breaks reliance on them.
- The limitations explain why neighbourhood-based SFDA (NRC, AaD) is expected to inherit the gap; this is stated as an
  expectation, not a result.
- Section 5 concedes that Bio-SFDA's published controller may suppress much of the false acceptance we measured with fixed
  thresholds.
- The conclusions require verified healthy recordings from the target machine before a physics gate is used.

**Not adopted, with reasons:**
- Report 1 expands SDALR as "Source-Domain Adaptation with Label Relaxation". This is not the method's name; the paper is
  "Both reliable and unreliable predictions matter" (Neurocomputing 657:131661).
- Report 1 says CNNs memorise "high-frequency resonances" and calls the oracle a "theoretical upper bound". Neither is
  supported by our measurements, and C108 shows that block labelling occurs equally on seen bearings.
- Report 2 asks for the diversity curve to be re-run on the SFDA backbone. That needs GPU runs on 30 triples x 4 levels.
  The result is scoped to the forest instead and stated as a limitation.
- Report 2 asks for a gate hold-out score. This is already reported: uncovered faulty windows gain a median of 0.3 pp (C107).
- Data and code deposit: remains a human-only item, since public release needs the authors' account and consent.
