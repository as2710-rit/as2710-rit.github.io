"""Manim scene: Voice Replication (XTTS v2) pipeline explainer.

Render:
    manim -ql voice_pipeline.py VoicePipeline      # draft
    manim -qh voice_pipeline.py VoicePipeline      # production
"""

from manim import *
import numpy as np

BG = "#1C1C1C"
PRIMARY = "#58C4DD"     # cyan
SECONDARY = "#83C167"   # green
ACCENT = "#FFFF00"      # yellow
WARN = "#FF6B6B"
MONO = "Consolas"


def label(text, size=20, color=WHITE, weight=NORMAL):
    return Text(text, font_size=size, color=color, weight=weight, font=MONO)


def caption(text, size=24):
    return label(text, size=size, color=PRIMARY, weight=BOLD)


def waveform(amplitude=0.35, length=4.0, cycles=6, color=PRIMARY,
             noise=0.0, thickness=2.5):
    """A simple sinusoidal waveform with optional wobble."""
    t = np.linspace(0, length, 400)
    y = amplitude * np.sin(2 * PI * cycles * t / length)
    if noise > 0:
        y += noise * np.sin(2 * PI * cycles * 3 * t / length)
    pts = np.c_[t - length / 2, y, np.zeros_like(t)]
    w = VMobject(color=color, stroke_width=thickness)
    w.set_points_as_corners(pts)
    return w


def person_icon(color=WHITE, scale=1.0):
    head = Circle(radius=0.18 * scale, color=color, stroke_width=3)
    body = Arc(radius=0.35 * scale, angle=PI, color=color,
               stroke_width=3).shift(DOWN * 0.35 * scale)
    return VGroup(head, body)


def mic_icon(color=WHITE, scale=1.0):
    cap = RoundedRectangle(width=0.18 * scale, height=0.32 * scale,
                           corner_radius=0.09 * scale,
                           color=color, stroke_width=3)
    stem = Line(UP * 0.0, DOWN * 0.20 * scale, color=color,
                stroke_width=3).shift(DOWN * 0.30 * scale)
    base = Line(LEFT * 0.2 * scale, RIGHT * 0.2 * scale,
                color=color, stroke_width=3).shift(DOWN * 0.50 * scale)
    arc = Arc(radius=0.22 * scale, angle=-PI, color=color,
              stroke_width=3).shift(DOWN * 0.12 * scale)
    return VGroup(cap, arc, stem, base)


def speaker_icon(color=WHITE, scale=1.0):
    box = Polygon(
        [-0.05 * scale, 0.12 * scale, 0],
        [0.18 * scale, 0.25 * scale, 0],
        [0.18 * scale, -0.25 * scale, 0],
        [-0.05 * scale, -0.12 * scale, 0],
        color=color, stroke_width=3,
    )
    wave1 = Arc(radius=0.30 * scale, angle=PI / 3,
                color=color, stroke_width=2).shift(RIGHT * 0.18 * scale)
    wave2 = Arc(radius=0.50 * scale, angle=PI / 3,
                color=color, stroke_width=2).shift(RIGHT * 0.18 * scale)
    return VGroup(box, wave1, wave2)


def lock_icon(color=SECONDARY, scale=1.0):
    body = RoundedRectangle(width=0.4 * scale, height=0.32 * scale,
                            corner_radius=0.05 * scale,
                            color=color, stroke_width=3,
                            fill_opacity=0.15, fill_color=color)
    shackle = Arc(radius=0.16 * scale, angle=PI, color=color,
                  stroke_width=3).shift(UP * 0.16 * scale)
    return VGroup(body, shackle)


# ------------------------------------------------------------


