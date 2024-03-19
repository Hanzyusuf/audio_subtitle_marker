# Audio Subtitle Marker Tool

The Audio Subtitle Marker Tool is a simple utility for marking timestamps of dialogs/verses in an audio file. It allows users to quickly add timestamps while listening to the audio, which can then be used for various purposes such as creating subtitles or automating tasks.

## Features

- Load audio files in various formats (e.g., WAV, MP3).
- Play, pause, stop, skip forward/backward, and seek to specific timestamps.
- Automatically mark timestamps with customizable shortcuts.
- Display real-time playback progress and timestamps.
- Support for both manual and auto-verse mode for timestamping.
- Ability to delete the last timestamp and verse.

## Usage

1. **Load Audio File**: Click the "Load Audio File" button to select an audio file from your system.
2. **Play/Pause**: Press the "Play/Pause" button or use the shortcut key (Spacebar) to toggle playback.
3. **Skip Forward/Backward**: Use the "Skip Forward 2s" and "Skip Back 2s" buttons to navigate through the audio.
4. **Seek to Last End Timestamp**: Click the "Seek to Last End Timestamp" button to jump to the last marked timestamp.
5. **Auto Verse Mode**: Toggle the "Auto Verse Mode" button to enable/disable automatic verse marking.
6. **Timestamp Marking**: Press the "S" key twice to mark the start and end of a verse/dialog. The timestamp will be saved automatically.
7. **Output Display**: The marked timestamps will be displayed in the output text area in real-time.

## Shortcuts

- **Space**: Toggle play/pause
- **S**: Add timestamp
- **A**: Skip backward 2 seconds
- **D**: Skip forward 2 seconds
- **T**: Toggle auto verse mode
- **F**: Seek to end of last marked verse
- **X**: Delete last marked verse OR cancel the currently started one

## Requirements

- Python 3.x
- Pynput
- [Just_Playback](https://github.com/cheofusi/just_playback)

## Installation

1. Clone the repository to your local machine.
2. Install the required dependencies using pip: `pip install -r requirements.txt`.
3. Run the main script: `python main.py`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
