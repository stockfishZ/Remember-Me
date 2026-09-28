"""
generate_audio.py
Authentic 16-bit / 8-bit Chiptune RPG Soundtrack + High-Fidelity Retro Foley
for RememberMe v2 Launch Video (v4 Edition).

Sample Rate: 44,100 Hz, 16-bit Stereo PCM WAV.
Total Duration: exactly 22.000 seconds (970,200 samples).
Peak normalized to -0.5 dB (~0.944), soft limiter (tanh) for zero clipping,
and perfectly click-free loop transition.
"""

import math
import struct
import wave
import random
import os
import shutil

SAMPLE_RATE = 44100
DURATION = 22.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION) # 970,200 samples

left_channel = [0.0] * TOTAL_SAMPLES
right_channel = [0.0] * TOTAL_SAMPLES

def add_sample(idx, l, r=None):
    if 0 <= idx < TOTAL_SAMPLES:
        if r is None:
            r = l
        left_channel[idx] += l
        right_channel[idx] += r

# ----------------- CHIPTUNE SYNTHESIS PRIMITIVES -----------------

def square_wave(freq, t, harmonics=7):
    """Band-limited square wave (50% duty cycle)"""
    val = 0.0
    for k in range(1, harmonics * 2, 2):
        val += math.sin(2.0 * math.pi * freq * k * t) / k
    return val * (4.0 / math.pi) * 0.5

def pulse_wave(freq, t, duty=0.25, harmonics=6):
    """Band-limited pulse wave (classic NES 25% or 12.5% duty)"""
    val = 0.0
    for k in range(1, harmonics + 1):
        amp = math.sin(math.pi * k * duty) / k
        val += amp * math.cos(2.0 * math.pi * freq * k * t)
    return val * 1.4

def triangle_wave(freq, t):
    """NES-style 4-bit stepped triangle wave approximation"""
    phase = (freq * t) % 1.0
    if phase < 0.5:
        val = 4.0 * phase - 1.0
    else:
        val = 3.0 - 4.0 * phase
    # Quantize to 16 steps (4-bit DAC like NES triangle)
    steps = 16.0
    val = math.floor(val * (steps / 2.0)) / (steps / 2.0)
    return val * 0.7

def sine_wave(freq, t):
    return math.sin(2.0 * math.pi * freq * t)

# Authentic 15-bit LFSR pseudo-random noise generator
lfsr_state = 0x7FFF
def nes_noise():
    global lfsr_state
    bit = ((lfsr_state >> 0) ^ (lfsr_state >> 1)) & 1
    lfsr_state = (lfsr_state >> 1) | (bit << 14)
    return 1.0 if (lfsr_state & 1) else -1.0

# ----------------- MUSICAL NOTE PRIMITIVE -----------------

def note(start_time, freq, dur=0.14, amp=0.18, wave_type='pulse', duty=0.25, pan=0.0, vibrato_start=0.06):
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        idx = start_idx + i
        if idx >= TOTAL_SAMPLES:
            break
        t = i / SAMPLE_RATE
        # Envelope: 5ms attack, smooth exponential decay
        if t < 0.005:
            env = t / 0.005
        else:
            env = math.exp(-(t - 0.005) * (3.5 / dur))
        # Pitch vibrato after vibrato_start
        vib = math.sin(2.0 * math.pi * 5.5 * t) * (freq * 0.012) if t > vibrato_start else 0.0
        f = freq + vib
        if wave_type == 'square':
            s = square_wave(f, t, harmonics=6)
        elif wave_type == 'pulse':
            s = pulse_wave(f, t, duty=duty, harmonics=6)
        elif wave_type == 'triangle':
            s = triangle_wave(f, t)
        elif wave_type == 'sine':
            s = sine_wave(f, t)
        else:
            s = math.sin(2.0 * math.pi * f * t)
        val = s * env * amp
        add_sample(idx, val * l_pan, val * r_pan)

