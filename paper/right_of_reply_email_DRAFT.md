# DRAFT — right-of-reply email to the Bio-SFDA authors (NOT SENT; the authors of this paper send it)

**To:** Jongpil Jeong (corresponding author, Sungkyunkwan University) — jpjeong@skku.edu (address as printed in the article)
**Subject:** Reimplementation of the EAGLE gating mechanism (Results in Engineering 30:111105) — invitation to comment

Dear Professor Jeong,

We are preparing a manuscript on the evaluation of physics-based pseudo-label gating in source-free domain adaptation for
bearing diagnosis, and we discuss your article "Bio–SFDA: Physics-guided multimodal source-free domain adaptation for reliable
bearing fault diagnosis" (Results in Engineering 30:111105, 2026).

Because code for the article is not publicly available, we reimplemented the gating mechanism from the description in
Section 4.2 (band-energy and SNR predicates at BPFO, BPFI and BSF on the STFT, with robust z-scoring across records). In our
evaluation on 480 healthy Paderborn records, this reimplementation accepted a fault label for 214 records at our chosen
threshold. We state in the manuscript that this concerns our reimplementation of the described mechanism, not your
implementation, and we do not compare with the accuracy reported in your paper because we could not determine the exact data
split and label definition used for Paderborn (Section 5.2 lists a ball class, which the Paderborn data set does not include).

We would value your view before submission, in particular:
1. whether our reading of the EAGLE predicates and thresholds matches your implementation;
2. which Paderborn bearings and window length were used, and how the ball class was defined;
3. whether you would be willing to share the code or the split, so that we can report your implementation directly.

We are happy to share our reimplementation and evaluation scripts. We would include any correction or comment you provide.

With kind regards,
[authors]
