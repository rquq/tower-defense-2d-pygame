import os
import wave
import struct
import math
import random

SAMPLE_RATE = 22050

def save_wav(filename, samples):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2) # 16-bit
        wav_file.setframerate(SAMPLE_RATE)
        for s in samples:
            # clip
            s = max(-1.0, min(1.0, s))
            # scale to 16-bit integer
            v = int(s * 32767.0)
            wav_file.writeframesraw(struct.pack('<h', v))

def generate_tone(freq_start, freq_end, duration, wave_type='square', vol_start=1.0, vol_end=0.0):
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0.0
    for i in range(num_samples):
        t = i / float(num_samples)
        freq = freq_start * (1 - t) + freq_end * t
        vol = vol_start * (1 - t) + vol_end * t
        
        phase += (freq * 2 * math.pi) / SAMPLE_RATE
        
        if wave_type == 'square':
            val = 1.0 if math.sin(phase) > 0 else -1.0
        elif wave_type == 'saw':
            val = 2.0 * (phase / (2 * math.pi) - math.floor(phase / (2 * math.pi) + 0.5))
        elif wave_type == 'sine':
            val = math.sin(phase)
        elif wave_type == 'noise':
            val = random.uniform(-1.0, 1.0)
            
        samples.append(val * vol * 0.5) # Overall volume reduction
    return samples

def append_silence(samples, duration):
    samples.extend([0.0] * int(SAMPLE_RATE * duration))
    return samples

# Generators
sounds = {}

# UI
sounds['ui_click.wav'] = generate_tone(880, 1200, 0.05, 'square', 0.5, 0.0)
sounds['error.wav'] = generate_tone(150, 150, 0.1, 'saw', 0.8, 0.1) + generate_tone(150, 100, 0.15, 'saw', 0.8, 0.0)
sounds['place_tower.wav'] = generate_tone(300, 50, 0.15, 'sine', 1.0, 0.0)
sounds['sell.wav'] = generate_tone(800, 1200, 0.1, 'sine', 0.8, 0.4) + generate_tone(1200, 2000, 0.2, 'sine', 0.6, 0.0)

# Weapons
sounds['shoot_cannon.wav'] = generate_tone(100, 50, 0.15, 'noise', 0.3, 0.0)
sounds['shoot_arrow.wav'] = generate_tone(1000, 400, 0.1, 'sine', 0.2, 0.0)
sounds['shoot_fire.wav'] = generate_tone(300, 50, 0.3, 'noise', 0.25, 0.0)
sounds['shoot_lightning.wav'] = generate_tone(800, 200, 0.15, 'saw', 0.2, 0.0) + generate_tone(1000, 400, 0.1, 'square', 0.1, 0.0)
sounds['shoot_ice.wav'] = generate_tone(1200, 1500, 0.2, 'sine', 0.25, 0.0)

# Entities
sounds['enemy_hit.wav'] = generate_tone(400, 200, 0.05, 'noise', 0.3, 0.0)
sounds['enemy_death.wav'] = generate_tone(300, 100, 0.25, 'saw', 0.3, 0.0)
sounds['base_hit.wav'] = generate_tone(150, 50, 0.4, 'noise', 0.5, 0.0)

# Events
sounds['wave_start.wav'] = generate_tone(440, 440, 0.15, 'square', 0.5, 0.3) + generate_tone(554, 554, 0.15, 'square', 0.5, 0.3) + generate_tone(659, 659, 0.4, 'square', 0.5, 0.0)
sounds['powerup.wav'] = generate_tone(600, 800, 0.1, 'sine', 0.6, 0.5) + generate_tone(800, 1200, 0.3, 'sine', 0.5, 0.0)
sounds['game_over.wav'] = generate_tone(300, 250, 0.4, 'saw', 0.7, 0.4) + generate_tone(250, 200, 0.4, 'saw', 0.6, 0.3) + generate_tone(200, 100, 0.8, 'saw', 0.5, 0.0)

for name, samples in sounds.items():
    path = os.path.join("assets", "sounds", name)
    save_wav(path, samples)
    print(f"Generated {path}")

print("All sounds generated successfully!")