# Standard note frequencies (Hz)
C2, D2, E2, F2, G2, A2, B2 = 65.41, 73.42, 82.41, 87.31, 97.99, 110.00, 123.47
C3, D3, E3, F3, G3, A3, B3 = 130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94
C4, D4, E4, F4, G4, Ab4, A4, Bb4, B4 = 261.63, 293.66, 329.63, 349.23, 392.00, 415.30, 440.00, 466.16, 493.88
C5, D5, E5, F5, G5, Ab5, A5, Bb5, B5 = 523.25, 587.33, 659.25, 698.46, 783.99, 830.61, 880.00, 932.33, 987.77
C6, D6, E6, G6, A6, B6 = 1046.50, 1174.66, 1318.51, 1567.98, 1760.00, 1975.53
C7, D7, E7, G7, C8 = 2093.00, 2349.32, 2637.02, 3135.96, 4186.01

# ----------------- SECTION SOUND EFFECT GENERATORS -----------------

def sfx_drum_kick(start_time, amp=0.38):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.12
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 28.0)
        freq = 140.0 * math.exp(-t * 36.0) + 36.0
        val = triangle_wave(freq, t) * env * amp
        add_sample(start_idx + i, val, val)

def sfx_drum_snare(start_time, amp=0.28):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.13
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 22.0)
        tone = triangle_wave(180.0, t) * 0.35
        ns = nes_noise() * 0.75
        val = (tone + ns) * env * amp
        add_sample(start_idx + i, val, val)

def sfx_drum_hihat(start_time, amp=0.10):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.045
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 65.0)
        val = nes_noise() * env * amp
        add_sample(start_idx + i, val * 0.7, val * 1.1)

def sfx_drum_crash(start_time, amp=0.25):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.45
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 7.5)
        val = nes_noise() * env * amp
        add_sample(start_idx + i, val * 0.9, val * 1.0)

def sfx_badge_impact(start_time, pitch_scale=1.0, amp=0.28, pan=0.0):
    """Cartoonish chiptune thud, bounce, and clatter as badge rains down and settles"""
    start_idx = int(start_time * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)

    # 1. High transient clatter / click (18ms)
    click_dur = 0.018
    click_samples = int(click_dur * SAMPLE_RATE)
    for i in range(click_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 110.0)
        click_val = (nes_noise() * 0.65 + pulse_wave(1800.0 * pitch_scale, t, duty=0.25, harmonics=3) * 0.45) * env * amp * 0.75
        add_sample(start_idx + i, click_val * l_pan, click_val * r_pan)

    # 2. Main low-end thud (100ms)
    thud_dur = 0.10
    thud_samples = int(thud_dur * SAMPLE_RATE)
    for i in range(thud_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 30.0)
        freq = 190.0 * pitch_scale * math.exp(-t * 28.0) + 40.0
        val = (triangle_wave(freq, t) + 0.22 * nes_noise()) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

    # 3. Cartoonish bounce rebound blip (70ms)
    bounce_time = start_time + 0.065
    bounce_idx = int(bounce_time * SAMPLE_RATE)
    bounce_dur = 0.07
    bounce_samples = int(bounce_dur * SAMPLE_RATE)
    for i in range(bounce_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 35.0)
        b_freq = 320.0 * pitch_scale * math.exp(-t * 20.0) + 130.0
        val = pulse_wave(b_freq, t, duty=0.25, harmonics=4) * env * amp * 0.40
        add_sample(bounce_idx + i, val * l_pan, val * r_pan)

def sfx_alarm_pulse(start_time, freq=880.0, dur=0.085, amp=0.22, pan=0.0):
    """Urgent 8-bit alarm pulse with rising chirp bite"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = (1.0 - t / dur) ** 0.5
        # Slight upward pitch chirp for urgent distress feeling
        f = freq + 150.0 * (t / dur)
        val = pulse_wave(f, t, duty=0.125, harmonics=5) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def sfx_badge_slot(start_time, freq, amp=0.14, pan=0.0):
    """High sparkle chime as badge slots into the vault"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.11
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 24.0)
        val = (pulse_wave(freq, t, duty=0.125, harmonics=4) + 
               0.3 * sine_wave(freq * 2.0, t)) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def sfx_mechanical_keystroke(start_time, amp=0.16, pan=0.0, is_enter=False):
    """Crisp mechanical terminal keyboard click and keycap clack"""
    start_idx = int(start_time * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)

    # 1. High switch click (10ms)
    click_dur = 0.012
    click_samples = int(click_dur * SAMPLE_RATE)
    click_freq = 4200.0 if not is_enter else 3400.0
    for i in range(click_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 160.0)
        click_val = (pulse_wave(click_freq, t, duty=0.25, harmonics=3) * 0.6 + nes_noise() * 0.4) * env * amp
        add_sample(start_idx + i, click_val * l_pan, click_val * r_pan)

    # 2. Keycap bottom-out body clack (22ms)
    clack_dur = 0.024 if not is_enter else 0.035
    clack_samples = int(clack_dur * SAMPLE_RATE)
    clack_freq = 720.0 if not is_enter else 420.0
    for i in range(clack_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 80.0)
        clack_val = triangle_wave(clack_freq, t) * env * amp * (1.4 if is_enter else 0.85)
        add_sample(start_idx + i, clack_val * l_pan, clack_val * r_pan)