class VoicePipeline(Scene):
    def construct(self):
        self.camera.background_color = BG

        # ---- TITLE ------------------------------------------------------
        title = label("Voice Replication Pipeline",
                      size=44, color=PRIMARY, weight=BOLD)
        subtitle = label("Fine-tuned XTTS v2, gated by speaker verification",
                         size=22, color=GREY_B)
        title.shift(UP * 0.5)
        subtitle.next_to(title, DOWN, buff=0.5)
        self.play(Write(title), run_time=1.4)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(title), FadeOut(subtitle), run_time=0.7)

        # ---- STAGE 1: DATASET PREP -----------------------------------------
        s1 = caption("Stage 1 · Dataset prep")
        s1.to_edge(UP, buff=0.6)
        self.play(Write(s1), run_time=0.8)

        # speaker icon on the left, waves flowing into a folder
        owner = person_icon(color=PRIMARY, scale=1.2).to_edge(LEFT, buff=1.4).shift(UP * 0.4)
        owner_label = label("target\nspeaker", size=16).next_to(owner, DOWN, buff=0.3)
        mic = mic_icon(color=WHITE, scale=1.4).next_to(owner, RIGHT, buff=0.8)

        waves = VGroup(*[
            waveform(amplitude=0.18, length=1.6, cycles=4 + i * 0.5,
                     color=PRIMARY, thickness=2)
            .next_to(mic, RIGHT, buff=0.4).shift(DOWN * i * 0.35)
            for i in range(3)
        ])

        folder_body = RoundedRectangle(width=1.6, height=1.1,
                                       corner_radius=0.12,
                                       color=GREY_B, stroke_width=3,
                                       fill_color=GREY_B, fill_opacity=0.1)
        folder_tab = Polygon([-0.8, 0.55, 0], [-0.4, 0.55, 0],
                             [-0.3, 0.35, 0], [-0.8, 0.35, 0],
                             color=GREY_B, stroke_width=3)
        folder = VGroup(folder_body, folder_tab).to_edge(RIGHT, buff=1.4).shift(UP * 0.4)
        folder_label = label("clean clips\n.wav + transcripts", size=15).next_to(folder, DOWN, buff=0.25)

        arrow_to_folder = Arrow(mic.get_right() + RIGHT * 2.2,
                                folder.get_left() + LEFT * 0.05,
                                color=WHITE, buff=0.15,
                                stroke_width=3,
                                max_tip_length_to_length_ratio=0.18)

        self.play(FadeIn(owner), Write(owner_label), run_time=0.7)
        self.play(FadeIn(mic), run_time=0.5)
        self.play(LaggedStart(*[Create(w) for w in waves], lag_ratio=0.18),
                  run_time=1.6)
        self.play(GrowArrow(arrow_to_folder), run_time=0.7)
        self.play(FadeIn(folder), Write(folder_label), run_time=0.8)

        # checklist
        checks = VGroup(*[
            label(t, size=15, color=SECONDARY) for t in
            ["✓ mono 22.05kHz", "✓ silence-trimmed", "✓ transcripts aligned"]
        ]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        checks.to_edge(DOWN, buff=0.8).shift(LEFT * 4.0)
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2)
                                for c in checks], lag_ratio=0.25),
                  run_time=1.6)
        self.wait(2.0)

        stage1_group = VGroup(owner, owner_label, mic, waves, folder,
                              folder_label, arrow_to_folder, checks)
        self.play(stage1_group.animate.scale(0.5).to_edge(LEFT, buff=0.5).shift(UP * 0.0),
                  run_time=1.0)

        # ---- STAGE 2: XTTS v2 FINE-TUNE ------------------------------------
        s2 = caption("Stage 2 · Fine-tune XTTS v2")
        s2.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(s1, s2), run_time=0.7)

        # GPT block with layers
        gpt = RoundedRectangle(width=3.0, height=2.2, corner_radius=0.15,
                               color=SECONDARY, stroke_width=3,
                               fill_color=SECONDARY, fill_opacity=0.08)
        gpt_label = label("GPT\nsynthesizer", size=20, color=SECONDARY,
                          weight=BOLD).move_to(gpt.get_center())
        enc = RoundedRectangle(width=3.0, height=1.2, corner_radius=0.15,
                               color=PRIMARY, stroke_width=3,
                               fill_color=PRIMARY, fill_opacity=0.08)
        enc_label = label("Speaker encoder", size=18, color=PRIMARY,
                          weight=BOLD).move_to(enc.get_center())

        stack = VGroup(enc, gpt).arrange(DOWN, buff=0.3)
        stack.move_to(ORIGIN).shift(RIGHT * 3.2 + UP * 0.3)
        enc_label.move_to(enc.get_center())
        gpt_label.move_to(gpt.get_center())

        # embedding arrow from speaker encoder to GPT
        embed_arrow = Arrow(enc.get_top() + UP * 0.0,
                            gpt.get_bottom() + DOWN * 0.0,
                            color=WHITE, buff=0.05, stroke_width=3,
                            max_tip_length_to_length_ratio=0.25)
        embed_label = label("speaker\nembedding", size=13,
                            color=GREY_B).next_to(embed_arrow, RIGHT, buff=0.15)

        # "training" bars
        train_bars = VGroup(*[
            Rectangle(width=0.32, height=h, color=PRIMARY,
                      fill_opacity=0.85, stroke_width=0)
            for h in [0.3, 0.55, 0.8, 1.05, 1.2]
        ]).arrange(RIGHT, buff=0.18, aligned_edge=DOWN)
        train_bars.next_to(stack, DOWN, buff=0.45)
        train_label = label("gradient steps",
                            size=14, color=GREY_B).next_to(train_bars, DOWN, buff=0.15)

        self.play(FadeIn(enc), Write(enc_label), run_time=0.8)
        self.play(FadeIn(gpt), Write(gpt_label), run_time=0.8)
        self.play(GrowArrow(embed_arrow), Write(embed_label), run_time=0.7)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in train_bars],
                              lag_ratio=0.12), run_time=1.4)
        self.play(Write(train_label), run_time=0.5)
        self.wait(2.0)

        stage2_group = VGroup(stack, enc_label, gpt_label,
                              embed_arrow, embed_label,
                              train_bars, train_label)
        self.play(FadeOut(stage1_group), run_time=0.6)
        self.play(stage2_group.animate.scale(0.78).shift(LEFT * 1.2),
                  run_time=1.0)

        # ---- STAGE 3: SPEAKER VERIFICATION --------------------------------
        s3 = caption("Stage 3 · Speaker-verification gate")
        s3.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(s2, s3), run_time=0.7)

        # incoming voice on the right
        requester = person_icon(color=WARN, scale=1.2).to_edge(RIGHT, buff=0.8).shift(UP * 0.4)
        req_label = label("incoming\nrequester", size=16).next_to(requester, DOWN, buff=0.3)
        req_wave = waveform(amplitude=0.25, length=1.4, cycles=4, color=WARN)
        req_wave.next_to(requester, LEFT, buff=0.25)

        # d-vector chip in the middle
        dv_box = RoundedRectangle(width=1.8, height=1.0,
                                  corner_radius=0.1, color=ACCENT,
                                  stroke_width=3,
                                  fill_color=ACCENT, fill_opacity=0.08)
        dv_label = label("MFCC\nd-vector", size=17, color=ACCENT,
                         weight=BOLD).move_to(dv_box.get_center())
        dv_box.move_to(ORIGIN).shift(DOWN * 0.3 + RIGHT * 1.2)

        # cosine similarity bar
        sim_bar_bg = Rectangle(width=2.4, height=0.3, color=GREY_B,
                               stroke_width=2, fill_opacity=0.2,
                               fill_color=GREY_B)
        sim_bar_bg.move_to(dv_box.get_center() + DOWN * 1.9)
        sim_bar_fill = Rectangle(width=2.3, height=0.24, color=SECONDARY,
                                 fill_opacity=0.85, stroke_width=0)
        sim_bar_fill.move_to(sim_bar_bg, aligned_edge=LEFT).shift(RIGHT * 0.025)
        sim_label = label("cosine similarity  ≥  θ", size=14,
                          color=SECONDARY).next_to(sim_bar_bg, LEFT, buff=0.2)

        # lock at output
        lock = lock_icon(color=SECONDARY, scale=1.4).to_edge(LEFT, buff=1.0).shift(DOWN * 0.4)
        lock_label = label("allow synthesis\n(owner verified)", size=15,
                           color=SECONDARY).next_to(lock, DOWN, buff=0.25)

        self.play(FadeIn(requester), Write(req_label), FadeIn(req_wave),
                  run_time=0.8)
        self.play(GrowFromCenter(dv_box), Write(dv_label), run_time=0.8)
        self.play(Create(sim_bar_bg), run_time=0.5)
        self.play(GrowFromEdge(sim_bar_fill, LEFT), Write(sim_label),
                  run_time=1.0)
        self.play(FadeIn(lock), Write(lock_label), run_time=0.8)
        self.wait(2.4)

        # denied flash (different voice gets rejected) — quick beat
        deny_text = label("mismatch → deny", size=15, color=WARN,
                          weight=BOLD).next_to(sim_bar_bg, DOWN, buff=0.2)
        deny_fill = Rectangle(width=0.7, height=0.24, color=WARN,
                              fill_opacity=0.85, stroke_width=0)
        deny_fill.move_to(sim_bar_bg, aligned_edge=LEFT).shift(RIGHT * 0.025)
        self.play(ReplacementTransform(sim_bar_fill, deny_fill),
                  FadeIn(deny_text), run_time=0.8)
        self.wait(0.7)
        # back to accepted
        ok_fill = Rectangle(width=2.3, height=0.24, color=SECONDARY,
                            fill_opacity=0.85, stroke_width=0)
        ok_fill.move_to(sim_bar_bg, aligned_edge=LEFT).shift(RIGHT * 0.025)
        self.play(ReplacementTransform(deny_fill, ok_fill),
                  FadeOut(deny_text), run_time=0.8)
        sim_bar_fill = ok_fill
        self.wait(0.5)

        # ---- STAGE 4: WHISPER GROUNDING -----------------------------------
        s4 = caption("Stage 4 · Whisper grounding")
        s4.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(s3, s4), run_time=0.7)

        whisper_box = RoundedRectangle(width=2.4, height=1.1,
                                       corner_radius=0.12,
                                       color=PRIMARY, stroke_width=3,
                                       fill_color=PRIMARY, fill_opacity=0.08)
        whisper_label = label("Whisper\nASR", size=20, color=PRIMARY,
                              weight=BOLD).move_to(whisper_box.get_center())
        whisper_box.move_to(ORIGIN).shift(UP * 0.1)

        transcript = label("\"clone my voice\nfor this demo\"", size=17,
                           color=WHITE).next_to(whisper_box, RIGHT, buff=0.7)
        quote_mark = label("\\[", size=40, color=GREY_B).next_to(
            transcript, LEFT, buff=0.0).scale(0.01)  # spacer, removed later
        quote_mark.set_opacity(0)

        self.play(FadeIn(whisper_box), Write(whisper_label), run_time=0.8)
        self.play(Write(transcript), FadeIn(quote_mark), run_time=0.9)

        ground_note = label("every request stays text-tractable & auditable",
                            size=14, color=GREY_B).to_edge(DOWN, buff=1.0)
        self.play(Write(ground_note), run_time=0.7)
        self.wait(1.6)

        stage3to4_group = VGroup(requester, req_label, req_wave,
                                 dv_box, dv_label,
                                 sim_bar_bg, sim_bar_fill, sim_label,
                                 lock, lock_label,
                                 whisper_box, whisper_label, transcript,
                                 ground_note)
        self.play(FadeOut(stage3to4_group), FadeOut(stage2_group),
                  run_time=0.9)

        # ---- STAGE 5: SYNTHESIS + SERVING --------------------------------
        s5 = caption("Stage 5 · Synthesis & serving")
        s5.to_edge(UP, buff=0.6)
        self.play(ReplacementTransform(s4, s5), run_time=0.7)

        # central chip = fine-tuned XTTS
        chip = RoundedRectangle(width=3.4, height=1.4, corner_radius=0.15,
                                color=SECONDARY, stroke_width=3,
                                fill_color=SECONDARY, fill_opacity=0.1)
        chip_label = label("XTTS v2\n(fine-tuned)", size=20,
                           color=SECONDARY, weight=BOLD).move_to(chip.get_center())
        chip.move_to(ORIGIN)

        # input arrows + labels
        inbox_text = label("text", size=15, color=GREY_B)
        inbox_embedding = label("speaker\nembedding", size=15, color=GREY_B)
        a1 = Arrow(LEFT * 0.6, RIGHT * 0.0, color=PRIMARY, stroke_width=3,
                   buff=0.05, max_tip_length_to_length_ratio=0.35)
        a1.next_to(chip, LEFT, buff=0.15).shift(UP * 0.35)
        inbox_text.next_to(a1, LEFT, buff=0.25)
        a2 = Arrow(LEFT * 0.6, RIGHT * 0.0, color=ACCENT, stroke_width=3,
                   buff=0.05, max_tip_length_to_length_ratio=0.35)
        a2.next_to(chip, LEFT, buff=0.15).shift(DOWN * 0.35)
        inbox_embedding.next_to(a2, LEFT, buff=0.25)

        # output waveform + speaker
        out_wave = waveform(amplitude=0.4, length=1.8, cycles=5,
                            color=SECONDARY, thickness=3)
        out_wave.next_to(chip, RIGHT, buff=0.4).shift(UP * 0.1)
        spk = speaker_icon(color=SECONDARY, scale=1.5)
        spk.next_to(out_wave, RIGHT, buff=0.35)
        # caption under waveform-and-speaker pair, centered on the pair
        out_label = label("cloned voice", size=16, color=SECONDARY)
        pair_group = VGroup(out_wave, spk)
        out_label.next_to(pair_group, DOWN, buff=0.25)

        # GPU footer
        gpu = label("▶ RTX-class GPU · realtime inference",
                    size=15, color=GREY_B).to_edge(DOWN, buff=0.8)

        self.play(FadeIn(chip), Write(chip_label), run_time=0.8)
        self.play(GrowArrow(a1), GrowArrow(a2),
                  FadeIn(inbox_text), FadeIn(inbox_embedding), run_time=0.9)
        self.play(Create(out_wave), FadeIn(spk), Write(out_label),
                  run_time=1.2)
        self.play(Write(gpu), run_time=0.6)
        self.wait(2.5)

        # ---- finale --------------------------------------------------------
        fin = label("Verified voice → fine-tuned clone → gated output",
                    size=24, color=PRIMARY, weight=BOLD)
        fin.to_edge(DOWN, buff=1.0)
        fin.set_opacity(0)
        self.play(FadeOut(VGroup(chip, chip_label, a1, a2,
                                 inbox_text, inbox_embedding,
                                 out_wave, spk, out_label, gpu)), run_time=0.7)
        self.play(fin.animate.set_opacity(1).shift(UP * 1.4), run_time=1.0)
        self.wait(3.0)

        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=0.8)
        self.wait(0.5)
