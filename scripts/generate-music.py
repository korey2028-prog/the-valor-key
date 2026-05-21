"""
生成一段温暖的 ambient piano-like WAV 循环
- 16 秒,4 个和弦循环 (Em → D → C → Bm)
- 22050 Hz mono 16-bit (~700 KB)
- 每个音符叠加多个 harmonics + 轻微 detuning 模拟钢琴音色
- ADSR envelope 让每个和弦像钢琴一样起音 → 衰减
"""
import wave
import struct
import math

SAMPLE_RATE = 22050
CHORD_SECONDS = 4
SAMPLES_PER_CHORD = SAMPLE_RATE * CHORD_SECONDS

# 和弦进行: Em → D → C → Bm
# 每个和弦由 5 个音符组成(root + 各种 voicing)
chord_freqs = [
    [82.41, 123.47, 164.81, 246.94, 329.63],  # E2, B2, E3, B3, E4 (Em)
    [73.42, 110.00, 146.83, 220.00, 293.66],  # D2, A2, D3, A3, D4 (D)
    [65.41, 98.00,  130.81, 196.00, 261.63],  # C2, G2, C3, G3, C4 (C)
    [61.74, 92.50,  123.47, 185.00, 246.94],  # B1, F#2, B2, F#3, B3 (Bm)
]

# 每个和弦内各音符的相对音量(根音较重,高音较轻)
NOTE_WEIGHTS = [0.40, 0.28, 0.22, 0.12, 0.06]

OUTPUT_PATH = "public/audio/city-of-stars-loop.wav"

samples = []

for chord_idx, freqs in enumerate(chord_freqs):
    for i in range(SAMPLES_PER_CHORD):
        t = i / SAMPLE_RATE  # 当前秒(在和弦内)

        # ADSR envelope: attack 0.8s 起音, sustain, release 1.5s
        if t < 0.8:
            env = (t / 0.8) ** 0.7
        elif t > CHORD_SECONDS - 1.5:
            env = ((CHORD_SECONDS - t) / 1.5) ** 0.6
        else:
            env = 1.0

        sample = 0.0
        for freq, weight in zip(freqs, NOTE_WEIGHTS):
            # 基音
            sample += math.sin(2 * math.pi * freq * t) * weight
            # 第二谐波(让音色更丰满)
            sample += math.sin(2 * math.pi * freq * 2 * t) * weight * 0.30
            # 第三谐波(增加钢琴特有的明亮感)
            sample += math.sin(2 * math.pi * freq * 3 * t) * weight * 0.12
            # 轻微 detuning - chorus 效果让声音更温暖
            sample += math.sin(2 * math.pi * freq * 1.005 * t) * weight * 0.20

        # 全局音量 + envelope + 防爆音
        sample = sample * env * 0.20
        sample = max(-0.95, min(0.95, sample))
        samples.append(int(sample * 32767))

# 写 WAV 文件
with wave.open(OUTPUT_PATH, 'wb') as f:
    f.setnchannels(1)      # mono
    f.setsampwidth(2)      # 16-bit
    f.setframerate(SAMPLE_RATE)
    # 一次性写所有 frame
    raw = b''.join(struct.pack('<h', s) for s in samples)
    f.writeframes(raw)

import os
size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"OK Generated {OUTPUT_PATH}")
print(f"   Duration: {len(samples)/SAMPLE_RATE:.1f}s, Size: {size_kb:.0f} KB")
