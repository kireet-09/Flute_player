# Hand Gesture Controlled Flute Player

A Python application that allows you to play a virtual flute using hand gestures captured by your webcam. The application uses OpenCV for computer vision, MediaPipe for hand tracking, and Pygame for sound generation.

## Features

- Real-time hand gesture detection using MediaPipe Hands
- Maps finger positions to flute notes
- Visual feedback showing current note and required finger positions
- Synthetic flute sound generation

## Requirements

- Python 3.7+
- Webcam
- Packages listed in `requirements.txt`

## Installation

1. Clone this repository:

   ```
   git clone <repository-url>
   cd flute
   ```

2. Install required packages:

   ```
   pip install -r requirements.txt
   ```

3. Generate flute note sound files:
   ```
   python generate_notes.py
   ```

## Usage

1. Run the main application:

   ```
   python flute_player.py
   ```

2. Position your hand in front of the webcam with palm facing the camera.

3. The application will display:

   - Your hand with landmark tracking
   - A virtual flute with 8 holes at the bottom of the screen
   - The currently playing note (if any)

4. To play notes:

   - Cover virtual flute holes with your fingers by positioning them higher or lower
   - The application will detect which fingers are "down" and play the corresponding note
   - Red circles indicate holes that should be covered for the current note
   - Green circles indicate holes that should remain open

5. Press 'q' to quit the application.

## Flute Fingering Chart

The application uses the following simplified fingering chart (1 = finger down, 0 = finger up):

- C4: [1, 1, 1, 1, 1, 1, 1, 1] (All fingers down)
- D4: [1, 1, 1, 1, 1, 1, 1, 0] (All except right pinky)
- E4: [1, 1, 1, 1, 1, 1, 0, 0] (All except right ring and pinky)
- F4: [1, 1, 1, 1, 1, 0, 0, 0] (All except right middle, ring, pinky)
- G4: [1, 1, 1, 1, 0, 0, 0, 0] (Only left hand fingers)
- A4: [1, 1, 1, 0, 0, 0, 0, 0] (Left index, middle, ring)
- B4: [1, 1, 0, 0, 0, 0, 0, 0] (Left index, middle)
- C5: [1, 0, 0, 0, 0, 0, 0, 0] (Only left index)

## Customization

- Adjust the `threshold` parameter in the `is_finger_down` function to change sensitivity
- Modify `NOTE_FINGERING` dictionary to create your own fingering patterns
- Edit the `generate_flute_tone` function in `generate_notes.py` to customize the sound

## Limitations

- The hand detection works best in good lighting conditions
- The simplified fingering system is not as precise as a real flute
- Performance may vary depending on your hardware

## Troubleshooting

- If you see "Error: Could not open camera", check your webcam connection
- If no sounds play, ensure the note sound files were generated correctly
- If hand detection is poor, try improving lighting or adjusting your hand position
