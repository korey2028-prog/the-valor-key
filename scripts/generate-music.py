"""
V3: 浪漫钢琴 ballad 风格 (City of Stars 灵感)

设计哲学:
- 像水流一样的 broken chord arpeggio (不是 walking bass)
- Stepwise singable 旋律 (中音区, 不刺耳)
- Sustained bass pedal (低音根基稳)
- 慢 BPM 42 (浪漫氛围)
- 深 reverb (空间感拉满)
- 柔和 attack (legato, 不机械)

3 层:
1. Bass pedal: 根音长 sustain 整小节
2. Arpeggio: 4 个音/小节,中音区,broken chord 上下波动
3. Melody: 2 个长音/小节 (half note),stepwise motion,可哼

和弦: A maj7 - F#m7 - D maj7 - E7sus4 (jazz voicings, City of Stars 主歌走向)
"""
import wave
import numpy as np
import os
import math

SAMPLE_RATE = 22050
BPM = 42
BEATS_PER_BAR = 4
BARS = 4

SECONDS_PER_BEAT = 60.0 / BPM             # 1.43 秒/拍
SECONDS_PER_BAR = SECONDS_PER_BEAT * 4    # 5.71 秒/小节
TOTAL_SECONDS = SECONDS_PER_BAR * BARS    # 22.86 秒
TOTAL_SAMPLES = int(TOTAL_SECONDS * SAMPLE_RATE)


