"""Fig. 1: (a) the paired leaky/clean design, (b) the physics gate on the pseudo-label step, (c) the paired contrasts.

Drawn in millimetres at printed size (190 mm, Elsevier double column). Panels (a) and (b) contain real data, recomputed
here rather than drawn:
  - raw vibration from one source bearing per class of split S00 at the source condition, with the windows that the
    adaptation data actually use (make_m0.even_starts, same per-record window count as make_k10);
  - the envelope-rule spectrum of two clean-target recordings of S00 at the target condition, computed with the gate
    code (experiments/gate_roc.pcv_record path) and asserted against the retained in-loop verdicts
    (results/m2/gate_verdicts.json).
The split, conditions, records and verdict counts are written to paper/figures/data/fig1_design.csv.

Run: python paper/figures/fig1_design.py   (also called by build_schematics.py)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import style as S  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

# ---- example shown in the figure (split from configs/splits_k10.yaml; conditions as in Section 3)
SPLIT = "S00"
COND = {"A1": "N15_M01_F10", "A2": "N15_M07_F04", "A3": "N15_M07_F10"}
SRC, TGT = "A2", "A1"
Z_GATE = 10.0                       # fixed envelope-rule operating point (Section 4, Gating)
TRACE_S = 0.5                       # seconds of raw signal shown per trace
X_ORD = 15.5                        # spectrum axis: covers the first three BPFO and BPFI harmonics
CLASSES = ("normal", "outer_race", "inner_race")
CLASS_TXT = {"normal": "healthy", "outer_race": "outer race", "inner_race": "inner race"}

# ---- page geometry and type
W_MM, H_MM = 190.0, 117.0
FS = 7.0                            # every text span >= 7 pt (validate_figures.py)
FS_H = 7.5                          # stage headers
FS_T = 8.0                          # panel titles, as in the other figures
FS_M = 9.0                          # mathtext labels: subscripts render at 0.7 x 9 = 6.3 pt

INK = "#1F2328"
MUTED = "#555D66"
LINE = "#4B5258"
STAGE_FILL = "#F3F4F6"
STAGE_EDGE = "#D5D9DE"
BADGE = "#2F3B45"
NEUTRAL = "#8A939B"


def tint(hex_colour: str, a: float) -> tuple:
    """hex_colour mixed with white; a = share of the colour."""
    h = hex_colour.lstrip("#")
    rgb = np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])
    return tuple(1 - a * (1 - rgb))


# ------------------------------------------------------------------ data
def _load_example():
    import comb
    import band_select
    import prewhiten
    import pu
    import ses
    from harmonic_coords import J_SIDE, K_HARM
    from h6_prewhitening import N_SAMPLES, PU_BAND_HI_HZ
    from kinematics import kinematics, slip_window
    from make_m0 import PER_CLASS, W, even_starts

    split = yaml.safe_load((ROOT / "configs" / "splits_k10.yaml").read_text(encoding="utf-8"))["splits"][SPLIT]
    stored = json.loads((ROOT / "results" / "m2" / "gate_verdicts.json").read_text(encoding="utf-8"))["pcv"]

    traces = []
    for c in CLASSES:
        bid = split["source"][c][0]
        rid = f"{COND[SRC]}_{bid}_1"
        order = [p.stem for p in pu.files(bearings=split["source"][c], conditions=[COND[SRC]])]
        assert len(order) == 20 * len(split["source"][c]), (c, len(order))
        i, n = order.index(rid), len(order)
        k = PER_CLASS // n + (1 if i < PER_CLASS % n else 0)          # make_m0.windows_from_records
        r = pu.read_one(ROOT / "data" / "pu" / bid / f"{rid}.mat")
        starts = even_starts(r.signal.size, k)
        traces.append(dict(cls=c, bid=bid, rid=rid, fs=r.fs_hz, x=r.signal.astype(float), starts=starts, W=W, k=k))

    def spectrum(bid):
        rid = f"{COND[TGT]}_{bid}_1"
        r = pu.read_one(ROOT / "data" / "pu" / bid / f"{rid}.mat")
        kin = kinematics(r.bearing_model)
        fr = r.rpm / 60
        y = prewhiten.prewhiten(r.signal[:N_SAMPLES].astype(float), "none")
        b = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * kin.BPFI + J_SIDE) * fr,
                                    f_hi=PU_BAND_HI_HZ)
        f, Sx = ses.squared_envelope_spectrum(y, r.fs_hz, band=(b.lo_hz, b.hi_hz))
        z = comb.normalise(f, Sx)
        peaks, at = {}, {}
        for fam in ("BPFO", "BPFI"):
            peaks[fam], at[fam] = [], []
            for h in (1, 2, 3):
                lo, hi = slip_window(kin, fam, harmonic=h)
                m = np.flatnonzero((f >= lo * fr) & (f <= hi * fr))
                j = m[np.argmax(z[m])]
                peaks[fam].append(float(z[j]))
                at[fam].append(float(f[j] / fr))
        lit = [fam for fam in peaks if sum(p > Z_GATE for p in peaks[fam]) >= 2]
        assert len(lit) <= 1, (rid, peaks)
        verdict = {"BPFO": "outer_race", "BPFI": "inner_race"}[lit[0]] if lit else "normal"
        assert verdict == stored[rid], f"{rid}: recomputed {verdict}, retained {stored[rid]}"
        same = [v for key, v in stored.items() if key.startswith(f"{COND[TGT]}_{bid}_")]
        assert len(same) == 20, (bid, len(same))
        return dict(bid=bid, rid=rid, order=f / fr, z=z, peaks=peaks, at=at, verdict=verdict,
                    n_same=sum(v == verdict for v in same), n_rec=len(same), BPFO=kin.BPFO, BPFI=kin.BPFI,
                    n_samples=N_SAMPLES, fs=r.fs_hz)

    assert "KA04" in split["target"]["outer_race"] and "KI17" in split["target"]["inner_race"]
    spectra = [spectrum("KA04"), spectrum("KI17")]
    assert spectra[0]["verdict"] == "outer_race" and spectra[1]["verdict"] == "normal"
    assert all(3 * max(sp["BPFO"], sp["BPFI"]) < X_ORD for sp in spectra)   # all six harmonics the rule reads are shown
    return split, traces, spectra


# ------------------------------------------------------------------ drawing helpers (mm, y downwards)
class Canvas:
    def __init__(self):
        S.apply()
        plt.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic",
                             "mathtext.bf": "Arial:bold", "mathtext.default": "it"})
        self.fig = plt.figure(figsize=(W_MM * S.MM, H_MM * S.MM))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W_MM)
        ax.set_ylim(H_MM, 0)
        ax.set_aspect("equal")
        ax.axis("off")
        self.ax = ax

    def inset(self, x, y, w, h):
        a = self.fig.add_axes([x / W_MM, 1 - (y + h) / H_MM, w / W_MM, h / H_MM])
        a.patch.set_alpha(0)
        return a

    def text(self, x, y, s, size=FS, color=INK, ha="left", va="center", weight="normal", **kw):
        return self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, zorder=6, **kw)

    def rbox(self, x, y, w, h, face, edge, lw=0.6, r=1.2, z=1, ls="-"):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", facecolor=face,
                                         edgecolor=edge, linewidth=lw, zorder=z, linestyle=ls))

    def armbox(self, x, y, w, h, colour, title, sub=None):
        """Tinted box with a solid accent bar on the left: the arm colour is carried by the bar and the border."""
        self.rbox(x, y, w, h, tint(colour, 0.12), colour, lw=0.7, r=1.0, z=2)
        self.ax.add_patch(Rectangle((x + 0.35, y + 0.35), 1.1, h - 0.7, facecolor=colour, edgecolor="none", zorder=3))
        if sub is None:
            self.text(x + 3.0, y + h / 2, title)
        else:
            self.text(x + 3.0, y + h / 2 - 1.55, title, weight="bold")
            self.text(x + 3.0, y + h / 2 + 1.6, sub, color=MUTED)

    def line(self, pts, color=LINE, lw=0.7, ls="-", z=4):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="butt", zorder=z)

    def arrow(self, pts, color=LINE, lw=0.7, both=False):
        """Orthogonal connector through pts; arrowhead on the last segment (and the first if both)."""
        if len(pts) > 2:
            self.line(pts[:-1], color=color, lw=lw)
        style = "<|-|>" if both else "-|>"
        self.ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle=style, mutation_scale=6.5, lw=lw,
                                          color=color, shrinkA=0, shrinkB=0, zorder=5))

    def stage(self, x, y, w, h, num, title):
        self.rbox(x, y, w, h, STAGE_FILL, STAGE_EDGE, lw=0.5, r=1.6, z=0)
        self.ax.add_patch(Circle((x + 3.4, y + 3.6), 2.05, facecolor=BADGE, edgecolor="none", zorder=3))
        self.text(x + 3.4, y + 3.65, str(num), color="white", ha="center", weight="bold")
        self.text(x + 6.6, y + 3.6, title, size=FS_H, weight="bold")

    def bracket(self, x, y0, y1, tick=1.0, color=LINE, lw=0.6):
        self.line([(x - tick, y0), (x, y0), (x, y1), (x - tick, y1)], color=color, lw=lw)

    def check(self, cx, cy, s=1.1, color=INK):
        self.line([(cx - s, cy), (cx - 0.35 * s, cy + 0.7 * s), (cx + s, cy - 0.85 * s)], color=color, lw=0.9)

    def cross(self, cx, cy, s=0.85, color=INK):
        self.line([(cx - s, cy - s), (cx + s, cy + s)], color=color, lw=0.9)
        self.line([(cx - s, cy + s), (cx + s, cy - s)], color=color, lw=0.9)

    def bearing(self, cx, cy, R):
        """Deep-groove ball bearing, front view, 8 rolling elements (Paderborn 6203 datasheets: 'pc. 8')."""
        u = R / 20.0                                 # drawn on a 40 mm outside diameter, 17 mm bore, 6.75 mm balls
        ax = self.ax
        for r_out, r_in in ((20.0, 17.0), (12.2, 8.5)):
            ax.add_patch(Circle((cx, cy), r_out * u, facecolor="#C9CFD5", edgecolor=LINE, lw=0.5, zorder=3))
            ax.add_patch(Circle((cx, cy), r_in * u, facecolor="white" if r_in < 10 else STAGE_FILL,
                                edgecolor=LINE, lw=0.5, zorder=3))
        for i in range(8):
            t = 2 * np.pi * i / 8 + np.pi / 8
            ax.add_patch(Circle((cx + 14.6 * u * np.cos(t), cy + 14.6 * u * np.sin(t)), 3.0 * u,
                                facecolor="#4F5A64", edgecolor="none", zorder=4))

    def network(self, x, y, w, h, color=BADGE):
        layers = [3, 4, 4, 3]
        xs = np.linspace(x, x + w, len(layers))
        pos = [[(xx, y + h * (j + 1) / (n + 1)) for j in range(n)] for xx, n in zip(xs, layers)]
        for a, b in zip(pos[:-1], pos[1:]):
            for p in a:
                for q in b:
                    self.line([p, q], color=tint(color, 0.45), lw=0.3, z=3)
        for col in pos:
            for p in col:
                self.ax.add_patch(Circle(p, 0.62, facecolor="white", edgecolor=color, lw=0.6, zorder=4))


# ------------------------------------------------------------------ figure
def build():
    split, traces, spectra = _load_example()
    cv = Canvas()
    C = S.C
    src_b = {c: split["source"][c] for c in CLASSES}
    tgt_b = {c: split["target"][c] for c in CLASSES}
    n_src = sum(len(v) for v in src_b.values())
    n_tgt = sum(len(v) for v in tgt_b.values())

    # =============================== (a) paired design
    cv.text(0.8, 2.6, "(a) Paired leaky/clean design", size=FS_T)
    top, bot = 6.0, 60.0
    X1, X2, X3, X4 = (0.0, 41.5), (43.5, 84.5), (86.5, 147.5), (149.5, 190.0)

    # ---- stage 1: bearing pool
    cv.stage(X1[0], top, X1[1] - X1[0], bot - top, 1, "Bearing pool")
    cv.bearing(X1[1] - 4.6, top + 4.4, 3.4)
    cw, ch, gap, pitch = 11.0, 3.9, 1.2, 4.55
    gx = X1[0] + 2.6
    y0 = top + 12.4
    cols = {"normal": ["K001", "K002", "K003", "K004", "K005", "K006"],
            "outer_race": ["KA04", "KA15", "KA16", "KA22", "KA30"],
            "inner_race": ["KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]}
    for j, c in enumerate(CLASSES):
        assert sorted(src_b[c] + tgt_b[c]) == cols[c], c
        xc = gx + j * (cw + gap)
        cv.text(xc + cw / 2, y0 - 2.9, {"normal": "healthy", "outer_race": "outer", "inner_race": "inner"}[c],
                ha="center", color=MUTED)
        for i, b in enumerate(cols[c]):
            col = C["leaky"] if b in src_b[c] else C["clean"]
            cv.rbox(xc, y0 + i * pitch, cw, ch, tint(col, 0.16), col, lw=0.6, r=0.7, z=2)
            cv.text(xc + cw / 2, y0 + i * pitch + ch / 2 + 0.05, b, ha="center")
    ly = y0 + 6 * pitch + 2.4
    for k, (col, lab) in enumerate(((C["leaky"], f"source / leaky ({n_src})"), (C["clean"], f"clean ({n_tgt})"))):
        cv.rbox(gx, ly + k * 4.2 - 1.3, 3.4, 2.6, tint(col, 0.16), col, lw=0.6, r=0.5, z=2)
        cv.text(gx + 4.8, ly + k * 4.2, lab)

    # ---- stage 2: source training
    cv.stage(X2[0], top, X2[1] - X2[0], bot - top, 2, f"Source training at {SRC}")
    tx, tw, th = X2[0] + 2.4, X2[1] - X2[0] - 4.8, 5.6
    ty = [top + 11.0, top + 19.4, top + 27.8]
    for t, yy in zip(traces, ty):
        n = int(TRACE_S * t["fs"])
        x = t["x"][:n]
        scale = np.percentile(np.abs(x), 99.9)
        a = cv.inset(tx, yy, tw, th)

        def envelope(seg, t0, ncol):
            m = seg[: len(seg) // ncol * ncol].reshape(ncol, -1)
            tt = t0 + (np.arange(ncol) + 0.5) * m.shape[1] / t["fs"]
            return tt, np.clip(m.min(1) / scale, -1, 1), np.clip(m.max(1) / scale, -1, 1)

        a.fill_between(*envelope(x, 0.0, 520), color="#B9BFC5", lw=0, zorder=1)
        for s0 in t["starts"]:                       # the windows the adaptation data actually use
            if s0 + t["W"] <= n:
                a.fill_between(*envelope(x[s0:s0 + t["W"]], s0 / t["fs"], 32), color=C["leaky"], lw=0, zorder=2)
        a.set_xlim(0, TRACE_S)
        a.set_ylim(-1.08, 1.08)
        a.axis("off")
        cv.text(tx, yy - 1.45, t["bid"], color=MUTED)
    sb_y = ty[-1] + th + 2.2
    cv.rbox(tx, sb_y - 1.1, 2.0, 2.2, C["leaky"], "none", r=0.2, z=2)
    cv.text(tx + 3.2, sb_y, "window", color=MUTED)
    cv.line([(tx + tw - 0.1 / TRACE_S * tw, sb_y), (tx + tw, sb_y)], color=INK, lw=0.8)
    cv.text(tx + tw - 0.1 / TRACE_S * tw - 1.0, sb_y, "0.1 s", ha="right")
    mb_x, mb_w, mb_h = X2[0] + 2.4, X2[1] - X2[0] - 4.8, 9.6
    mb_y = bot - 2.6 - mb_h
    cv.arrow([(mb_x + mb_w / 2, sb_y + 2.0), (mb_x + mb_w / 2, mb_y)])
    cv.rbox(mb_x, mb_y, mb_w, mb_h, "white", BADGE, lw=0.7, r=1.2, z=2)
    cv.network(mb_x + 2.2, mb_y + 0.6, 7.6, mb_h - 1.2)
    cv.text(mb_x + 12.4, mb_y + mb_h / 2 - 1.55, "Source model", weight="bold")
    cv.text(mb_x + 12.4, mb_y + mb_h / 2 + 1.6, "SDALR", color=MUTED)

    # ---- stage 3: adaptation
    cv.stage(X3[0], top, X3[1] - X3[0], bot - top, 3, f"Adaptation at {TGT}")
    lx, lw_ = X3[0] + 4.6, X3[1] - X3[0] - 6.8
    leaky_y, leaky_h = top + 8.4, 8.6
    cv.armbox(lx, leaky_y, lw_, leaky_h, C["leaky"], "Leaky target", f"same {n_src} bearings")
    clean_y = leaky_y + leaky_h + 3.6
    clean_h = bot - 2.4 - clean_y
    cv.rbox(lx, clean_y, lw_, clean_h, tint(C["clean"], 0.05), C["clean"], lw=0.7, r=1.2, z=1)
    cv.text(lx + 3.0, clean_y + 3.1, "Clean target", weight="bold")
    cv.text(lx + 20.0, clean_y + 3.1, f"other {n_tgt} bearings", color=MUTED)
    ax_ = lx + 2.6
    aw, ah, astep = lw_ - 4.6, 6.0, 7.6
    arm_y = [clean_y + 6.2 + i * astep for i in range(3)]
    arms = [("clean", "ungated"), ("gated", "+ physics gate"), ("oracle", "+ oracle filter")]
    for (key, lab), yy in zip(arms, arm_y):
        cv.armbox(ax_, yy, aw, ah, C[key], lab)
    trunk_x = X3[0] + 2.3
    mid = mb_y + mb_h / 2
    cv.line([(mb_x + mb_w, mid), (trunk_x, mid)])
    targets_y = [leaky_y + leaky_h / 2] + [yy + ah / 2 for yy in arm_y]
    cv.line([(trunk_x, min(targets_y)), (trunk_x, max(max(targets_y), mid))])
    cv.arrow([(trunk_x, targets_y[0]), (lx, targets_y[0])])
    for yy in targets_y[1:]:
        cv.arrow([(trunk_x, yy), (ax_, yy)])
    for yy in targets_y:
        cv.ax.add_patch(Circle((trunk_x, yy), 0.42, facecolor=LINE, edgecolor="none", zorder=5))

    # ---- stage 4: readouts
    cv.stage(X4[0], top, X4[1] - X4[0], bot - top, 4, "Accuracy")
    rx = X4[0] + 4.6
    reads = [("leaky", r"$a_{\mathrm{leaky}}$"), ("clean", r"$a_{\mathrm{clean}}$"), ("gated", r"$a_{\mathrm{gated}}$"),
             ("oracle", r"$a_{\mathrm{oracle}}$")]
    ends = [lx + lw_] + [ax_ + aw] * 3
    for (key, lab), yy, x_end in zip(reads, targets_y, ends):
        cv.arrow([(x_end, yy), (rx - 1.6, yy)])
        cv.ax.add_patch(Circle((rx, yy), 1.15, facecolor=C[key], edgecolor="white", lw=0.4, zorder=6))
        cv.text(rx + 2.4, yy, lab, size=FS_M)
    dx = X4[0] + 25.0
    cv.arrow([(dx, targets_y[0] + 1.3), (dx, targets_y[1] - 1.3)], both=True, lw=0.75)
    cv.text(dx + 1.8, (targets_y[0] + targets_y[1]) / 2, r"$\Delta_{\mathrm{leak}}$", size=FS_M)

    # =============================== (b) gate on the pseudo-label step
    by = 66.0
    cv.text(0.8, by, "(b) Physics gate on pseudo-labels", size=FS_T)
    sx, sw, sh = 7.5, 46.5, 13.0
    s_y = [by + 11.0, by + 29.5]
    ky, kx = by + 5.0, sx
    for lab, filled in (("BPFO", True), ("BPFI", False)):
        cv.ax.plot([kx + 0.9], [ky], marker="v", ms=3.2, mfc=INK if filled else "white", mec=INK, mew=0.6, zorder=6)
        cv.text(kx + 2.4, ky, lab)
        kx += 10.5
    cv.line([(kx, ky), (kx + 4.0, ky)], color=INK, lw=0.6, ls=(0, (3, 2)))
    cv.text(kx + 5.0, ky, f"z = {Z_GATE:g}")
    for i, (sp, yy) in enumerate(zip(spectra, s_y)):
        a = cv.inset(sx, yy, sw, sh)
        keep = sp["order"] <= X_ORD
        a.plot(sp["order"][keep], np.clip(sp["z"][keep], 0.3, None), color="#2E353B", lw=0.35, zorder=2)
        a.axhline(Z_GATE, color=INK, lw=0.6, ls=(0, (3, 2)), zorder=3)
        a.set_yscale("log")
        a.set_ylim(0.3, 3000)
        a.set_xlim(0, X_ORD)
        a.set_yticks([1, 10, 100, 1000])
        a.set_yticklabels(["1", "10", "100", "1000"])
        a.minorticks_off()
        a.set_xticks(range(0, 16))
        a.set_xticklabels([str(v) if v % 5 == 0 else "" for v in range(0, 16)] if i == 1 else [])
        a.tick_params(labelsize=FS, length=2.0, width=0.5, pad=1.5)
        for side in ("left", "bottom"):
            a.spines[side].set_linewidth(0.5)
        for fam, filled in (("BPFO", True), ("BPFI", False)):
            for h in (1, 2, 3):
                o = sp[fam] * h
                if o <= X_ORD:
                    a.plot([o], [1700], marker="v", ms=3.2, mfc=INK if filled else "white", mec=INK, mew=0.6,
                           zorder=4, clip_on=False)
                if sp["peaks"][fam][h - 1] > Z_GATE:
                    a.plot([sp["at"][fam][h - 1]], [sp["peaks"][fam][h - 1]], marker="o", ms=2.8, mfc=C["gated"],
                           mec="white", mew=0.3, zorder=5)
        a.set_ylabel("z", fontsize=FS, labelpad=1.5)
        cls = "outer race" if sp["bid"].startswith("KA") else "inner race"
        cv.text(sx, yy - 2.4, f"{sp['bid']}", weight="bold")
        cv.text(sx + 8.0, yy - 2.4, cls, color=MUTED)
        vx, vw, vh = sx + sw + 4.2, 13.6, 6.0
        vy = yy + sh / 2 - vh / 2
        speaks = sp["verdict"] != "normal"
        cv.arrow([(sx + sw + 0.8, yy + sh / 2), (vx, yy + sh / 2)])
        cv.rbox(vx, vy, vw, vh, tint(C["gated"], 0.18) if speaks else "white", C["gated"] if speaks else NEUTRAL,
                lw=0.7, r=0.9, z=2, ls="-" if speaks else (0, (2.5, 1.5)))
        cv.text(vx + vw / 2, vy + vh / 2, "outer race" if speaks else "silent", ha="center")
    cv.text(sx + sw / 2, s_y[1] + sh + 5.6, "shaft order", ha="center")

    # rule table: pseudo-label y-hat against verdict v
    gx0, gx1 = 75.5, 120.0
    rows = [(r"$v$ silent", "unchanged", None),
            (r"$v = \hat{y}$", r"keep $\hat{y}$", "check"),
            (r"$v \neq \hat{y}$", r"withhold $\hat{y}$", "cross")]
    rh, ry0, cond_w = 6.0, s_y[0] - 0.6, 12.5
    for i, (cnd, out, icon) in enumerate(rows):
        yy = ry0 + i * (rh + 2.0)
        cv.rbox(gx0, yy, cond_w, rh, "white", C["gated"], lw=0.7, r=0.9, z=2)
        cv.text(gx0 + cond_w / 2, yy + rh / 2, cnd, ha="center")
        cv.arrow([(gx0 + cond_w + 0.5, yy + rh / 2), (gx0 + cond_w + 3.9, yy + rh / 2)])
        face = tint(C["gated"], 0.18) if icon == "check" else ("white" if icon == "cross" else STAGE_FILL)
        cv.rbox(gx0 + cond_w + 4.4, yy, gx1 - gx0 - cond_w - 4.4, rh, face, C["gated"] if icon else STAGE_EDGE,
                lw=0.7, r=0.9, z=2, ls="-" if icon != "cross" else (0, (2.5, 1.5)))
        cv.text(gx0 + cond_w + 6.6, yy + rh / 2, out)
        if icon == "check":
            cv.check(gx1 - 3.0, yy + rh / 2)
        elif icon == "cross":
            cv.cross(gx1 - 3.0, yy + rh / 2)
    oy = ry0 + 3 * (rh + 2.0) + 1.0
    cv.armbox(gx0, oy, gx1 - gx0, 6.0, C["oracle"], r"oracle: $v$ = true label")

    # =============================== (c) contrasts
    cx0 = 127.0
    cv.text(cx0, by, "(c) Contrasts", size=FS_T)
    axx, ay_top, ay_bot = cx0 + 3.6, by + 7.0, by + 42.0
    cv.arrow([(axx, ay_bot), (axx, ay_top)], lw=0.7)
    cv.text(cx0 + 1.3, (ay_top + ay_bot) / 2, "accuracy", rotation=90, ha="center")
    yl, yo, yc = by + 12.0, by + 20.0, by + 38.0
    for key, yy, lab in (("leaky", yl, r"$a_{\mathrm{leaky}}$"), ("oracle", yo, r"$a_{\mathrm{oracle}}$"),
                         ("clean", yc, r"$a_{\mathrm{clean}}$")):
        cv.ax.add_patch(Circle((axx + 2.6, yy), 1.1, facecolor=C[key], edgecolor="white", lw=0.4, zorder=6))
        cv.text(axx + 4.8, yy, lab, size=FS_M)
    b1 = cx0 + 24.0
    cv.bracket(b1, yl, yc)
    cv.text(b1 + 1.6, (yl + yc) / 2, r"$\Delta_{\mathrm{leak}}$", size=FS_M)
    b2 = cx0 + 35.0
    cv.bracket(b2, yl + 0.3, yo - 0.3)
    cv.bracket(b2, yo + 0.3, yc)
    cv.text(b2 + 1.6, (yl + yo) / 2, "not recovered")
    cv.text(b2 + 1.6, (yo + yc) / 2, "recovered by oracle")

    # ---- data record for the supplementary material
    rows_csv = []
    for t in traces:
        rows_csv.append(["trace", SPLIT, SRC, COND[SRC], t["cls"], t["bid"], t["rid"], t["k"], "", "", ""])
    for sp in spectra:
        rows_csv.append(["spectrum", SPLIT, TGT, COND[TGT], sp["bid"], sp["rid"], sp["verdict"],
                         f"{sp['n_same']}/{sp['n_rec']}", ";".join(f"{v:.1f}" for v in sp["peaks"]["BPFO"]),
                         ";".join(f"{v:.1f}" for v in sp["peaks"]["BPFI"]), Z_GATE])
    S.save(cv.fig, "fig1_design", rows_csv,
           ["kind", "split", "condition", "condition_code", "class_or_bearing", "bearing_or_record",
            "record_or_verdict", "windows_or_same_verdict", "bpfo_z_h1_h3", "bpfi_z_h1_h3", "z_gate"])


if __name__ == "__main__":
    build()
