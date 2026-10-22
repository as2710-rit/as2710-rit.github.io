"""Manim scene: MI-EEG classification pipeline explainer.

Render:
    manim -ql mi_eeg_pipeline.py MI_EEGPipeline      # draft (480p15)
    manim -qh mi_eeg_pipeline.py MI_EEGPipeline      # production (1080p60)
"""

from manim import *
import numpy as np

BG = "#1C1C1C"
PRIMARY = "#58C4DD"     # cyan
SECONDARY = "#83C167"   # green
ACCENT = "#FFFF00"      # yellow
WARN = "#FF6B6B"
MONO = "Consolas"


# ------------------------------------------------- helpers

def label(text, size=20, color=WHITE, weight=NORMAL):
    return Text(text, font_size=size, color=color, weight=weight, font=MONO)


def caption(text, size=24):
    return label(text, size=size, color=PRIMARY, weight=BOLD)


def electrodes_positions():
    """Standard 10-20 labels we care about, mapped to a head outline."""
    return {
        "Fz":  ( 0.0,  1.6), "Cz":  ( 0.0,  0.0), "Pz": ( 0.0, -1.6),
        "C3":  (-1.3,  0.0), "C4":  ( 1.3,  0.0),
        "FC3": (-1.0,  0.8), "FC4": ( 1.0,  0.8),
        "CP3": (-1.0, -0.8), "CP4": ( 1.0, -0.8),
        "P3":  (-1.3, -1.6), "P4":  ( 1.3, -1.6),
        "F3":  (-1.3,  1.6), "F4":  ( 1.3,  1.6),
    }


def make_head_with_electrodes(scale=1.0, color=PRIMARY):
    head = VGroup()
    circle = Circle(radius=2.1 * scale, color=GREY_B, stroke_width=3)
    nose = Polygon([-0.15, 2.0 * scale, 0],
                   [0.15, 2.0 * scale, 0],
                   [0.0, 2.3 * scale, 0],
                   color=GREY_B, stroke_width=3)
    head.add(circle, nose)

    dots = VGroup()
    labels = VGroup()
    for name, (x, y) in electrodes_positions().items():
        d = Dot(point=[x * scale, y * scale, 0], radius=0.07 * scale,
                color=color)
        t = label(name, size=10).scale(scale)
        t.next_to(d, UP * 0.6 + RIGHT * 0.2, buff=0.04)
        dots.add(d)
        labels.add(t)
    head.add(dots, labels)
    return head, dots, labels


# ------------------------------------------------- scene


