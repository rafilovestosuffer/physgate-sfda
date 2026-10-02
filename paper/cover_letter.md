# Cover letter — Mechanical Systems and Signal Processing

**Date:** 2026-10-02

Dear Editor,

We submit our manuscript "Bearing leakage survives source-free adaptation: a bearing-wise evaluation of SDALR and SHOT with physics-gated pseudo-labels" for consideration as a Standard Research Article (subject area A) in *Mechanical Systems and Signal
Processing*.

**The engineering problem.** A condition-monitoring system earns its place by making a correct call on a bearing it has not
seen before. Published source-free domain adaptation results for rolling bearings report 94–100 % accuracy, but the
evaluation protocols behind those numbers put the same physical bearings on both sides of the transfer task. Whether the
reported reliability survives on a new specimen has not been measured, and a maintenance decision cannot rest on a number
that has not been tested that way.

**What we did.** We built a paired design in which the source model, the operating conditions, the windows and the seed are
all held fixed and only bearing overlap changes, so the difference measures exactly one thing. Every hypothesis, decision
rule and budget was committed to a versioned protocol before the corresponding runs; the change log, the run ledger and the
retained artifacts accompany the paper. Where our own explanations failed a test, the paper says so: a measured A/A
floor of zero falsified our first account of a small cross-job difference, and the pre-registered test of our second
account rejected it too.

**What we found.** On Paderborn, bearing-disjoint targets cost a published SFDA method a median 36.2 points over ten
pre-registered bearing splits (95 % CI 25.0-56.3), and a given bearing loses a median 38.7 points when it is unseen rather
than seen. The gap is already present in the source model before any adaptation step (35.1 points): SDALR and SHOT
inherit it and do not repair it. Non-adaptive random forests, a fixed-condition control and a second rig (HUST, in direction and size)
show the same loss. A pre-registered source-diversity curve shows why: accuracy on unseen bearings rises from 46 % to 75 %
as the source grows from one to four specimens per class (random forest), so three specimens per class under-sample the damage signatures.

**The signal-processing contribution.** Envelope-based kinematic gates accept 0 to 9 of 480 healthy recordings as faulty,
against 214 for a raw-spectrum band rule of the kind used in recent physics-guided adaptation. Inside the adaptation loop the
safe gate adds a median 4.5 points, almost entirely on the recordings it certifies, and an oracle pseudo-label filter shows
that correct labels would recover a median 82 % of the loss. Every envelope-based gate certifies the same four specimens,
those with the largest damage according to the dataset's own damage profiles: on this rig the limit of physics-gated
adaptation is the detectability of small damage, not the gate. Kinematics are resolved per specimen from each rig's own
documentation, and gate safety is measured on healthy bearings rather than assumed.

**Why MSSP.** The work is about the validity of vibration-based diagnosis on real machinery: the kinematics are resolved
per specimen from each rig's own documentation, gate safety is measured on healthy bearings rather than assumed, and the
recommendations are addressed to anyone deploying such a system. It extends the bearing-wise evaluation argument published in this journal (Vieira et al., MSSP 258, 2026),
which concerns supervised training within a single test bench, to source-free adaptation, and it reports the failures of
our own physics gates as plainly as their gains.

The manuscript is original, is not under consideration elsewhere, and the author approves the submission. I have no
competing interests to declare.

Yours sincerely,

Mohammad Rafiur Rahman  
Department of Mechanical Engineering, Chittagong University of Engineering & Technology (CUET), Bangladesh  
u2303064@student.cuet.ac.bd
