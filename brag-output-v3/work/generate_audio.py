"""
generate_audio.py
Procedural 22.0-second Stereo Soundtrack for RememberMe v2 Launch Video.
Framerate: 60 FPS -> 1320 frames -> 22.000s duration.
Sample Rate: 44,100 Hz, 16-bit Stereo PCM.
"""

import math
import struct
import wave
import random

SAMPLE_RATE = 44100
DURATION = 22.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

left_channel = [0.0] * TOTAL_SAMPLES
right_channel = [0.0] * TOTAL_SAMPLES

def add_sample(idx, l, r=None):
    if 0 <= idx < TOTAL_SAMPLES:
        if r is None:
            r = l
        left_channel[idx] += l
        right_channel[idx] += r

# ----------------- SYNTHESIS PRIMITIVES -----------------

def square_wave(freq, t, harmonics=9):
    """Band-limited square wave using additive synthesis"""
    val = 0.0
    for k in range(1, harmonics * 2, 2):
        val += math.sin(2 * math.pi * freq * k * t) / k
    return val * (4.0 / math.pi) * 0.7

def pulse_wave(freq, t, duty=0.25, harmonics=7):
    """Band-limited pulse wave"""
    val = 0.0
    for k in range(1, harmonics + 1):
        amp = math.sin(math.pi * k * duty) / k
        val += amp * math.cos(2 * math.pi * freq * k * t)
    return val * 1.5

def noise():
    return random.random() * 2.0 - 1.0

# ----------------- SOUND EFFECTS & INSTRUMENTS -----------------

def chiptune_note(start_time, freq, dur=0.15, amp=0.18, pan=0.0, wave_type='square'):
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * (4.0 / dur)) if dur > 0.05 else 1.0
        # vibrato
        vib = math.sin(2 * math.pi * 6.0 * t) * (freq * 0.015) if t > 0.08 else 0.0
        f = freq + vib
        if wave_type == 'square':
            s = square_wave(f, t, harmonics=7)
        elif wave_type == 'pulse':
            s = pulse_wave(f, t, duty=0.3, harmonics=6)
        else:
            s = math.sin(2 * math.pi * f * t)
        val = s * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def chiptune_error(start_time, amp=0.25):
    """Harsh retro 8-bit buzzer/error alarm"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.22
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        # Rapid toggle between 220Hz and 140Hz
        freq = 240 if (int(t * 40) % 2 == 0) else 130
        env = (1.0 - t / dur)
        val = square_wave(freq, t, harmonics=5) * env * amp
        add_sample(start_idx + i, val * 0.8, val * 1.2)

def magic_arpeggio(start_time, freqs, step_dur=0.07, amp=0.15):
    """Crystalline sparkle arpeggios"""
    for idx, f in enumerate(freqs):
        t0 = start_time + idx * step_dur
        dur = 0.4
        st_idx = int(t0 * SAMPLE_RATE)
        pan = -0.6 + (1.2 * (idx / max(1, len(freqs)-1)))
        l_pan = 0.5 * (1.0 - pan)
        r_pan = 0.5 * (1.0 + pan)
        samples = int(dur * SAMPLE_RATE)
        for i in range(samples):
            t = i / SAMPLE_RATE
            env = math.exp(-t * 9.0)
            sparkle = (math.sin(2 * math.pi * f * t) + 
                       0.5 * math.sin(2 * math.pi * f * 2.0 * t) + 
                       0.25 * math.sin(2 * math.pi * f * 3.01 * t))
            val = sparkle * env * amp
            add_sample(st_idx + i, val * l_pan, val * r_pan)

def spiral_vortex(start_time, dur=3.2, amp=0.22):
    """Whooshing 3D vortex riser with circular stereo panning"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        progress = t / dur
        # rising frequency for swirling bandpass noise
        swirl_rate = 2.0 + progress * 6.0  # rotations per second
        pan = math.sin(2 * math.pi * swirl_rate * t)
        l_pan = 0.5 * (1.0 - pan)
        r_pan = 0.5 * (1.0 + pan)
        env = (progress ** 1.5) * (1.0 if progress < 0.9 else (1.0 - progress) * 10)
        n = noise()
        # tone modulation
        pitch = 300 + (progress ** 2) * 2200
        mod = math.sin(2 * math.pi * pitch * t)
        val = (n * 0.7 + mod * 0.3) * env * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def wooden_snap(start_time, amp=0.35):
    """Crisp wooden bookshelf latch / snap click"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.08
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        body = math.sin(2 * math.pi * 180 * math.exp(-t * 60) * t) * math.exp(-t * 70)
        snap = noise() * math.exp(-t * 120) * 0.8
        val = (body + snap) * amp
        add_sample(start_idx + i, val, val)

def mech_typing(start_time, amp=0.18):
    """Crisp mechanical keyboard keystroke foley"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.04
    samples = int(dur * SAMPLE_RATE)
    pan = random.uniform(-0.3, 0.3)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    freq = random.uniform(1600, 2400)
    for i in range(samples):
        t = i / SAMPLE_RATE
        click = math.sin(2 * math.pi * freq * t) * math.exp(-t * 180)
        thump = math.sin(2 * math.pi * 220 * t) * math.exp(-t * 90) * 0.4
        val = (click + thump) * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def levitation_hum(start_time, dur=1.8, amp=0.25):
    """Mystical low frequency levitation hum with pitch rise"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        prog = t / dur
        freq = 90 + prog * 60 + math.sin(2 * math.pi * 5.0 * t) * 4.0
        env = math.sin(math.pi * prog)
        hum = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2.0 * t)
        val = hum * env * amp
        add_sample(start_idx + i, val * 0.9, val * 1.1)

def activation_chime(start_time, amp=0.3):
    """Electric spark chime on activation badge bloom"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.6
    samples = int(dur * SAMPLE_RATE)
    freqs = [1480, 2220, 2960]
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 7.0)
        chime = sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs)
        val = chime * env * amp
        add_sample(start_idx + i, val * 0.7, val * 1.3)