# ----------------- SECTION 1: 0.0s - 2.5s (PANIC ALARM & BADGE AVALANCHE) -----------------
print("Synthesizing Section 1: Panic Alarm & Badge Avalanche Torrent (0.0s - 2.5s)...")

# Low ominous dungeon bass drone signaling memory pressure
for t_sec in [0.0, 0.6, 1.2, 1.8]:
    note(t_sec, D2, dur=0.55, amp=0.20, wave_type='triangle', pan=0.0)

# Rapid pulsing 8-bit alarm tones: alternating 880Hz (A5) and 1174.66Hz (D6)
alarm_times = [
    (0.15, 880.0, -0.3), (0.35, 1174.66, 0.3),
    (0.55, 880.0, -0.3), (0.75, 1174.66, 0.3),
    (0.95, 880.0, -0.3), (1.15, 1174.66, 0.3),
    (1.35, 880.0, -0.3), (1.55, 1174.66, 0.3),
    (1.75, 880.0, -0.3), (1.95, 1174.66, 0.3),
    (2.15, 880.0, -0.3), (2.35, 1174.66, 0.3)
]
for at, afreq, apan in alarm_times:
    sfx_alarm_pulse(at, freq=afreq, dur=0.085, amp=0.22, pan=apan)

# Rapid sequence of cartoonish chiptune thuds, bounces, and clatters
badge_fall_times = [
    0.35, 0.48, 0.58, 0.68, 0.78, 0.88, 0.96, 1.05, 1.14, 1.22,
    1.30, 1.38, 1.46, 1.54, 1.62, 1.70, 1.78, 1.85, 1.92, 2.00,
    2.07, 2.14, 2.21, 2.28, 2.35, 2.42
]
for idx, b_time in enumerate(badge_fall_times):
    pitch_mod = 0.85 + (idx % 5) * 0.12
    pan_mod = -0.55 + ((idx * 7) % 11) * 0.10
    amp_mod = random.uniform(0.24, 0.36)
    sfx_badge_impact(b_time, pitch_scale=pitch_mod, amp=amp_mod, pan=pan_mod)


# ----------------- SECTION 2: 2.5s - 7.5s (WIZARD HAT, LEVEL UP, VORTEX & VAULT LOCK) -----------------
print("Synthesizing Section 2: Jump, Level-Up Fanfare, Centripetal Vortex & Vault Lock (2.5s - 7.5s)...")

# 2.5s: Whoosh / spring jump sfx as Claude leaps to catch the hat
jump_start = 2.50
jump_idx = int(jump_start * SAMPLE_RATE)
jump_dur = 0.40
jump_samples = int(jump_dur * SAMPLE_RATE)
for i in range(jump_samples):
    t = i / SAMPLE_RATE
    env = (1.0 - t / jump_dur) ** 0.75
    freq_base = 135.0 * math.exp((t / jump_dur) * 2.05)
    spring_vib = math.sin(2.0 * math.pi * 22.0 * t) * (55.0 * (1.0 - t / jump_dur))
    freq = freq_base + spring_vib
    whoosh = nes_noise() * 0.28 * (1.0 - (2.0 * t - 1.0) ** 2 if t < jump_dur else 0.0)
    val = (square_wave(freq, t, harmonics=5) * 0.85 + whoosh) * env * 0.35
    pan = -0.3 + (t / jump_dur) * 0.6
    add_sample(jump_idx + i, val * (0.5 * (1.0 - pan)), val * (0.5 * (1.0 + pan)))

