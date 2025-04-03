import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import threading
from collections import deque
import os

# Initialize MediaPipe Hands with improved parameters
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.4
)

# Initialize Pygame for audio
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Define flute notes and their sound files
NOTES = {
    "C4": "notes/C4.wav",
    "D4": "notes/D4.wav",
    "E4": "notes/E4.wav",
    "F4": "notes/F4.wav",
    "G4": "notes/G4.wav",
    "A4": "notes/A4.wav",
    "B4": "notes/B4.wav",
    "C5": "notes/C5.wav",
}

# Load sounds with better error handling
sounds = {}
for note, file in NOTES.items():
    try:
        sounds[note] = pygame.mixer.Sound(file)
    except Exception as e:
        print(f"Warning: Could not load sound file {file}: {e}")

# Define finger landmarks for flute fingering
FINGER_LANDMARKS = {
    # Left hand fingers (first 4 holes)
    "LEFT_INDEX": mp_hands.HandLandmark.INDEX_FINGER_TIP,
    "LEFT_MIDDLE": mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    "LEFT_RING": mp_hands.HandLandmark.RING_FINGER_TIP,
    "LEFT_PINKY": mp_hands.HandLandmark.PINKY_TIP,
    # Right hand fingers (last 4 holes)
    "RIGHT_INDEX": mp_hands.HandLandmark.INDEX_FINGER_TIP,
    "RIGHT_MIDDLE": mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    "RIGHT_RING": mp_hands.HandLandmark.RING_FINGER_TIP,
    "RIGHT_PINKY": mp_hands.HandLandmark.PINKY_TIP,
}

# Map finger combinations to notes (1 = finger up, 0 = finger down)
NOTE_FINGERING = {
    "C4": [0, 0, 0, 0, 0, 0, 0, 0],  # All fingers down
    "D4": [0, 0, 0, 0, 0, 0, 0, 1],  # All fingers down except right pinky
    "E4": [0, 0, 0, 0, 0, 0, 1, 1],  # All fingers down except right ring and pinky
    "F4": [0, 0, 0, 0, 0, 1, 1, 1],  # All fingers down except right hand (except index)
    "G4": [0, 0, 0, 0, 1, 1, 1, 1],  # Only left hand fingers down
    "A4": [0, 0, 0, 1, 1, 1, 1, 1],  # Left hand except pinky down
    "B4": [0, 0, 1, 1, 1, 1, 1, 1],  # Only left index and middle down
    "C5": [0, 1, 1, 1, 1, 1, 1, 1],  # Only left index down
}

# Variables for sound control
current_note = None
playing = False
sound_thread = None
stop_event = threading.Event()
MIN_NOTE_CHANGE_DELAY = 0.5  # Seconds

# Finger position smoothing with larger window
SMOOTHING_WINDOW = 10  # Increased from 5
finger_history = {finger: deque(maxlen=SMOOTHING_WINDOW) for finger in FINGER_LANDMARKS.keys()}

def is_finger_down(landmarks, finger_landmark):
    """Check if a finger is down by checking if tip touches palm node."""
    if not landmarks:
        return False
    
    # Map finger tips to their corresponding palm nodes (MCP joints)
    finger_map = {
        mp_hands.HandLandmark.INDEX_FINGER_TIP: mp_hands.HandLandmark.INDEX_FINGER_MCP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP: mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
        mp_hands.HandLandmark.RING_FINGER_TIP: mp_hands.HandLandmark.RING_FINGER_MCP,
        mp_hands.HandLandmark.PINKY_TIP: mp_hands.HandLandmark.PINKY_MCP,
    }
    
    if finger_landmark not in finger_map:
        return False
    
    # Get finger tip and palm node positions
    tip = landmarks[finger_landmark]
    palm_node = landmarks[finger_map[finger_landmark]]
    
    # Calculate distance between tip and palm node
    distance = np.sqrt((tip.x - palm_node.x)**2 + (tip.y - palm_node.y)**2)
    
    # Consider finger down if tip is close enough to palm node
    threshold = 0.05  # Adjust this value to change sensitivity
    return distance < threshold

