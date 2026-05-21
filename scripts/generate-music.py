"""
生成 "City of Stars" 风格的钢琴 ambient loop —— V2: 加入真钢琴合成

核心改进(去除"玩具感"):
- 3 根弦每音 detuning(真钢琴特征)
- 8 个 harmonics + inharmonicity(高频不是完美整数倍)
- Attack noise burst(模拟琴锤撞击)
- Multi-rate decay(高频快衰减,低频持续)
- 3 层结构: Walking Bass + Chord Pad + Melody Line
- Jazz 和弦: A maj7 - F#m7 - D maj7 - E7sus4
- 6-tap Reverb 空间感
- Low-pass smoothing 避免刺耳
"""
import wave
import numpy as np
import os
import math

SAMPLE_RATE = 22050
BPM = 50
BEATS_PER_BAR = 4
BARS = 4

SECONDS_PER_BEAT = 60.0 / BPM             # 1.2 秒/拍
SECONDS_PER_BAR = SECONDS_PER_BEAT * 4    # 4.8 秒/小节
TOTAL_SECONDS = SECONDS_PER_BAR * BARS    # 19.2 秒
TOTAL_SAMPLES = int(TOTAL_SECONDS * SAMPLE_RATE)

# ====== Piano Note Synthesis ======
def piano_note(freq, duration, velocity=0.7, decay_mult=1.0):
    """生成一个钢琴音 - inharmonicity + 3 strings + attack noise + multi-rate decay."""
    if duration <= 0:
        return np.array([])

    num_samples = int(duration * SAMPLE_RATE)
    if num_samples <= 0:
        return np.array([])

    t = np.arange(num_samples) / SAMPLE_RATE

    B = 0.0003  # Inharmonicity 系数(典型钢琴中音区)
    note = np.zeros(num_samples)

    # 3 根 detuned "弦"
    string_detunes = [-0.0025, 0.0, 0.0025]
    string_weights = [0.6, 1.0, 0.6]

    for sd, sw in zip(string_detunes, string_weights):
        f0 = freq * (1 + sd)

        # 8 个谐波,真实钢琴 spectrum
        for n in range(1, 9):
            # Inharmonic frequency
            fn = f0 * n * math.sqrt(1 + B * n * n)
            # Harmonic 强度按谐波号衰减
            amp = 1.0 / (n ** 1.3)
            # Multi-rate decay - 高谐波快衰减
            decay_rate = (1.0 + n * 0.4) * decay_mult
            decay = np.exp(-t * decay_rate)

            note += np.sin(2 * np.pi * fn * t) * amp * decay * sw

    note *= 0.07 * velocity

    # Attack noise burst(琴锤撞击)
    attack_samples = min(int(0.008 * SAMPLE_RATE), num_samples)
    if attack_samples > 0:
        attack_env = (1 - np.arange(attack_samples) / max(attack_samples, 1)) ** 2
        noise = (np.random.rand(attack_samples) - 0.5) * 2 * velocity * 0.05
        note[:attack_samples] += noise * attack_env

    # 全局 envelope - 快速 attack, 末尾 fade out 防止 click
    if num_samples > 100:
        attack_n = min(int(0.004 * SAMPLE_RATE), num_samples // 4)
        if attack_n > 0:
            note[:attack_n] *= np.linspace(0, 1, attack_n)
        release_n = min(int(0.15 * SAMPLE_RATE), num_samples // 4)
        if release_n > 0:
            note[-release_n:] *= np.linspace(1, 0, release_n) ** 1.5

    return note


def add_note(track, freq, t_start, duration, velocity=0.7, decay_mult=1.0):
    """把一个钢琴音加到 track 上."""
    note = piano_note(freq, duration, velocity, decay_mult)
    if len(note) == 0:
        return
    start_idx = int(t_start * SAMPLE_RATE)
    end_idx = min(start_idx + len(note), len(track))
    if start_idx >= len(track):
        return
    track[start_idx:end_idx] += note[:end_idx - start_idx]


# ====== Music Definition ======
# Chord voicings: A maj7 → F#m7 → D maj7 → E7sus4 (jazz progression)
chords = [
    [220.00, 277.18, 329.63, 415.30],   # A maj7 (A3, C#4, E4, G#4)
    [185.00, 220.00, 277.18, 329.63],   # F#m7 (F#3, A3, C#4, E4)
    [146.83, 185.00, 220.00, 277.18],   # D maj7 (D3, F#3, A3, C#4)
    [164.81, 220.00, 246.94, 293.66],   # E7sus4 (E3, A3, B3, D4)
]

# Bass walking - 4 个音/小节
bass_walks = [
    [55.00, 82.41, 55.00, 69.30],   # A1 - E2 - A1 - C#2 (over A maj7)
    [46.25, 69.30, 46.25, 55.00],   # F#1 - C#2 - F#1 - A1 (over F#m7)
    [36.71, 55.00, 36.71, 46.25],   # D1 - A1 - D1 - F#1 (over D maj7)
    [41.20, 61.74, 41.20, 51.91],   # E1 - B1 - E1 - G#1 (over E7)
]

# Melody - 2 个音/小节 (each half note)
melodies = [
    [554.37, 659.25],   # C#5 → E5
    [659.25, 554.37],   # E5 → C#5
    [739.99, 880.00],   # F#5 → A5 (climbing)
    [830.61, 987.77],   # G#5 → B5 (climax, then resolve to A on next loop)
]

# ====== Render Track ======
track = np.zeros(TOTAL_SAMPLES)
np.random.seed(42)  # 一致性

for bar_idx in range(BARS):
    bar_start = bar_idx * SECONDS_PER_BAR
    chord_freqs = chords[bar_idx]
    bass_notes = bass_walks[bar_idx]
    melody_notes = melodies[bar_idx]

    # === Chord pad (持续整小节, 柔和) ===
    for cf in chord_freqs:
        add_note(track, cf, bar_start, SECONDS_PER_BAR + 0.4, velocity=0.40, decay_mult=0.55)

    # === Walking bass (每拍一个音) ===
    for beat_idx, bf in enumerate(bass_notes):
        beat_start = bar_start + beat_idx * SECONDS_PER_BEAT
        # 微微 swing 感
        if beat_idx % 2 == 1:
            beat_start += SECONDS_PER_BEAT * 0.04
        add_note(track, bf, beat_start, SECONDS_PER_BEAT * 1.15, velocity=0.55, decay_mult=0.85)

    # === Melody (2 个音/小节, 半拍) ===
    for mel_idx, mf in enumerate(melody_notes):
        mel_start = bar_start + mel_idx * SECONDS_PER_BEAT * 2
        # 轻微 rubato (人性化时间)
        mel_start += np.random.uniform(-0.015, 0.015)
        add_note(track, mf, mel_start, SECONDS_PER_BEAT * 2.2, velocity=0.65, decay_mult=0.7)


# ====== Reverb (6-tap delay) ======
def apply_reverb(track):
    delays_ms = [30, 65, 110, 160, 220, 290]
    gains    = [0.28, 0.22, 0.17, 0.12, 0.08, 0.05]

    reverb_out = track.copy()
    for delay_ms, gain in zip(delays_ms, gains):
        delay_samples = int(delay_ms * SAMPLE_RATE / 1000)
        if 0 < delay_samples < len(track):
            delayed = np.zeros_like(track)
            delayed[delay_samples:] = track[:-delay_samples]
            reverb_out += delayed * gain

    return reverb_out

track = apply_reverb(track)


# ====== Soft low-pass smoothing(避免刺耳)======
window = 3
smoothed = np.convolve(track, np.ones(window) / window, mode='same')
track = smoothed


# ====== Normalize ======
peak = np.max(np.abs(track))
if peak > 0:
    track = track / peak * 0.85  # 留点 headroom


# ====== 让起点和终点 cross-fade,避免 loop click ======
xfade_samples = int(0.05 * SAMPLE_RATE)
if xfade_samples > 0 and len(track) > 2 * xfade_samples:
    fade_in = np.linspace(0, 1, xfade_samples)
    track[:xfade_samples] *= fade_in
    fade_out = np.linspace(1, 0, xfade_samples)
    track[-xfade_samples:] *= fade_out


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
print(f"   Chords: A maj7 - F#m7 - D maj7 - E7sus4 (jazz 7th voicings)")
print(f"   Layers: Walking bass + Chord pad + Melody line")
print(f"   Synth: 3 detuned strings, 8 harmonics with inharmonicity, attack noise, multi-rate decay")
print(f"   FX: 6-tap reverb, low-pass smoothing, loop cross-fade")