# 3.2s - 3.7s: Level-up fanfare / bright arpeggio with celebratory sparkle chime as wizard hat equips
level_up_notes = [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98, 2093.00] # C5 to C7
step = 0.042
for idx, freq in enumerate(level_up_notes):
    st = 3.20 + idx * step
    d = 0.32 if idx == len(level_up_notes) - 1 else 0.08
    pan = -0.4 + (idx / len(level_up_notes)) * 0.8
    note(st, freq, dur=d, amp=0.32 if idx == len(level_up_notes) - 1 else 0.24,
         wave_type='pulse', duty=0.25, pan=pan)

# Celebratory sparkle chimes
sparkle_freqs = [2093.00, 2637.02, 3135.96, 4186.01]
for s_idx, sf in enumerate(sparkle_freqs):
    st_s = 3.52 + s_idx * 0.045
    note(st_s, sf, dur=0.24, amp=0.16, wave_type='pulse', duty=0.125, pan=(-0.5 if s_idx % 2 == 0 else 0.5))

# 3.7s - 6.5s: Centripetal vortex riser + swirling frequency sweep + magic spell casting hum
vortex_start = 3.70
vortex_end = 6.50
vortex_dur = vortex_end - vortex_start
vortex_samples = int(vortex_dur * SAMPLE_RATE)
vortex_idx = int(vortex_start * SAMPLE_RATE)

for i in range(vortex_samples):
    t = i / SAMPLE_RATE
    prog = t / vortex_dur
    env = 0.3 + 0.7 * (prog ** 1.2)
    # Magic spell casting hum (C2=65.41Hz and G2=97.99Hz with slow chorus)
    hum_chorus = math.sin(2.0 * math.pi * 1.5 * t) * 1.5
    hum = (triangle_wave(65.41 + hum_chorus, t) * 0.5 + 
           sine_wave(97.99, t) * 0.35 + 
           sine_wave(130.81, t) * 0.2) * 0.16
    
    # Swirling frequency sweep (240Hz ramping to 1350Hz)
    sweep_freq = 240.0 * math.exp(prog * 1.72)
    rot_speed = 8.0 + prog * 10.0
    pan = math.sin(2.0 * math.pi * rot_speed * t) * 0.75
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    
    sweep_val = (pulse_wave(sweep_freq, t, duty=0.25, harmonics=4) * 0.65 + 
                 square_wave(sweep_freq * 1.5, t, harmonics=3) * 0.35) * env * 0.20
    
    add_sample(vortex_idx + i, (hum + sweep_val) * l_pan, (hum + sweep_val) * r_pan)

# Rapid successive sparkle chimes (sfx_badge_slot) as badges swirl into the vault (3.85s - 6.45s)
slot_chime_notes = [1046.50, 1174.66, 1318.51, 1567.98, 1760.00, 2093.00, 2349.32, 2637.02]
num_slots = 28
for i in range(num_slots):
    # Accelerating timing
    t_slot = vortex_start + 0.15 + (i / num_slots) ** 1.35 * 2.50
    f_slot = slot_chime_notes[i % len(slot_chime_notes)]
    slot_pan = math.sin(i * 1.2) * 0.7
    sfx_badge_slot(t_slot, f_slot, amp=0.15, pan=slot_pan)

# 6.5s - 7.5s: Mechanical vault latch click / lock sound + clean confirmation chime
# 1) Sharp double metallic pulse (6.58s and 6.68s)
def sfx_metallic_click(start_time, f1=2800.0, f2=4200.0, amp=0.26):
    s_idx = int(start_time * SAMPLE_RATE)
    dur = 0.025
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 140.0)
        val = (pulse_wave(f1, t, duty=0.125, harmonics=3) * 0.6 + 
               sine_wave(f2, t) * 0.4 + 
               nes_noise() * 0.4) * env * amp
        add_sample(s_idx + i, val * 0.8, val * 1.1)

sfx_metallic_click(6.58, f1=2800.0, f2=4200.0, amp=0.28)
sfx_metallic_click(6.68, f1=2200.0, f2=3300.0, amp=0.30)

