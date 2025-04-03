import pygame
import time
import os

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Check if notes directory exists
if not os.path.exists("notes"):
    print("Notes directory not found. Please run generate_notes.py first.")
    exit(1)

# List of notes to test
notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]

# Play each note
print("Testing flute note sounds...")
for note in notes:
    file_path = os.path.join("notes", f"{note}.wav")
    
    if not os.path.exists(file_path):
        print(f"Warning: Sound file for {note} not found at {file_path}")
        continue
    
    try:
        print(f"Playing {note}...")
        sound = pygame.mixer.Sound(file_path)
        sound.play()
        
        # Wait for the sound to finish playing (approximately)
        duration = 1.0  # seconds
        time.sleep(duration)
        
        # Stop the sound to ensure it doesn't continue
        sound.stop()
        
    except Exception as e:
        print(f"Error playing {note}: {e}")

print("Test complete. Press any key to exit...")
input()

# Clean up
pygame.mixer.quit() 