def heavy_riser(start_time, dur=1.0, amp=0.35):
    """Cinematic swell & riser into the beat drop"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        prog = t / dur
        pitch = 80 + (prog ** 2.2) * 1600
        env = (prog ** 2.0)
        tone = math.sin(2 * math.pi * pitch * t)
        swish = noise() * env * 0.6
        val = (tone * 0.5 + swish) * amp
        add_sample(start_idx + i, val * (1.0 - prog * 0.4), val * (0.6 + prog * 0.4))

# ----------------- BEAT 4 MODERN ELECTRONIC -----------------

def kick_808(start_time, amp=0.75):
    """Punchy low-end 808 kick drum"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.45
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        # Exponential pitch drop from 140Hz down to 45Hz
        freq = 45 + 110 * math.exp(-t * 22)
        phase = 2 * math.pi * (45 * t + 110 * (1 - math.exp(-t * 22)) / 22)
        env = math.exp(-t * 6.5)
        body = math.sin(phase) * env
        click = math.exp(-t * 120) * 0.25 * math.sin(2 * math.pi * 1200 * t)
        val = (body + click) * amp
        add_sample(start_idx + i, val, val)

def sub_bass_note(start_time, freq, dur=0.45, amp=0.42):
    """Warm saturated sub bass note"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        attack = min(1.0, t / 0.015)
        decay = math.exp(-t * (1.6 / dur))
        env = attack * decay
        sub = math.sin(2 * math.pi * freq * t)
        # soft saturation
        sat = math.tanh(sub * 1.5)
        val = sat * env * amp
        add_sample(start_idx + i, val, val)

def modern_snare(start_time, amp=0.45):
    """Crisp electronic layered snare & clap"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.22
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        n = noise() * math.exp(-t * 18)
        body = math.sin(2 * math.pi * 210 * math.exp(-t * 30) * t) * math.exp(-t * 25) * 0.5
        clap = noise() * math.exp(-t * 35) * (1.0 if t < 0.04 else 0.4)
        val = (n * 0.5 + body + clap * 0.3) * amp
        add_sample(start_idx + i, val * 0.95, val * 1.05)

