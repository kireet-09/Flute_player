import numpy as np
import os
from scipy.io import wavfile

# Create notes directory if it doesn't exist
os.makedirs("notes", exist_ok=True)

# Function to generate a flute-like tone
def generate_flute_tone(frequency, duration=0.5, sample_rate=44100):
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate base sine wave at the fundamental frequency
    fundamental = 0.5 * np.sin(frequency * 2 * np.pi * t)
    
    # Add harmonics to create a more flute-like timbre
    # Flutes have strong odd harmonics
    second_harmonic = 0.2 * np.sin(2 * frequency * 2 * np.pi * t)
    third_harmonic = 0.3 * np.sin(3 * frequency * 2 * np.pi * t)
    fifth_harmonic = 0.1 * np.sin(5 * frequency * 2 * np.pi * t)
    
    # Combine all harmonics
    tone = fundamental + second_harmonic + third_harmonic + fifth_harmonic
    
    # Apply envelope for more realistic sound
    # Quick attack, long decay
    attack = 0.05  # portion of the sound dedicated to attack
    decay = 0.2    # portion of the sound dedicated to decay
    sustain = 0.6  # level at which the sound sustains
    release = 0.1  # portion of the sound dedicated to release
    
    envelope = np.ones(len(tone))
    attack_samples = int(attack * sample_rate * duration)
    decay_samples = int(decay * sample_rate * duration)
    release_samples = int(release * sample_rate * duration)
    
    # Attack phase (linear ramp up)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay phase (exponential decay to sustain level)
    decay_end = attack_samples + decay_samples
    envelope[attack_samples:decay_end] = np.linspace(1, sustain, decay_samples)
    
    # Sustain phase (constant level)
    release_start = len(envelope) - release_samples
    
    # Release phase (exponential decay to zero)
    envelope[release_start:] = np.linspace(sustain, 0, release_samples)
    
    # Apply envelope to the tone
    tone = tone * envelope
    
    # Normalize to avoid clipping
    tone = tone / np.max(np.abs(tone))
    
    # Convert to 16-bit PCM
    return (tone * 32767).astype(np.int16)

# Note frequencies (in Hz)
NOTE_FREQUENCIES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
}

# Generate and save each note
for note, frequency in NOTE_FREQUENCIES.items():
    print(f"Generating {note} at {frequency} Hz")
    tone = generate_flute_tone(frequency)
    output_file = os.path.join("notes", f"{note}.wav")
    wavfile.write(output_file, 44100, tone)
    print(f"Saved to {output_file}")

print("All notes generated successfully!") 