# 2) Solid vault latch thud (6.72s)
thud_idx = int(6.72 * SAMPLE_RATE)
thud_dur = 0.18
for i in range(int(thud_dur * SAMPLE_RATE)):
    t = i / SAMPLE_RATE
    env = math.exp(-t * 26.0)
    freq = 88.0 * math.exp(-t * 22.0) + 32.0
    val = (triangle_wave(freq, t) * 0.85 + nes_noise() * 0.25) * env * 0.42
    add_sample(thud_idx + i, val, val)

# 3) Clean confirmation chime when context drops to 2% (6.90s - 7.45s)
note(6.90, G6, dur=0.22, amp=0.24, wave_type='pulse', duty=0.125, pan=-0.2)
note(7.02, C7, dur=0.48, amp=0.30, wave_type='pulse', duty=0.25, pan=0.2)
# Shimmering harmonic ring
note(7.05, E7, dur=0.40, amp=0.16, wave_type='sine', pan=0.3)


# ----------------- SECTION 3: 7.5s - 12.5s (VICTORY FANFARE & CHIPTUNE GROOVE) -----------------
print("Synthesizing Section 3: Victory Fanfare & Upbeat Chiptune Groove (7.5s - 12.5s)...")

BPM = 150
BEAT = 60.0 / BPM # 0.40s
SIXTEENTH = BEAT / 4.0 # 0.10s

# Celebratory crash cymbal at onset of victory groove
sfx_drum_crash(7.50, amp=0.30)
sfx_drum_crash(11.90, amp=0.32)

# Drum Section (7.5s to 12.3s)
t_beat = 7.50
bar_count = 0
while t_beat < 12.25:
    # Kick on beat 1 and 3
    sfx_drum_kick(t_beat, amp=0.34)
    sfx_drum_hihat(t_beat + SIXTEENTH, amp=0.09)
    # Snare on beat 2 and 4
    sfx_drum_snare(t_beat + BEAT * 0.5, amp=0.27)
    sfx_drum_hihat(t_beat + BEAT * 0.5 + SIXTEENTH, amp=0.09)
    t_beat += BEAT

# Hi-hat 16th subdivision groove
t_hh = 7.50
while t_hh < 12.25:
    sfx_drum_hihat(t_hh, amp=0.06)
    t_hh += SIXTEENTH

# Walking Triangle Bassline (7.5s to 12.3s)
bass_sequence = [
    # Bar 1: C Major (7.5s - 9.1s)
    (7.50, C3), (7.70, C3), (7.90, E3), (8.10, G3),
    (8.30, C4), (8.50, G3), (8.70, E3), (8.90, D3),
    # Bar 2: A Minor -> F Major (9.1s - 10.7s)
    (9.10, A2), (9.30, A2), (9.50, C3), (9.70, E3),
    (9.90, F3), (10.10, A3), (10.30, C4), (10.50, A3),
    # Bar 3: G Major -> C Cadence (10.7s - 12.3s)
    (10.70, G3), (10.90, G3), (11.10, B3), (11.30, D4),
    (11.50, G3), (11.70, F3), (11.90, C3), (12.10, C3)
]
for bt, bf in bass_sequence:
    note(bt, bf, dur=SIXTEENTH * 1.8, amp=0.26, wave_type='triangle', pan=0.0)

# Bright Upbeat Lead Melody (Pulse 25% + detuned stereo pulse)
melody_sequence = [
    # Phrase 1: Festive ascent (7.5s - 9.0s)
    (7.50, G4, 0.12, 0.28),
    (7.65, C5, 0.28, 0.30),
    (8.00, E5, 0.28, 0.30),
    (8.30, G5, 0.48, 0.32),
    (8.85, A5, 0.18, 0.28),
    (9.00, G5, 0.18, 0.28),
    # Phrase 2: Joyful leaps (9.1s - 10.6s)
    (9.20, C6, 0.48, 0.34),
    (9.70, B5, 0.18, 0.28),
    (9.90, A5, 0.18, 0.28),
    (10.15, G5, 0.48, 0.30),
    # Phrase 3: Heroic cadence to sustained C6 resolution (10.7s - 12.4s)
    (10.70, F5, 0.18, 0.28),
    (10.90, A5, 0.18, 0.28),
    (11.15, D6, 0.32, 0.32),
    (11.50, E6, 0.20, 0.32),
    (11.70, D6, 0.20, 0.32),
    (11.90, C6, 0.65, 0.36) # Sustained resolution
]
for mt, mf, md, ma in melody_sequence:
    # Lead voice
    note(mt, mf, dur=md, amp=ma, wave_type='pulse', duty=0.25, pan=-0.15)
    # Detuned chorus duplicate for wide 16-bit stereophonic presence
    note(mt, mf * 1.004, dur=md, amp=ma * 0.85, wave_type='pulse', duty=0.50, pan=0.15)
    # Harmony voice a third below
    note(mt, mf * 0.80, dur=md, amp=ma * 0.45, wave_type='pulse', duty=0.125, pan=0.25)