def hihat(start_time, amp=0.15, pan=0.2):
    """Crisp high-frequency hi-hat tick"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.035
    samples = int(dur * SAMPLE_RATE)
    l_pan = 0.5 * (1.0 - pan)
    r_pan = 0.5 * (1.0 + pan)
    for i in range(samples):
        t = i / SAMPLE_RATE
        val = noise() * math.exp(-t * 120) * amp
        add_sample(start_idx + i, val * l_pan, val * r_pan)

def synth_chord(start_time, freqs, dur=1.8, amp=0.22):
    """Modern side-chained electronic synth pad chord"""
    start_idx = int(start_time * SAMPLE_RATE)
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        # Sidechain pump ducking for first 80ms
        sidechain = min(1.0, (t / 0.12) ** 2) if t < 0.12 else 1.0
        decay = math.exp(-t * (1.8 / dur))
        chord_val = 0.0
        for f in freqs:
            # detuned saw/sine mixture
            osc1 = math.sin(2 * math.pi * f * t)
            osc2 = math.sin(2 * math.pi * (f * 1.004) * t) * 0.6
            chord_val += (osc1 + osc2)
        chord_val = (chord_val / len(freqs)) * sidechain * decay * amp
        add_sample(start_idx + i, chord_val * 0.85, chord_val * 1.15)

def ui_counter_tick(start_time, freq=1800, amp=0.14):
    """Snappy Apple-style click for counter roll-up"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.015
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        val = math.sin(2 * math.pi * freq * t) * math.exp(-t * 250) * amp
        add_sample(start_idx + i, val, val)