class MI_EEGPipeline(Scene):
    def construct(self):
        self.camera.background_color = BG

        # ---- TITLE --------------------------------------------------------
        title = label("Motor-Imagery EEG Classification",
                      size=44, color=PRIMARY, weight=BOLD)
        subtitle = label("From raw scalp recordings to decoded intent",
                         size=22, color=GREY_B)
        title.shift(UP * 0.5)
        subtitle.next_to(title, DOWN, buff=0.5)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.7)

        # ---- STAGE 1: PARTICIPANTS / UNIPOLAR ------------------------------
        stage1 = caption("Stage 1 · Raw unipolar EEG")
        stage1.to_edge(UP, buff=0.6)
        self.play(Write(stage1), run_time=1.0)

        head, dots, labels_ = make_head_with_electrodes()
        head.move_to(ORIGIN)
        self.play(FadeIn(head, scale=0.9), run_time=1.2)
        self.wait(0.6)

        # show wavy traces floating near the head
        traces = VGroup()
        for i, (name, (x, y)) in enumerate(
                list(electrodes_positions().items())[:4]):
            t = np.linspace(0, 2 * PI, 240)
            amp = 0.18 + 0.05 * i
            xs = t * 0.35 + x * 1.4  # horizontal offset per channel
            ys = np.sin(3 * t + i) * amp + y * 0.95 + 3.4
            pts = np.c_[xs, ys, np.zeros_like(xs)]
            wave = VMobject(color=PRIMARY, stroke_width=2)
            wave.set_points_as_corners(pts)
            traces.add(wave)
        traces.shift(LEFT * 0.2)
        self.play(LaggedStart(*[Create(tr) for tr in traces],
                              lag_ratio=0.15), run_time=2.0)
        self.wait(1.2)
        self.play(FadeOut(traces), run_time=0.6)
        self.wait(0.5)

        # ---- STAGE 2: BIPOLAR CONVERSION -----------------------------------
        stage2 = caption("Stage 2 · Unipolar → bipolar")
        stage2.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(stage1, stage2), run_time=0.7)

        # highlight a bipolar pair
        dot_map = {name: d for (name, _), d in
                   zip(electrodes_positions().items(), dots)}
        pair_a = dot_map["C3"]
        pair_b = dot_map["Cz"]
        ring_a = Circle(radius=0.22, color=ACCENT,
                        stroke_width=3).move_to(pair_a)
        ring_b = Circle(radius=0.22, color=ACCENT,
                        stroke_width=3).move_to(pair_b)
        line = Line(pair_a.get_center(), pair_b.get_center(),
                    color=ACCENT, stroke_width=4)
        minus = label("−", size=36, color=ACCENT,
                      weight=BOLD).move_to(
            (pair_a.get_center() + pair_b.get_center()) / 2 + UP * 0.32)
        eq = label("C3 − Cz", size=22, color=ACCENT,
                   weight=BOLD).to_edge(DOWN, buff=0.7)
        self.play(FadeIn(ring_a), FadeIn(ring_b), run_time=0.8)
        self.play(Create(line), Write(minus), run_time=0.8)
        self.play(Write(eq), run_time=0.8)
        self.wait(2.0)

        # pack up electrodes and head
        head_group = VGroup(head, ring_a, ring_b, line, minus, eq)
        self.play(head_group.animate.scale(0.55).to_edge(LEFT, buff=0.6),
                  stage2.animate.shift(UP * 0.0), run_time=1.2)
        self.wait(0.5)

        # ---- STAGE 3: PSD --------------------------------------------------
        stage3 = caption("Stage 3 · PSD per bipolar pair")
        stage3.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(stage2, stage3), run_time=0.7)

        # axes for PSD curve
        ax = Axes(
            x_range=[0, 7, 1], y_range=[0, 1, 0.5],
            x_length=5.6, y_length=3.2,
            tips=False,
            axis_config={"color": GREY_B, "stroke_width": 2},
        ).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.1)
        bands = ["δ", "θ", "α", "β1", "β2", "γ1", "γ2"]
        band_labels = VGroup(*[
            label(b, size=14).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.2)
            for i, b in enumerate(bands)
        ])
        y_label = label("power", size=14, color=GREY_B)
        y_label.next_to(ax, UP, buff=0.2)
        random_psd = [0.65, 0.40, 0.90, 0.55, 0.35, 0.22, 0.15]
        bars = VGroup(*[
            Rectangle(width=0.55, height=v * 3.2,
                      fill_opacity=0.85, stroke_width=0,
                      color=PRIMARY if i == 2 else GREY_B)
            .move_to(ax.c2p(i + 0.5, 0), aligned_edge=DOWN)
            for i, v in enumerate(random_psd)
        ])
        psd_title = label("7 frequency bands",
                          size=18, color=GREY_B).next_to(ax, UP, buff=0.6)
        self.play(Create(ax), Write(y_label), FadeIn(psd_title), run_time=1.0)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.1), run_time=2.0)
        self.play(FadeIn(band_labels), run_time=0.8)
        self.wait(2.0)

        # highlight alpha band
        band_hi = SurroundingRectangle(bars[2], color=ACCENT,
                                       buff=0.08, stroke_width=3)
        alpha_note = label("sensorimotor rhythms", size=16,
                           color=ACCENT).next_to(band_hi, UP, buff=0.3)
        self.play(Create(band_hi), Write(alpha_note), run_time=0.9)
        self.wait(1.4)

        # pack up PSD
        psd_group = VGroup(ax, band_labels, y_label, psd_title,
                           bars, band_hi, alpha_note)
        self.play(psd_group.animate.scale(0.55).to_edge(RIGHT, buff=0.6),
                  run_time=1.2)
        self.wait(0.4)

        # ---- STAGE 4: TOP-10 CHANNEL PAIR SELECTION ------------------------
        stage4 = caption("Stage 4 · Select top 10 channel pairs")
        stage4.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(stage3, stage4), run_time=0.7)

        # show a "list" of pairs, top 10 highlighted
        all_pairs = [
            "C3 − Cz", "C4 − Cz", "FC3 − FCz", "FC4 − FCz",
            "CP3 − CPz", "CP4 − CPz", "C3 − FC3", "C4 − FC4",
            "C3 − CP3", "C4 − CP4",
            "F3 − Fz", "F4 − Fz", "P3 − Pz", "P4 − Pz",
            "Fz − Cz", "Cz − Pz",
        ]
        items = VGroup(*[label(p, size=15) for p in all_pairs])
        items.arrange_in_grid(rows=8, cols=2, buff=0.28)
        items.move_to(ORIGIN).shift(DOWN * 0.2)

        rects = VGroup(*[
            SurroundingRectangle(items[i], color=(
                SECONDARY if i < 10 else GREY_C),
                buff=0.10, stroke_width=3 if i < 10 else 1.5,
                corner_radius=0.06)
            for i in range(len(all_pairs))
        ])
        # dim bottom 6 (the pruned pairs)
        for i in range(10, len(all_pairs)):
            items[i].set_opacity(0.35)

        top_label = label("top 10 kept", size=18,
                          color=SECONDARY, weight=BOLD)
        top_label.to_edge(UP, buff=1.4).shift(RIGHT * 4.0)
        arrow_top = Arrow(start=top_label.get_left() + DOWN * 0.2,
                          end=rects[0].get_top() + UP * 0.1,
                          color=SECONDARY, buff=0.1,
                          stroke_width=3, max_tip_length_to_length_ratio=0.15)

        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1)
                                for r in items], lag_ratio=0.04),
                  run_time=1.6)
        self.play(LaggedStart(*[Create(r) for r in rects[:10]],
                              lag_ratio=0.05), run_time=1.4)
        self.play(Write(top_label), GrowArrow(arrow_top), run_time=0.8)
        self.wait(2.0)

        pick = VGroup(items, rects, top_label, arrow_top)
        self.play(FadeOut(pick), FadeOut(psd_group), FadeOut(head_group),
                  run_time=0.9)

        # ---- STAGE 5: WAVELET FEATURES -------------------------------------
        stage5 = caption("Stage 5 · Wavelet feature extraction")
        stage5.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(stage4, stage5), run_time=0.7)

        # left: input signal, right: multi-scale wavelet atoms
        sig_axes = Axes(x_range=[0, 4, 1], y_range=[-1.5, 1.5, 1],
                        x_length=5.0, y_length=2.4,
                        tips=False,
                        axis_config={"color": GREY_B, "stroke_width": 2})
        sig_axes.to_edge(LEFT, buff=0.8).shift(UP * 0.3)
        t = np.linspace(0, 4, 400)
        sig_pts = np.c_[ax.x_axis.n2p(0)[0] * 0 + t * 1.2 - 2.0,
                        (np.sin(2 * PI * 3 * t) * np.exp(-((t - 2) ** 2) / 0.8)
                         + 0.2 * np.sin(2 * PI * 12 * t)) * 0.9,
                        np.zeros_like(t)]
        signal = VMobject(color=PRIMARY, stroke_width=2.5)
        signal.set_points_as_corners(sig_pts)
        signal.move_to(sig_axes.get_center())
        sig_title = label("bipolar signal", size=16,
                          color=GREY_B).next_to(sig_axes, UP, buff=0.2)

        # wavelet atoms at different scales (right side)
        wt_axes = Axes(x_range=[0, 2 * PI, 1], y_range=[-1.2, 1.2, 1],
                       x_length=5.0, y_length=2.4,
                       tips=False,
                       axis_config={"color": GREY_B, "stroke_width": 2})
        wt_axes.to_edge(RIGHT, buff=0.8).shift(UP * 0.3)

        wt_atoms = []
        scale_offsets = [(0.0, 0.5), (0.3, 0.0), (-0.3, -0.5)]
        for i, (dx, dy) in enumerate(scale_offsets):
            tfine = np.linspace(-3, 3, 240)
            psi = (1 - (tfine ** 2)) * np.exp(-(tfine ** 2) / 2)  # Ricker
            stretch = 0.6 + 0.4 * i
            pts = np.c_[tfine * 0.35 * stretch + dx,
                        psi * 0.5 + dy,
                        np.zeros_like(tfine)]
            atom = VMobject(color=(ACCENT if i == 0 else SECONDARY),
                            stroke_width=2.5)
            atom.set_points_as_corners(pts)
            atom.move_to(wt_axes.get_center() + RIGHT * dx * 4 + UP * dy * 4)
            wt_atoms.append(atom)
        wt_title = label("wavelet atoms (multi-scale)", size=16,
                         color=GREY_B).next_to(wt_axes, UP, buff=0.2)

        arrow_wave = Arrow(sig_axes.get_right() + RIGHT * 0.15,
                           wt_axes.get_left() + LEFT * 0.15,
                           color=WHITE, buff=0.05,
                           stroke_width=3,
                           max_tip_length_to_length_ratio=0.18)
        arrow_lbl = label("DWT", size=18, color=WHITE,
                          weight=BOLD).next_to(arrow_wave, UP, buff=0.15)

        self.play(Create(sig_axes), Write(sig_title), run_time=0.8)
        self.play(Create(signal), run_time=1.4)
        self.play(GrowArrow(arrow_wave), Write(arrow_lbl), run_time=0.7)
        self.play(Create(wt_axes), Write(wt_title), run_time=0.7)
        self.play(LaggedStart(*[Create(a) for a in wt_atoms],
                              lag_ratio=0.2), run_time=1.8)
        self.wait(1.2)

        # feature chips
        chips = VGroup(*[
            label(f, size=15, color=PRIMARY) for f in
            ["mean |cA|", "std |cD3|", "energy cA",
             "energy cD1..D3", "band ratios", "…"]
        ])
        chips.arrange(RIGHT, buff=0.5).to_edge(DOWN, buff=0.7)
        feat_label = label("feature vector", size=16,
                           color=GREY_B).next_to(chips, UP, buff=0.15)
        self.play(Write(feat_label), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1)
                                for c in chips], lag_ratio=0.12),
                  run_time=1.6)
        self.wait(2.0)

        wave_group = VGroup(sig_axes, sig_title, signal,
                            wt_axes, wt_title, arrow_wave, arrow_lbl,
                            chips, feat_label, *wt_atoms)
        self.play(FadeOut(wave_group), run_time=0.9)

        # ---- STAGE 6: XGBOOST CLASSIFIER -----------------------------------
        stage6 = caption("Stage 6 · XGBoost classifier (subject-specific)")
        stage6.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(stage5, stage6), run_time=0.7)

        # draw little decision trees
        trees = VGroup()

        def make_tree(color):
            root = Dot(radius=0.10, color=color)
            left = Dot(radius=0.08, color=color).shift(DL * 0.7)
            right = Dot(radius=0.08, color=color).shift(DR * 0.7)
            ll = Dot(radius=0.07, color=color).shift(DL * 0.7 + DL * 0.55)
            lr = Dot(radius=0.07, color=color).shift(DL * 0.7 + DR * 0.55)
            rl = Dot(radius=0.07, color=color).shift(DR * 0.7 + DL * 0.55)
            rr = Dot(radius=0.07, color=color).shift(DR * 0.7 + DR * 0.55)
            edges = VGroup(
                Line(root, left, color=color, stroke_width=2),
                Line(root, right, color=color, stroke_width=2),
                Line(left, ll, color=color, stroke_width=2),
                Line(left, lr, color=color, stroke_width=2),
                Line(right, rl, color=color, stroke_width=2),
                Line(right, rr, color=color, stroke_width=2),
            )
            return VGroup(edges, root, left, right, ll, lr, rl, rr)

        for i, col in enumerate([PRIMARY, SECONDARY, ACCENT]):
            t = make_tree(col).scale(0.9)
            t.shift(LEFT * 4.5 + RIGHT * i * 3.5 + UP * 0.9)
            trees.add(t)

        self.play(LaggedStart(*[FadeIn(t, scale=0.8)
                                for t in trees], lag_ratio=0.2),
                  run_time=1.8)

        # "+" between trees
        plus_group = VGroup()
        for i in range(len(trees) - 1):
            plus = label("+", size=36, color=WHITE, weight=BOLD)
            plus.move_to((trees[i].get_center() +
                          trees[i + 1].get_center()) / 2)
            plus_group.add(plus)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5)
                                for p in plus_group], lag_ratio=0.1),
                  run_time=0.8)

        boost_lbl = label("boosted ensemble — trees vote together",
                          size=18, color=GREY_B)
        boost_lbl.next_to(trees, DOWN, buff=0.5)
        self.play(Write(boost_lbl), run_time=0.7)
        self.wait(0.8)

        # final output: 4-class MI labels
        out_labels = VGroup(*[
            label(s, size=22, color=WHITE, weight=BOLD) for s in
            ["left hand", "right hand", "feet", "tongue"]
        ])
        out_labels.arrange(RIGHT, buff=0.7).to_edge(DOWN, buff=0.6)

        arrow_out = Arrow(trees.get_bottom() + DOWN * 0.2,
                          out_labels.get_top() + UP * 0.2,
                          color=WHITE, buff=0.1,
                          stroke_width=3,
                          max_tip_length_to_length_ratio=0.15)

        self.play(FadeOut(plus_group), FadeOut(boost_lbl),
                  GrowArrow(arrow_out), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.15)
                                for l in out_labels], lag_ratio=0.12),
                  run_time=1.6)
        self.wait(2.2)

        # ---- finale ---------------------------------------------------------
        fin = label("End to end:  raw EEG  →  decoded intent",
                    size=26, color=PRIMARY, weight=BOLD)
        fin.to_edge(DOWN, buff=1.0)
        fin.set_opacity(0)
        self.play(FadeOut(trees), FadeOut(arrow_out), FadeOut(out_labels),
                  run_time=0.7)
        self.play(fin.animate.set_opacity(1).shift(UP * 1.4), run_time=1.0)
        self.wait(3.0)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
        self.wait(0.5)