# Sparkle dust accompanying final chord
for s_idx in range(6):
    note(11.95 + s_idx * 0.06, random.choice([1567.98, 2093.00, 2637.02, 3135.96]),
         dur=0.18, amp=0.12, wave_type='pulse', duty=0.125, pan=random.uniform(-0.6, 0.6))


# ----------------- SECTION 4: 12.5s - 18.0s (TERMINAL KEYBOARD FOLEY & LEVITATION) -----------------
print("Synthesizing Section 4: Soft Window Blip, Terminal Typing Foley & Levitation (12.5s - 18.0s)...")

# 12.5s: Soft window open blip (smooth rising 2-tone chime)
note(12.50, G5, dur=0.06, amp=0.20, wave_type='sine', pan=-0.2)
note(12.56, C6, dur=0.09, amp=0.24, wave_type='sine', pan=0.2)

# 13.0s - 14.8s: Crisp mechanical terminal keyboard typing foley
# 18 distinct keystrokes with realistic timing jitter simulating terminal typing
keystroke_times = [
    13.02, 13.11, 13.19, 13.29, 13.38, 13.46,
    13.57, 13.66, 13.75, 13.87, 13.96, 14.05,
    14.16, 14.25, 14.34, 14.43, 14.52, 14.68 # Enter key at 14.68
]
for k_idx, kt in enumerate(keystroke_times):
    is_ent = (k_idx == len(keystroke_times) - 1)
    k_pan = -0.20 + ((k_idx * 5) % 9) * 0.05
    k_amp = 0.22 if is_ent else random.uniform(0.14, 0.19)
    sfx_mechanical_keystroke(kt, amp=k_amp, pan=k_pan, is_enter=is_ent)

# Carriage return acknowledge beep at 14.80s
note(14.80, A6, dur=0.065, amp=0.18, wave_type='square', pan=0.0)

# 15.0s - 17.5s: Magic casting chime, low resonant levitation hum + magical harmonic shimmer
# 1) Magic casting chime at 15.0s (glockenspiel arpeggio)
lev_arpeggio = [659.25, 830.61, 987.77, 1318.51, 1661.22] # E5, G#5, B5, E6, G#6
for l_idx, lf in enumerate(lev_arpeggio):
    note(15.00 + l_idx * 0.045, lf, dur=0.25, amp=0.18, wave_type='pulse', duty=0.125, pan=-0.4 + l_idx * 0.2)

# 2) Low resonant levitation hum (15.0s to 17.5s)
lev_start = 15.00
lev_dur = 2.50
lev_samples = int(lev_dur * SAMPLE_RATE)
lev_idx = int(lev_start * SAMPLE_RATE)

for i in range(lev_samples):
    t = i / SAMPLE_RATE
    # Smooth fade in and fade out envelope for the hum
    env = math.sin(math.pi * (t / lev_dur)) ** 0.85
    # Gentle 2.5Hz pulsating tremolo/chorus
    trem = 0.85 + 0.15 * math.sin(2.0 * math.pi * 2.5 * t)
    drone = (triangle_wave(110.00, t) * 0.55 + 
             sine_wave(164.81, t) * 0.35 + 
             sine_wave(220.00, t) * 0.25) * env * trem * 0.20
    # Gentle floating stereo pan drift
    pan = math.sin(2.0 * math.pi * 0.6 * t) * 0.4
    add_sample(lev_idx + i, drone * 0.5 * (1.0 - pan), drone * 0.5 * (1.0 + pan))