def get_smoothed_finger_state(finger_name, is_down):
    """Apply smoothing to finger state to reduce jitter"""
    finger_history[finger_name].append(1 if is_down else 0)
    avg = sum(finger_history[finger_name]) / len(finger_history[finger_name])
    return avg > 0.6  # Slightly reduced threshold for more responsiveness

def get_current_note(landmarks_left, landmarks_right):
    """Determine which note to play based on finger positions from both hands"""
    if not landmarks_left or not landmarks_right:
        return None
    
    finger_status = []
    for i, (finger_name, landmark_id) in enumerate(FINGER_LANDMARKS.items()):
        landmarks = landmarks_left if "LEFT" in finger_name else landmarks_right
        is_down = is_finger_down(landmarks, landmark_id)
        smoothed_state = get_smoothed_finger_state(finger_name, is_down)
        finger_status.append(1 if smoothed_state else 0)
    
    best_match, best_score = None, -1
    for note, pattern in NOTE_FINGERING.items():
        score = sum(1 for a, b in zip(finger_status, pattern) if a == b)
        if score > best_score:
            best_score = score
            best_match = note
    
    return best_match if best_score >= 7 else None

def play_note_thread(note):
    """Play a note continuously until stopped."""
    if note not in sounds:
        return
    sound = sounds[note]
    while not stop_event.is_set():
        sound.play()
        time.sleep(0.5)  # Longer delay between note plays

def stop_playing():
    """Stop the current note."""
    global playing, sound_thread
    if playing and sound_thread:
        stop_event.set()
        sound_thread.join()
        stop_event.clear()
        playing = False

def start_playing(note):
    """Start playing a note."""
    global playing, sound_thread, current_note
    if note not in sounds:
        return
    stop_playing()
    current_note = note
    sound_thread = threading.Thread(target=play_note_thread, args=(note,))
    sound_thread.daemon = True
    sound_thread.start()
    playing = True

def main():
    """Main function for the virtual flute player."""
    os.makedirs("notes", exist_ok=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    last_note_change = time.time()
    note_display_time = 2
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image")
            break
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        frame_height, frame_width = frame.shape[:2]
        landmarks_left, landmarks_right = None, None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                if wrist_x < 0.5:
                    landmarks_left = hand_landmarks.landmark
                else:
                    landmarks_right = hand_landmarks.landmark
                
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )
            
            note = get_current_note(landmarks_left, landmarks_right)
            current_time = time.time()
            if note and (current_note != note or not playing):
                if current_time - last_note_change >= MIN_NOTE_CHANGE_DELAY:
                    start_playing(note)
                    last_note_change = current_time
            
            if current_note and current_time - last_note_change < note_display_time:
                cv2.putText(frame, f"Playing: {current_note}", (50, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            stop_playing()
        
        # Draw virtual flute UI
        cv2.rectangle(frame, (50, frame_height - 100), (frame_width - 50, frame_height - 50), (0, 0, 255), 2)
        hole_y = frame_height - 75
        hole_spacing = (frame_width - 100) // 8
        for i in range(8):
            hole_x = 50 + hole_spacing // 2 + i * hole_spacing
            # Fixed color logic: 0 = down (red), 1 = up (green)
            color = (128, 128, 128) if not current_note else (
                (0, 255, 0) if NOTE_FINGERING[current_note][i] == 1 else (0, 0, 255)
            )
            cv2.circle(frame, (hole_x, hole_y), 15, color, -1)
        
        cv2.putText(frame, "Use both hands to play the virtual flute", (50, frame_height - 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow('Virtual Flute Player', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    stop_playing()
    cap.release()
    cv2.destroyAllWindows()
    pygame.mixer.quit()

if __name__ == "__main__":
    main() 