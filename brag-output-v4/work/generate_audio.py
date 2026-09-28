"""
generate_audio.py
Authentic 16-bit / 8-bit Chiptune RPG Soundtrack + High-Fidelity Retro Foley
for RememberMe v2 Launch Video (18.0s / 1,080 Frames Edition).

Sample Rate: 44,100 Hz, 16-bit Stereo PCM WAV.
Total Duration: exactly 18.000 seconds (793,800 samples).
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
DURATION = 18.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION) # 793,800 samples

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
        freq = 150.0 * math.exp(-t * 38.0) + 38.0
        env = (1.0 - t / dur) ** 2.2
        val = triangle_wave(freq, t) * env * amp
        add_sample(start_idx + i, val, val)

def sfx_drum_snare(start_time, amp=0.28):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.11
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env_body = math.exp(-t * 35.0)
        env_noise = math.exp(-t * 22.0)
        body = triangle_wave(185.0 * math.exp(-t * 18.0), t) * env_body * 0.45
        noise = nes_noise() * env_noise * 0.65
        val = (body + noise) * amp
        add_sample(start_idx + i, val, val)

def sfx_drum_hihat(start_time, amp=0.10):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.035
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 85.0)
        val = nes_noise() * env * amp
        add_sample(start_idx + i, val * 0.8, val * 1.1)

def sfx_drum_crash(start_time, amp=0.25):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.65
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 6.5)
        # Filtered / shimmering metallic noise
        s1 = math.sin(2.0 * math.pi * 3240.0 * t) * 0.2
        s2 = math.sin(2.0 * math.pi * 4820.0 * t) * 0.2
        val = (nes_noise() * 0.7 + s1 + s2) * env * amp
        add_sample(start_idx + i, val * 0.9, val * 1.1)

def sfx_badge_impact(start_time, pitch_scale=1.0, amp=0.28, pan=0.0):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.075
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    
    # 1. Low punchy thud (tri drop)
    f_thud = 110.0 * pitch_scale
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 55.0)
        cur_f = f_thud * math.exp(-t * 28.0) + 38.0
        val = triangle_wave(cur_f, t) * env * amp * 0.75
        add_sample(start_idx + i, val * l_pan, val * r_pan)
        
    # 2. Clattering plastic/stone click (pulse burst)
    click_dur = 0.022
    click_samples = int(click_dur * SAMPLE_RATE)
    click_f = 640.0 * pitch_scale
    for i in range(click_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 110.0)
        val = (pulse_wave(click_f, t, duty=0.125, harmonics=4) * 0.6 + nes_noise() * 0.4) * env * amp * 0.45
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def sfx_alarm_pulse(start_time, freq=880.0, dur=0.085, amp=0.22, pan=0.0):
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        # Crisp square pulse with quick exponential decay
        env = math.exp(-t * 12.0)
        # Sub-harmonic growl for alarm bite
        val = (square_wave(freq, t, harmonics=5) * 0.75 + 
               square_wave(freq * 0.5, t, harmonics=3) * 0.35) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def sfx_badge_slot(start_time, freq, amp=0.14, pan=0.0):
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.065
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 60.0)
        val = pulse_wave(freq, t, duty=0.125, harmonics=4) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def sfx_mechanical_keystroke(start_time, amp=0.16, pan=0.0, is_enter=False):
    start_idx = int(start_time * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    
    # 1. High-frequency switch click (5ms)
    click_dur = 0.006
    click_samples = int(click_dur * SAMPLE_RATE)
    click_freq = 3400.0 if not is_enter else 2200.0
    for i in range(click_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 300.0)
        click_val = (pulse_wave(click_freq, t, duty=0.125, harmonics=3) * 0.6 + nes_noise() * 0.4) * env * amp * 0.8
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


# ----------------- SECTION 2: 2.5s - 7.0s (HAT EQUIP, VORTEX RISER & VAULT LOCK) -----------------
print("Synthesizing Section 2: Hat Equip, Vortex Riser & Vault Lock (2.5s - 7.0s)...")

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

# 3.10s - 3.50s: Level-up fanfare / bright arpeggio with celebratory sparkle chime as wizard hat equips
level_up_notes = [523.25, 659.25, 783.99, 987.77, 1046.50, 1318.51, 1567.98, 2093.00] # C5 to C7
step = 0.040
for idx, freq in enumerate(level_up_notes):
    st = 3.10 + idx * step
    d = 0.28 if idx == len(level_up_notes) - 1 else 0.08
    pan = -0.4 + (idx / len(level_up_notes)) * 0.8
    note(st, freq, dur=d, amp=0.32 if idx == len(level_up_notes) - 1 else 0.24,
         wave_type='pulse', duty=0.25, pan=pan)

# Celebratory sparkle chimes
sparkle_freqs = [2093.00, 2637.02, 3135.96, 4186.01]
for s_idx, sf in enumerate(sparkle_freqs):
    st_s = 3.42 + s_idx * 0.040
    note(st_s, sf, dur=0.22, amp=0.16, wave_type='pulse', duty=0.125, pan=(-0.5 if s_idx % 2 == 0 else 0.5))

# 3.5s - 6.2s: Centripetal vortex riser + swirling frequency sweep + magic spell casting hum
vortex_start = 3.50
vortex_end = 6.20
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
    
    # Swirling frequency sweep (240Hz ramping to 1400Hz)
    sweep_freq = 240.0 * math.exp(prog * 1.76)
    rot_speed = 8.0 + prog * 10.0
    pan = math.sin(2.0 * math.pi * rot_speed * t) * 0.75
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    
    sweep_val = (pulse_wave(sweep_freq, t, duty=0.25, harmonics=4) * 0.65 + 
                 square_wave(sweep_freq * 1.5, t, harmonics=3) * 0.35) * env * 0.20
    
    add_sample(vortex_idx + i, (hum + sweep_val) * l_pan, (hum + sweep_val) * r_pan)

# Accelerating slot chimes as badges swirl into the vault (3.65s - 6.15s)
slot_chime_notes = [1046.50, 1174.66, 1318.51, 1567.98, 1760.00, 2093.00, 2349.32, 2637.02]
num_slots = 28
for i in range(num_slots):
    t_slot = vortex_start + 0.15 + (i / num_slots) ** 1.35 * 2.45
    f_slot = slot_chime_notes[i % len(slot_chime_notes)]
    slot_pan = math.sin(i * 1.2) * 0.7
    sfx_badge_slot(t_slot, f_slot, amp=0.15, pan=slot_pan)

# 6.25s - 7.0s: Mechanical vault latch click / lock sound + clean confirmation chime
sfx_metallic_click(6.28, f1=2800.0, f2=4200.0, amp=0.28)
sfx_metallic_click(6.38, f1=2200.0, f2=3300.0, amp=0.30)

# Solid vault latch thud (6.42s)
thud_idx = int(6.42 * SAMPLE_RATE)
thud_dur = 0.18
for i in range(int(thud_dur * SAMPLE_RATE)):
    t = i / SAMPLE_RATE
    env = math.exp(-t * 26.0)
    freq = 88.0 * math.exp(-t * 22.0) + 32.0
    val = (triangle_wave(freq, t) * 0.85 + nes_noise() * 0.25) * env * 0.42
    add_sample(thud_idx + i, val, val)

# Clean confirmation chime when context drops to 2% (6.60s - 7.00s)
note(6.60, G6, dur=0.22, amp=0.24, wave_type='pulse', duty=0.125, pan=-0.2)
note(6.72, C7, dur=0.45, amp=0.30, wave_type='pulse', duty=0.25, pan=0.2)
note(6.75, E7, dur=0.40, amp=0.16, wave_type='sine', pan=0.3)


# ----------------- SECTION 3: 7.0s - 10.5s (TERMINAL BLIP & 18 TYPING SWITCH CLICKS) -----------------
print("Synthesizing Section 3: Terminal Popup Blip & 18 Typing Switch Clicks (7.0s - 10.5s)...")

# 7.0s: Soft window open blip (smooth rising 2-tone chime)
note(7.00, G5, dur=0.06, amp=0.20, wave_type='sine', pan=-0.2)
note(7.06, C6, dur=0.09, amp=0.24, wave_type='sine', pan=0.2)

# 7.35s - 9.40s: 18 distinct typing switch clicks
keystroke_times = [
    7.35, 7.45, 7.54, 7.65, 7.76, 7.86,
    7.97, 8.08, 8.19, 8.32, 8.43, 8.54,
    8.66, 8.77, 8.88, 8.99, 9.10, 9.35 # Enter key at 9.35
]
for k_idx, kt in enumerate(keystroke_times):
    is_ent = (k_idx == len(keystroke_times) - 1)
    k_pan = -0.20 + ((k_idx * 5) % 9) * 0.05
    k_amp = 0.22 if is_ent else random.uniform(0.14, 0.19)
    sfx_mechanical_keystroke(kt, amp=k_amp, pan=k_pan, is_enter=is_ent)

# Carriage return acknowledge beep at 9.50s
note(9.50, A6, dur=0.065, amp=0.18, wave_type='square', pan=0.0)


# ----------------- SECTION 4: 10.5s - 14.0s (GLOCKENSPIEL WAND CHIME & LEVITATION HUM) -----------------
print("Synthesizing Section 4: Glockenspiel Wand Chime & Levitation Hum (10.5s - 14.0s)...")

# 1) Magic casting chime at 10.50s (glockenspiel arpeggio)
lev_arpeggio = [659.25, 830.61, 987.77, 1318.51, 1661.22] # E5, G#5, B5, E6, G#6
for l_idx, lf in enumerate(lev_arpeggio):
    note(10.50 + l_idx * 0.045, lf, dur=0.25, amp=0.18, wave_type='pulse', duty=0.125, pan=-0.4 + l_idx * 0.2)

# 2) Low resonant levitation hum (10.5s to 13.8s)
lev_start = 10.50
lev_dur = 3.30
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

# 3) Magical harmonic shimmer as book floats across shelf (10.8s to 13.7s)
shimmer_notes = [1318.51, 1661.22, 1975.53, 2349.32, 2637.02, 3322.44]
for s_i in range(18):
    t_shim = 10.80 + s_i * 0.15
    f_shim = shimmer_notes[s_i % len(shimmer_notes)]
    shim_pan = math.sin(s_i * 0.8) * 0.75
    note(t_shim, f_shim, dur=0.30, amp=0.13, wave_type='pulse', duty=0.125, pan=shim_pan)


# ----------------- SECTION 5: 14.0s - 16.0s ('ACTIVATED' POWER CHORD) -----------------
print("Synthesizing Section 5: 'ACTIVATED' Power Chord (14.0s - 16.0s)...")

# 14.00s: Electric synth zap
zap_idx = int(14.00 * SAMPLE_RATE)
zap_dur = 0.055
for i in range(int(zap_dur * SAMPLE_RATE)):
    t = i / SAMPLE_RATE
    env = (1.0 - t / zap_dur) ** 0.8
    freq = 3200.0 * math.exp(-t * 45.0) + 240.0
    val = (pulse_wave(freq, t, duty=0.125, harmonics=4) * 0.7 + nes_noise() * 0.4) * env * 0.32
    add_sample(zap_idx + i, val * 0.9, val * 1.1)

# 14.02s: Power-up chord stinger hit
activated_chord = [C5, G5, C6, E6, G6]
for cf in activated_chord:
    note(14.02, cf, dur=0.55, amp=0.22, wave_type='pulse', duty=0.25, pan=0.0)

# Sustained chord with sparkles / chimes
for s_i in range(8):
    note(14.20 + s_i * 0.15, random.choice([1567.98, 2093.00, 2637.02, 3135.96]),
         dur=0.22, amp=0.12, wave_type='pulse', duty=0.125, pan=random.uniform(-0.5, 0.5))


# ----------------- SECTION 6: 16.0s - 18.0s (SWELLING CHORD RISER & RADIANT LOOP CHIME) -----------------
print("Synthesizing Section 6: Swelling Chord Riser & Radiant Loop Chime (16.0s - 18.0s)...")

# 1) Book opening flutter & whoosh (16.00s - 16.25s)
for f_time in [16.00, 16.07, 16.15, 16.24]:
    s_idx = int(f_time * SAMPLE_RATE)
    for i in range(int(0.025 * SAMPLE_RATE)):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 90.0)
        val = nes_noise() * env * 0.18
        add_sample(s_idx + i, val * 0.8, val * 1.1)

# 2) Swelling magical chord / harmonic riser (16.20s to 17.00s)
riser_start = 16.20
riser_end = 17.00
riser_dur = riser_end - riser_start
riser_samples = int(riser_dur * SAMPLE_RATE)
riser_idx = int(riser_start * SAMPLE_RATE)

swell_chord = [C4, G4, B4, D5, E5, G5, B5] # Lush Cmaj9 voicing
for i in range(riser_samples):
    t = i / SAMPLE_RATE
    prog = t / riser_dur
    env = 0.04 + 0.34 * (prog ** 2.2)
    val = 0.0
    for note_f in swell_chord:
        val += sine_wave(note_f, t) * 0.22 + pulse_wave(note_f, t, duty=0.25, harmonics=2) * 0.12
    riser_sweep_freq = 800.0 * math.exp(prog * 1.3)
    sweep_tone = sine_wave(riser_sweep_freq, t) * 0.15 * prog
    total_val = (val + sweep_tone) * env
    pan = math.sin(prog * math.pi * 3.0) * 0.35
    add_sample(riser_idx + i, total_val * 0.5 * (1.0 - pan), total_val * 0.5 * (1.0 + pan))

# 3) Radiant bloom impact chord at 17.00s
bloom_chord = [C6, G6, E7, C8]
for bf in bloom_chord:
    note(17.00, bf, dur=0.75, amp=0.28, wave_type='pulse', duty=0.125, pan=0.0)
    note(17.00, bf * 0.5, dur=0.65, amp=0.20, wave_type='sine', pan=0.0)

# Multi-tap ethereal stereo reflections (delay shimmer)
echo_taps = [
    (17.15, -0.4, 0.65),
    (17.30,  0.4, 0.42),
    (17.48, -0.3, 0.26),
    (17.65,  0.3, 0.15),
    (17.80,  0.0, 0.08)
]
for et, epan, edecay in echo_taps:
    for bf in [G6, E7]:
        note(et, bf, dur=0.30, amp=0.18 * edecay, wave_type='sine', pan=epan)

# 4) Clean dissolve to silence at 18.000s:
# Apply smooth cosine taper from 17.85s to 18.000s ensuring exact 0.0 at the end
fade_start = 17.85
fade_idx = int(fade_start * SAMPLE_RATE)
for i in range(fade_idx, TOTAL_SAMPLES):
    t_fade = (i - fade_idx) / (TOTAL_SAMPLES - fade_idx)
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