def piano_note(freq, duration, velocity=0.6, decay_mult=0.7):
    """钢琴音 - inharmonicity + 3 strings + soft attack + multi-rate decay."""
    if duration <= 0:
        return np.array([])
    num_samples = int(duration * SAMPLE_RATE)
    if num_samples <= 0:
        return np.array([])

    t = np.arange(num_samples) / SAMPLE_RATE
    B = 0.0003
    note = np.zeros(num_samples)

    string_detunes = [-0.0025, 0.0, 0.0025]
    string_weights = [0.6, 1.0, 0.6]

    for sd, sw in zip(string_detunes, string_weights):
        f0 = freq * (1 + sd)
        for n in range(1, 9):
            fn = f0 * n * math.sqrt(1 + B * n * n)
            amp = 1.0 / (n ** 1.3)
            decay_rate = (1.0 + n * 0.4) * decay_mult
            decay = np.exp(-t * decay_rate)
            note += np.sin(2 * np.pi * fn * t) * amp * decay * sw

    note *= 0.07 * velocity

    # 更柔和的 attack noise (legato, 不像锤击)
    attack_samples = min(int(0.012 * SAMPLE_RATE), num_samples)
    if attack_samples > 0:
        attack_env = (1 - np.arange(attack_samples) / max(attack_samples, 1)) ** 2.5
        noise = (np.random.rand(attack_samples) - 0.5) * 2 * velocity * 0.025
        note[:attack_samples] += noise * attack_env

    # 全局 envelope - 慢起音(legato)+ 长 release(浪漫)
    if num_samples > 100:
        attack_n = min(int(0.012 * SAMPLE_RATE), num_samples // 4)
        if attack_n > 0:
            note[:attack_n] *= np.linspace(0, 1, attack_n) ** 0.6
        release_n = min(int(0.4 * SAMPLE_RATE), num_samples // 3)
        if release_n > 0:
            note[-release_n:] *= np.linspace(1, 0, release_n) ** 1.5

    return note


def add_note(track, freq, t_start, duration, velocity=0.6, decay_mult=0.7):
    note = piano_note(freq, duration, velocity, decay_mult)
    if len(note) == 0:
        return
    start_idx = int(t_start * SAMPLE_RATE)

    # Handle negative start (from rubato) - skip front of note
    if start_idx < 0:
        note = note[-start_idx:]
        start_idx = 0
        if len(note) == 0:
            return

    if start_idx >= len(track):
        return

    end_idx = min(start_idx + len(note), len(track))
    note_len = end_idx - start_idx
    if note_len <= 0:
        return

    track[start_idx:end_idx] += note[:note_len]


# ====== Music Definition ======

# Bass pedal: 每小节根音,sustained 整小节
bass_pedals = [
    110.00,   # A2 (over A maj7)
    92.50,    # F#2 (over F#m7)
    73.42,    # D2 (over D maj7)
    82.41,    # E2 (over E7sus4)
]

# Arpeggio: 4 个音/小节, broken chord 上下波动(像水流)
arpeggios = [
    [220.00, 277.18, 329.63, 277.18],   # A maj7: A3, C#4, E4, C#4
    [185.00, 220.00, 277.18, 220.00],   # F#m7: F#3, A3, C#4, A3
    [146.83, 185.00, 220.00, 185.00],   # D maj7: D3, F#3, A3, F#3
    [164.81, 220.00, 246.94, 220.00],   # E7sus4: E3, A3, B3, A3
]

# Melody: 2 个长音/小节, stepwise motion (singable)
# 整体走向: E → F# → F# → E → D → F# → G# → A (歌唱感, 像 City of Stars)
melodies = [
    [329.63, 369.99],   # Bar 1 (A maj7): E4 → F#4 (stepwise up)
    [369.99, 329.63],   # Bar 2 (F#m7): F#4 → E4 (stepwise down)
    [293.66, 369.99],   # Bar 3 (D maj7): D4 → F#4 (skip-step up)
    [415.30, 440.00],   # Bar 4 (E7sus4): G#4 → A4 (climax, resolves to A)
]

# ====== Render ======
track = np.zeros(TOTAL_SAMPLES)
np.random.seed(42)

for bar_idx in range(BARS):
    bar_start = bar_idx * SECONDS_PER_BAR

    # === Layer 1: Bass pedal (sustained 整小节, 低音根基) ===
    bass_freq = bass_pedals[bar_idx]
    add_note(track, bass_freq, bar_start, SECONDS_PER_BAR + 0.5,
             velocity=0.45, decay_mult=0.4)

    # === Layer 2: Arpeggio (broken chord, 每拍一个音, 像水流) ===
    arpeggio = arpeggios[bar_idx]
    for beat_idx, af in enumerate(arpeggio):
        beat_start = bar_start + beat_idx * SECONDS_PER_BEAT
        # 长 sustain 让各音重叠,形成 wash 效果
        add_note(track, af, beat_start, SECONDS_PER_BEAT * 1.8,
                 velocity=0.38, decay_mult=0.65)

    # === Layer 3: Melody (2 个长音, stepwise) ===
    melody = melodies[bar_idx]
    for mel_idx, mf in enumerate(melody):
        mel_start = bar_start + mel_idx * SECONDS_PER_BEAT * 2
        # 微微 rubato (人性化)
        mel_start += np.random.uniform(-0.025, 0.025)
        add_note(track, mf, mel_start, SECONDS_PER_BEAT * 2.4,
                 velocity=0.55, decay_mult=0.5)


# ====== Reverb (更深更长, 浪漫空间感) ======
def apply_reverb(track):
    delays_ms = [40, 90, 150, 220, 310, 420, 550]
    gains    = [0.30, 0.25, 0.20, 0.16, 0.12, 0.08, 0.05]

    reverb_out = track.copy()
    for delay_ms, gain in zip(delays_ms, gains):
        delay_samples = int(delay_ms * SAMPLE_RATE / 1000)
        if 0 < delay_samples < len(track):
            delayed = np.zeros_like(track)
            delayed[delay_samples:] = track[:-delay_samples]
            reverb_out += delayed * gain

    return reverb_out

track = apply_reverb(track)


# ====== Soft low-pass ======
window = 4
track = np.convolve(track, np.ones(window) / window, mode='same')


# ====== Normalize ======
peak = np.max(np.abs(track))
if peak > 0:
    track = track / peak * 0.82


# ====== Cross-fade 循环边界 ======
xfade_samples = int(0.08 * SAMPLE_RATE)
if xfade_samples > 0 and len(track) > 2 * xfade_samples:
    track[:xfade_samples] *= np.linspace(0, 1, xfade_samples) ** 0.7
    track[-xfade_samples:] *= np.linspace(1, 0, xfade_samples) ** 0.7


# ====== Write WAV ======
OUTPUT_PATH = "public/audio/city-of-stars-loop.wav"
samples_int = (track * 32767).astype(np.int16)

with wave.open(OUTPUT_PATH, 'wb') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    f.writeframes(samples_int.tobytes())

size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"OK Generated {OUTPUT_PATH}")
print(f"   Duration: {TOTAL_SECONDS:.1f}s | Size: {size_kb:.0f} KB | Tempo: BPM {BPM} | Key: A major")
print(f"   Chords: A maj7 - F#m7 - D maj7 - E7sus4")
print(f"   3 Layers: Bass pedal (sustained) + Arpeggio (water-like) + Melody (stepwise, mid-range)")
print(f"   FX: 7-tap deep reverb, low-pass smoothing, loop cross-fade")
print(f"   Style: Romantic ballad piano, 'City of Stars' inspired verse")