def impact_thud(start_time, amp=0.55):
    """Cinematic sub impact on 100% and key metric reveals"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 0.8
    samples = int(dur * SAMPLE_RATE)
    for i in range(samples):
        t = i / SAMPLE_RATE
        f = 75 * math.exp(-t * 12)
        env = math.exp(-t * 4.5)
        val = math.sin(2 * math.pi * f * t) * env * amp
        add_sample(start_idx + i, val, val)

def terminal_ding(start_time, amp=0.35):
    """Crisp high-resolution bell chime on terminal complete"""
    start_idx = int(start_time * SAMPLE_RATE)
    dur = 1.2
    samples = int(dur * SAMPLE_RATE)
    freqs = [2093.0, 3135.9, 4186.0]  # C7, G7, C8 harmonic ring
    for i in range(samples):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 3.5)
        s = (math.sin(2 * math.pi * freqs[0] * t) * 0.7 + 
             math.sin(2 * math.pi * freqs[1] * t) * 0.4 +
             math.sin(2 * math.pi * freqs[2] * t) * 0.2)
        val = s * env * amp
        add_sample(start_idx + i, val * 0.9, val * 1.1)

# ----------------- SOUNDTRACK ARRANGEMENT -----------------

print("Synthesizing 22.0s soundtrack score...")

# --- BEAT 1: 0.0s - 3.8s (Chiptune melody + skill avalanche + error warnings) ---
melody_notes = [
    # (time, freq, dur, wave_type)
    (0.00, 523.25, 0.18, 'square'),  # C5
    (0.20, 659.25, 0.18, 'square'),  # E5
    (0.40, 783.99, 0.18, 'square'),  # G5
    (0.60, 987.77, 0.18, 'square'),  # B5
    (0.80, 1046.5, 0.35, 'square'),  # C6
    (1.20, 880.00, 0.22, 'square'),  # A5
    (1.45, 698.46, 0.22, 'square'),  # F5
    (1.70, 783.99, 0.45, 'square'),  # G5
    # Second phrase - starts getting overwhelmed
    (2.20, 659.25, 0.15, 'pulse'),   # E5
    (2.38, 587.33, 0.15, 'pulse'),   # D5
    (2.55, 523.25, 0.15, 'pulse'),   # C5
    (2.72, 440.00, 0.15, 'pulse'),   # A4
]
for (t, f, d, w) in melody_notes:
    chiptune_note(t, f, dur=d, amp=0.18, wave_type=w)

# Chiptune 8-bit bass line in Beat 1
chiptune_bass = [
    (0.00, 130.81, 0.35), # C3
    (0.40, 164.81, 0.35), # E3
    (0.80, 110.00, 0.35), # A2
    (1.20, 87.31, 0.35),  # F2
    (1.60, 98.00, 0.35),  # G2
    (2.00, 110.00, 0.35), # A2
]
for (t, f, d) in chiptune_bass:
    chiptune_note(t, f, dur=d, amp=0.22, wave_type='pulse', pan=-0.1)

# Avalanche micro rattles (badges landing)
for t_badge in [0.8, 1.1, 1.4, 1.7, 1.9, 2.1, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4]:
    chiptune_note(t_badge, random.uniform(800, 1800), dur=0.03, amp=0.08, wave_type='square', pan=random.uniform(-0.8, 0.8))

# Panic error buzzers & warning flashes
chiptune_error(2.20, amp=0.22)
chiptune_error(2.80, amp=0.26)
chiptune_error(3.30, amp=0.32)

# --- BEAT 2: 3.8s - 8.0s (Wizard Hat, Magic Shockwave, Spiral Vortex, Bookshelf) ---
# 3.8s: Mascot peeks out, celestial sparkles descending
sparkle_freqs = [659.25, 783.99, 987.77, 1174.66, 1318.51, 1567.98, 1975.53, 2349.32]
magic_arpeggio(3.85, sparkle_freqs, step_dur=0.08, amp=0.18)

# 4.60s: Wizard Hat equips -> Purple Magic Shockwave burst
chiptune_note(4.60, 1760.0, dur=0.45, amp=0.35, wave_type='pulse')
magic_arpeggio(4.65, [1046.5, 1318.5, 1567.98, 2093.0, 2637.0], step_dur=0.05, amp=0.25)
# Sub swell from shockwave
sub_bass_note(4.60, 55.0, dur=0.8, amp=0.35)

# 4.9s - 7.6s: 3D spiral vortex whoosh riser
spiral_vortex(4.90, dur=2.7, amp=0.26)

# 7.65s: Skills cleanly lock into bookshelf -> Satisfying wooden latch snap
wooden_snap(7.65, amp=0.42)
wooden_snap(7.75, amp=0.25)

# --- BEAT 3: 8.0s - 11.5s (Terminal Prompt Typing, Levitation, Activation, Heavy Riser) ---
# 8.0s - 9.3s: Prompt typing (> "Audit postgres pool sizing...")
typing_times = [8.05, 8.12, 8.20, 8.28, 8.35, 8.44, 8.52, 8.61, 8.70, 8.78, 8.87, 8.95, 9.05, 9.15, 9.25]
for tt in typing_times:
    mech_typing(tt, amp=random.uniform(0.14, 0.22))

# 9.4s - 10.4s: Book levitates -> Humming sound
levitation_hum(9.40, dur=1.1, amp=0.28)

# 10.45s: Pill badge blooms (⚡ Activated: postgresql)
activation_chime(10.45, amp=0.38)

# 10.5s - 11.5s: Tome opens toward camera -> Heavy riser & swell into drop
heavy_riser(10.50, dur=1.0, amp=0.42)

# --- BEAT 4: 11.5s - 18.5s (Electronic Beat Drop & Apple Keynote Stats) ---
# The Drop hits at 11.50s exactly!
# BPM: 120 (0.5s per quarter note beat, 0.25s eighth, 0.125s sixteenth)
beat_start_time = 11.50
total_beats = 14  # 7 seconds = 14 beats at 120 BPM

# Chords: Fmaj7 (11.5s), G/A (13.5s), Am9 (15.5s), Em7 (17.0s)
synth_chord(11.50, [174.61, 220.00, 261.63, 329.63], dur=1.9, amp=0.28)  # Fmaj7
synth_chord(13.50, [196.00, 246.94, 293.66, 369.99], dur=1.9, amp=0.30)  # G
synth_chord(15.50, [220.00, 261.63, 329.63, 392.00], dur=1.5, amp=0.28)  # Am
synth_chord(17.00, [164.81, 246.94, 293.66, 329.63], dur=1.5, amp=0.26)  # Em

# Drum & Bass pattern:
for b in range(total_beats):
    t_b = beat_start_time + b * 0.5
    bar_beat = b % 4
    
    # 808 Kick on beats 0 and 2.5
    if bar_beat == 0:
        kick_808(t_b, amp=0.72)
    elif bar_beat == 2:
        kick_808(t_b, amp=0.68)
        if b < 12:
            kick_808(t_b + 0.375, amp=0.52) # syncopated push
            
    # Snare on beats 1 and 3
    if bar_beat in (1, 3):
        modern_snare(t_b, amp=0.48)
        
    # 16th Hi-hats
    for sub in [0.0, 0.125, 0.25, 0.375]:
        p = 0.25 if (int(sub * 1000) % 2 == 0) else -0.25
        hihat(t_b + sub, amp=0.14 if sub in (0.0, 0.25) else 0.09, pan=p)

# Sub bass melody
bass_notes = [
    (11.50, 43.65, 0.45), # F1
    (12.00, 43.65, 0.45),
    (12.75, 48.99, 0.35), # G1
    (13.50, 55.00, 0.45), # A1
    (14.00, 55.00, 0.45),
    (14.75, 43.65, 0.35),
    (15.50, 55.00, 0.45), # A1
    (16.00, 65.41, 0.45), # C2
    (16.75, 48.99, 0.35), # G1
    (17.50, 43.65, 0.80), # F1
]
for (t_sub, f_sub, d_sub) in bass_notes:
    sub_bass_note(t_sub, f_sub, dur=d_sub, amp=0.45)

# Metric 1 Foley: Counter rolling up 34% -> 100% (11.8s - 13.0s)
for i in range(24):
    t_tick = 11.80 + (i / 24.0) ** 1.3 * 1.15
    freq_tick = 1200 + i * 40
    ui_counter_tick(t_tick, freq=freq_tick, amp=0.15)
# Impact hit on 100% Reachable (13.00s)
impact_thud(13.00, amp=0.65)
activation_chime(13.02, amp=0.28)

# Metric 2 Foley: 0 DISK READS transition (14.50s)
ui_counter_tick(14.48, freq=2400, amp=0.22)
ui_counter_tick(14.53, freq=2800, amp=0.25)
impact_thud(14.55, amp=0.48)

# Metric 3 Foley: ~90% COST SAVED transition (16.50s)
ui_counter_tick(16.48, freq=2600, amp=0.22)
activation_chime(16.52, amp=0.32)
impact_thud(16.55, amp=0.48)

# --- BEAT 5: 18.5s - 22.0s (Outro, Isometric Terminal, Terminal Ding, Fade) ---
# Warm resolving synth chord
synth_chord(18.50, [130.81, 196.00, 261.63, 329.63, 392.00], dur=3.2, amp=0.26) # Cmaj9
sub_bass_note(18.50, 32.70, dur=2.5, amp=0.32) # C1 deep root

# Typing 'python install.py'
outro_typing = [18.85, 18.93, 19.02, 19.10, 19.18, 19.26, 19.35, 19.45, 19.55, 19.64, 19.74, 19.83, 19.92, 20.02, 20.12]
for ot in outro_typing:
    mech_typing(ot, amp=random.uniform(0.12, 0.20))

# Enter press & terminal complete ding at 20.30s
wooden_snap(20.30, amp=0.30)
terminal_ding(20.35, amp=0.40)

# ----------------- MASTERING & EXPORT -----------------

print("Mastering and soft-limiting stereo audio...")
max_val = max(max(abs(l) for l in left_channel), max(abs(r) for r in right_channel), 0.001)
gain = 0.88 / max_val
print(f"Peak amplitude: {max_val:.3f}, Applying normalization gain: {gain:.3f}")

packed = bytearray()
for i in range(TOTAL_SAMPLES):
    t = i / SAMPLE_RATE
    # Smooth fade out in the final 1.0 second
    fade = 1.0
    if t > 21.0:
        fade = max(0.0, (22.0 - t) / 1.0)
        
    l = math.tanh(left_channel[i] * gain) * fade
    r = math.tanh(right_channel[i] * gain) * fade
    
    l_int = int(max(-32767, min(32767, l * 32767)))
    r_int = int(max(-32767, min(32767, r * 32767)))
    packed.extend(struct.pack('<hh', l_int, r_int))

out_wav = r"D:\Project\RememberMe\brag-output-v3\work\audio.wav"
with wave.open(out_wav, 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(packed)

print(f"Successfully generated 22.0s soundtrack: {out_wav}")