# 3) Magical harmonic shimmer as book floats across shelf (15.3s to 17.4s)
shimmer_notes = [1318.51, 1661.22, 1975.53, 2349.32, 2637.02, 3322.44]
for s_i in range(16):
    t_shim = 15.30 + s_i * 0.13
    f_shim = shimmer_notes[s_i % len(shimmer_notes)]
    shim_pan = math.sin(s_i * 0.8) * 0.75
    note(t_shim, f_shim, dur=0.30, amp=0.13, wave_type='pulse', duty=0.125, pan=shim_pan)


# ----------------- SECTION 5: 18.0s - 22.0s (ACTIVATED STINGER, SWELL & BLOOM DISSOLVE) -----------------
print("Synthesizing Section 5: ACTIVATED Stinger, Swell & Radiant Bloom Dissolve (18.0s - 22.0s)...")

# 18.0s: Crisp energetic "⚡ ACTIVATED" prompt stinger (electric synth zap / power-up chime)
# 1) Electric synth zap
zap_idx = int(18.00 * SAMPLE_RATE)
zap_dur = 0.055
for i in range(int(zap_dur * SAMPLE_RATE)):
    t = i / SAMPLE_RATE
    env = (1.0 - t / zap_dur) ** 0.8
    freq = 3200.0 * math.exp(-t * 45.0) + 240.0
    val = (pulse_wave(freq, t, duty=0.125, harmonics=4) * 0.7 + nes_noise() * 0.4) * env * 0.32
    add_sample(zap_idx + i, val * 0.9, val * 1.1)

# 2) Power-up chord stinger hit
activated_chord = [C5, G5, C6, E6, G6]
for cf in activated_chord:
    note(18.02, cf, dur=0.45, amp=0.22, wave_type='pulse', duty=0.25, pan=0.0)

