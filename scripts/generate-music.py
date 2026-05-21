"""
生成一段 "City of Stars 风格" 的 ambient piano loop
- 调:A major(City of Stars 主歌 key)
- 和弦进行:A - F#m - D - E(I-vi-IV-V,主歌经典走向)
- Block chord(温暖底层)+ Arpeggio 旋律线(上方钢琴音符)
- 16 秒循环,温暖、舒缓、有 City of Stars 的气质
- 注:这是 "风格相似" 的原创,不是原曲(版权安全)
"""
import wave
import struct
import math
import os

SAMPLE_RATE = 22050
CHORD_SECONDS = 4
SAMPLES_PER_CHORD = SAMPLE_RATE * CHORD_SECONDS

# A major key: A - F#m - D - E
# (City of Stars 主歌经典 I-vi-IV-V 走向)
chord_freqs = [
    [110.00, 138.59, 164.81, 220.00, 277.18],  # A: A2, C#3, E3, A3, C#4
    [92.50,  110.00, 138.59, 185.00, 220.00],  # F#m: F#2, A2, C#3, F#3, A3
    [73.42,  110.00, 146.83, 220.00, 293.66],  # D: D2, A2, D3, A3, D4
    [82.41,  123.47, 164.81, 246.94, 329.63],  # E: E2, B2, E3, B3, E4
]

# 各音符相对音量(根音稍重)
NOTE_WEIGHTS = [0.40, 0.28, 0.22, 0.12, 0.06]

# 上方 arpeggio 旋律(每和弦 4 个音,每个 1 秒)
# 用每个和弦的高音区音符,形成"上行 → 下行"的优雅旋律线
arpeggio_pattern = [
    [440.00, 554.37, 659.25, 554.37],  # A: A4, C#5, E5, C#5
    [440.00, 554.37, 739.99, 554.37],  # F#m: A4, C#5, F#5, C#5
    [587.33, 739.99, 880.00, 739.99],  # D: D5, F#5, A5, F#5
    [659.25, 830.61, 987.77, 830.61],  # E: E5, G#5, B5, G#5
]

OUTPUT_PATH = "public/audio/city-of-stars-loop.wav"

samples = []

for chord_idx, freqs in enumerate(chord_freqs):
    arpeggio = arpeggio_pattern[chord_idx]

    for i in range(SAMPLES_PER_CHORD):
        t = i / SAMPLE_RATE  # 和弦内的相对时间

        # 和弦 envelope - 慢起,丰满,慢落
        if t < 0.6:
            chord_env = (t / 0.6) ** 0.7
        elif t > CHORD_SECONDS - 1.5:
            chord_env = ((CHORD_SECONDS - t) / 1.5) ** 0.6
        else:
            chord_env = 1.0

        # 底层和弦
        chord_sample = 0.0
        for freq, weight in zip(freqs, NOTE_WEIGHTS):
            chord_sample += math.sin(2 * math.pi * freq * t) * weight
            chord_sample += math.sin(2 * math.pi * freq * 2 * t) * weight * 0.25
            # 轻微 detuning - chorus 效果
            chord_sample += math.sin(2 * math.pi * freq * 1.005 * t) * weight * 0.18
        chord_sample *= chord_env * 0.55  # 底层比较轻,留 headroom 给旋律

        # 上方 arpeggio 旋律
        arpeggio_idx = int(t)  # 当前 arpeggio 索引(每秒切换)
        if arpeggio_idx < len(arpeggio):
            arp_freq = arpeggio[arpeggio_idx]
            arp_t = t - arpeggio_idx  # 当前音符内的相对时间

            # 钢琴式 envelope: 短 attack, 指数衰减
            if arp_t < 0.04:
                arp_env = arp_t / 0.04
            else:
                arp_env = math.exp(-(arp_t - 0.04) * 1.8)

            arp_sample = math.sin(2 * math.pi * arp_freq * t) * 0.45
            arp_sample += math.sin(2 * math.pi * arp_freq * 2 * t) * 0.15
            arp_sample += math.sin(2 * math.pi * arp_freq * 3 * t) * 0.05
            chord_sample += arp_sample * arp_env

        # 全局音量
        sample = chord_sample * 0.30
        sample = max(-0.95, min(0.95, sample))
        samples.append(int(sample * 32767))

with wave.open(OUTPUT_PATH, 'wb') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    raw = b''.join(struct.pack('<h', s) for s in samples)
    f.writeframes(raw)

size_kb = os.path.getsize(OUTPUT_PATH) / 1024
print(f"OK Generated {OUTPUT_PATH}")
print(f"   Duration: {len(samples)/SAMPLE_RATE:.1f}s, Size: {size_kb:.0f} KB")
print(f"   Key: A major | Progression: A - F#m - D - E (City of Stars inspired)")
print(f"   Block chord + Arpeggio melody (piano-like envelope)")