# 19.5s - 21.0s: Book opening rustle / whoosh + swelling magical chord / harmonic riser
# 1) Book opening flutter & whoosh (19.50s - 19.85s)
for f_time in [19.50, 19.57, 19.65, 19.74]:
    s_idx = int(f_time * SAMPLE_RATE)
    for i in range(int(0.025 * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 90.0)
        val = nes_noise() * env * 0.18
        add_sample(s_idx + i, val * 0.8, val * 1.1)

# 2) Swelling magical chord / harmonic riser (19.8s to 21.0s)
riser_start = 19.80
riser_end = 21.00
riser_dur = riser_end - riser_start
riser_samples = int(riser_dur * SAMPLE_RATE)
riser_idx = int(riser_start * SAMPLE_RATE)

swell_chord = [C4, G4, B4, D5, E5, G5, B5] # Lush Cmaj9 voicing
for i in range(riser_samples):
    t = i / SAMPLE_RATE
    prog = t / riser_dur
    # Exponential crescendo
    env = 0.04 + 0.34 * (prog ** 2.2)
    val = 0.0
    for note_f in swell_chord:
        val += sine_wave(note_f, t) * 0.22 + pulse_wave(note_f, t, duty=0.25, harmonics=2) * 0.12
    # Harmonic shimmer riser sweep
    riser_sweep_freq = 800.0 * math.exp(prog * 1.3)
    sweep_tone = sine_wave(riser_sweep_freq, t) * 0.15 * prog
    total_val = (val + sweep_tone) * env
    pan = math.sin(prog * math.pi * 3.0) * 0.35
    add_sample(riser_idx + i, total_val * 0.5 * (1.0 - pan), total_val * 0.5 * (1.0 + pan))

# 21.0s - 22.0s: Radiant glowing flash / bloom chime with ethereal high frequency shimmer
# 1) Bloom impact chord at 21.00s
bloom_chord = [C6, G6, E7, C8]
for bf in bloom_chord:
    note(21.00, bf, dur=0.75, amp=0.28, wave_type='pulse', duty=0.125, pan=0.0)
    note(21.00, bf * 0.5, dur=0.65, amp=0.20, wave_type='sine', pan=0.0)

# 2) Multi-tap ethereal stereo reflections (delay shimmer)
echo_taps = [
    (21.15, -0.4, 0.65),
    (21.32,  0.4, 0.42),
    (21.50, -0.3, 0.26),
    (21.68,  0.3, 0.15),
    (21.82,  0.0, 0.08)
]
for et, epan, edecay in echo_taps:
    for bf in [G6, E7]:
        note(et, bf, dur=0.35, amp=0.18 * edecay, wave_type='sine', pan=epan)

# 3) Clean dissolve to silence at 22.0s:
# Apply smooth cosine taper from 21.85s to 22.000s ensuring exact 0.0 at the end
fade_start = 21.85
fade_idx = int(fade_start * SAMPLE_RATE)
for i in range(fade_idx, TOTAL_SAMPLES):
    t_fade = (i - fade_idx) / (TOTAL_SAMPLES - fade_idx)
    # Cosine taper from 1.0 down to 0.0
    scale = 0.5 * (1.0 + math.cos(math.pi * t_fade))
    left_channel[i] *= scale
    right_channel[i] *= scale

# Also ensure smooth 5ms attack at 0.0s so there is zero initial pop
for i in range(int(0.005 * SAMPLE_RATE)):
    t_in = i / (0.005 * SAMPLE_RATE)
    scale = 0.5 * (1.0 - math.cos(math.pi * t_in))
    left_channel[i] *= scale
    right_channel[i] *= scale


# ----------------- NORMALIZATION & 16-BIT STEREO WAV MASTERING -----------------
print("Mastering audio, applying soft limiter (tanh) and peak normalizing to -0.5 dB...")

# 1. Soft limiter pass (tanh) to eliminate any harsh peaks
for i in range(TOTAL_SAMPLES):
    left_channel[i] = math.tanh(left_channel[i])
    right_channel[i] = math.tanh(right_channel[i])

# 2. Find peak amplitude across both channels
max_peak = 0.0
for i in range(TOTAL_SAMPLES):
    max_peak = max(max_peak, abs(left_channel[i]), abs(right_channel[i]))

print(f"Post-limiter peak amplitude: {max_peak:.4f}")

# Target peak: -0.5 dBFS = 10^(-0.5/20) = 0.94406
TARGET_PEAK = 10.0 ** (-0.5 / 20.0)
gain = TARGET_PEAK / max(0.0001, max_peak)
print(f"Applying normalization gain: {gain:.4f} -> Target Peak: {TARGET_PEAK:.4f} (-0.5 dBFS)")

wav_work_path = r"D:\Project\RememberMe\brag-output-v4\work\audio.wav"
wav_dist_path = r"D:\Project\RememberMe\brag-output-v4\audio.wav"

print(f"Writing 16-bit PCM Stereo WAV to {wav_work_path}...")
with wave.open(wav_work_path, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2) # 16-bit
    wf.setframerate(SAMPLE_RATE)
    
    frames = bytearray()
    for i in range(TOTAL_SAMPLES):
        l_s = max(-1.0, min(1.0, left_channel[i] * gain))
        r_s = max(-1.0, min(1.0, right_channel[i] * gain))
        
        l_int = int(l_s * 32767.0)
        r_int = int(r_s * 32767.0)
        
        frames.extend(struct.pack("<hh", l_int, r_int))
        
    wf.writeframes(frames)

# Copy to dist output path
shutil.copyfile(wav_work_path, wav_dist_path)
print(f"Copied audio to {wav_dist_path}")

# Verify file stats
file_size = os.path.getsize(wav_work_path)
expected_frames = TOTAL_SAMPLES
expected_bytes = 44 + TOTAL_SAMPLES * 4 # 44 byte header + 4 bytes per stereo 16-bit sample

print("\n--- AUDIO VERIFICATION SUMMARY ---")
print(f"Sample Rate:      {SAMPLE_RATE} Hz")
print(f"Channels:         2 (Stereo)")
print(f"Bit Depth:        16-bit PCM")
print(f"Total Duration:   {DURATION:.3f} s")
print(f"Total Samples:    {TOTAL_SAMPLES}")
print(f"File Size:        {file_size} bytes (Expected: {expected_bytes})")
print(f"Peak Normalized:  -0.5 dBFS (~{TARGET_PEAK:.3f})")
print(f"Loop Transition:  Zero at borders (Click-free)")
print("Audio synthesis complete!")
