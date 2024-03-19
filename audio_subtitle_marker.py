import os
import time
import sys
from pathlib import Path
from tkinter import Tk, Label, Button, filedialog, Text, Scrollbar, messagebox
from just_playback import Playback
from pynput import keyboard

seek_skip_duration = 2

audio_loaded = False
verse_index = 1 # Keep track of the last saved verse (note: we are starting from 1 and not 0)
last_saved_time = 0  # Keep track of the last saved end time
auto_verse_mode = False # Automatically mark the verse start timestamp to the previous verse end timestamp

# Function to handle key press events
def on_press(key):
    global click_count

    if key == keyboard.Key.space:
        toggle_play_pause()

    try:
        k = key.char
    except:
        k = key.name
    
    if k == 's':
        add_timestamp()
    elif k == 'a':
        seek_skip(-seek_skip_duration)
    elif k == 'd':
        seek_skip(seek_skip_duration)
    elif k == 't':
        toggle_auto_verse()

    elif k == 'g':
        seek_next_verse()
    elif k == 'f':
        seek_previous_verse()
    elif k == 'h':
        seek_first_verse()
    elif k == 'j':
        seek_last_verse()

    elif k == 'x':
        if(click_count == 1):
            cancel_verse() # simply cancels the verse that has it's start already marked 
        else:
            delete_last_timestamp_and_verse()

# Function to add timestamp
def add_timestamp():
    global start_time, click_count, playback, verse_index, last_saved_time, output_text

    if(not audio_loaded):
            return
    
    click_count += 1
    if click_count == 1:
        start_time = playback.curr_pos
        # Check if the current start time is later than the last saved end time
        if start_time >= last_saved_time:
            indicate_verse_start_began(verse_index, start_time)
            #append_timestamp_start(verse_index, start_time)
            #update_output_text()
        else:
            click_count-=1 # unregister click since error
            show_error("Cannot save a timestamp earlier than the last saved one!")
    elif click_count == 2:
        end_time = playback.curr_pos
        # Check if the current end time is later than the last saved end time
        if end_time > start_time:
            append_timestamp_start(verse_index, start_time)
            append_timestamp_end(end_time)
            update_output_text()
            verse_index += 1
            last_saved_time = end_time
            click_count = 0 # reset click count to get ready for a new verse
            
            # mark the next verse start time immediately if auto verse mode is on
            if(auto_verse_mode):
                add_timestamp()
        else:
            click_count-=1 # unregister click since error
            show_error("End time cannot be earlier than (or equal to) the start time!")

    update_gui()
    output_text.see("end")

# Function to toggle play/pause of audio
def toggle_play_pause():
    global playback

    if(not audio_loaded):
        show_error("No audio loaded!")
        return

    if(not playback.active):
        playback.play()
        update_gui()
        return

    if playback.playing:
        playback.pause()
    else:
        playback.resume()

    update_gui()

# # Function to append timestamp to the output file
# def append_timestamp(start_time, end_time):
#     with open(output_file, 'a') as f:
#         f.write(f"{start_time}-{end_time}\n")
        
# Function to append timestamp to the output file
def append_timestamp_start(index, time):
    with open(output_file, 'a') as f:
        conditional_linebreak = '\n\n' if index > 1 else ''
        f.write(f"{conditional_linebreak}[{index}]\n{time}-")

# Function to append timestamp to the output file
def append_timestamp_end(time):
    with open(output_file, 'a') as f:
        f.write(f"{time}")

# Function to load audio file
def load_audio_file():
    global playback, audio_loaded, audio_title, last_saved_time

    audio_file = select_audio_file()
    playback.load_file(audio_file)

    set_output_file(audio_file)

    audio_loaded = True
    update_gui()

    audio_title.configure(text=Path(audio_file).stem, fg='green')
    update_time_label()

    reset_verse_state() # resets variables and loads the last timestamp it's verse index if exists

# Function to get the last end time from the output file
def load_last_time_and_verse():
    global last_saved_time, verse_index, output_text
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines and len(lines) >= 2:
                last_line = lines[-1].strip()
                parts = last_line.split('-')
                try:
                    if len(parts) >= 2:  # Check if end time exists
                        end_time = parts[-1]
                        last_saved_time = float(end_time)
                        
                    else:  # If end time doesn't exist, use start time
                        start_time = parts[0]
                        last_saved_time = float(start_time)
                except:
                    show_error("Failed to read and load last timestamp!")

                last_second_line = lines[-2].strip()
                try:
                    verse_index = int(last_second_line[1:-1])  # Extract verse index
                except:
                    show_error("Failed to read and load last verse!")

        output_text.see("end") # scroll to end

# Function to set the output file path
def set_output_file(audio_file):
    global output_file
    output_file = os.path.join('Data', 'Output', Path(audio_file).stem + '.txt')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    update_output_text() # update the realtime output file text

# Function to update the playback time label
def update_time_label():
    if(audio_loaded):
        curr_time = time.strftime('%H:%M:%S', time.gmtime(playback.curr_pos))
        total_time = time.strftime('%H:%M:%S', time.gmtime(playback.duration))
        time_label.config(text=f"Current Time: {curr_time} / Total Time: {total_time}")

# Function to periodically update the time label
def auto_update_time_label():
    update_time_label()
    root.after(1000, auto_update_time_label)

# Function to skip forward/bckward the playback time. Pass negative integer to skip backward.
def seek_skip(seconds):
    playback.seek(playback.curr_pos + seconds)
    update_time_label()

# Function to update the output text temporily to mark that verse start has been noted and waiting for end
def indicate_verse_start_began(index, time):
    # enable editing
    output_text.config(state="normal")

    # since this is the first verse, clear default text
    if(index==1):
        output_text.delete("1.0", "end")
    
    # add the indication to the output text
    conditional_linebreak = '\n\n' if index > 1 else ''
    tmp_text = f"{conditional_linebreak}[{index}]\n{time}-"
    output_text.insert("end", tmp_text)

    # disable editing
    output_text.config(state="disabled")

# Function to update the output text area with timestamps
def update_output_text():
    global output_text

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines:
                output_text.config(state="normal")
                output_text.delete("1.0", "end")
                for line in lines:
                    output_text.insert("end", line)
                output_text.config(state="disabled")
            else:
                output_text.config(state="normal")
                output_text.delete("1.0", "end")
                output_text.insert("end", "No timestamps found.")
                output_text.config(state="disabled")
    else:
        output_text.config(state="normal")
        output_text.delete("1.0", "end")
        output_text.insert("end", "No file found. Start saving timestamps to create one!")
        output_text.config(state="disabled")

    output_text.see("end")

# Function to create GUI
def create_gui():
    global root, time_label, playback, output_text, audio_title, toggle_button, auto_verse_mode, auto_verse_button, mark_verse_button, main_buttons

    root = Tk()
    root.title("Audio Subtitle Marker Tool")

    load_button = Button(root, text="Load Audio File", command=load_audio_file)
    load_button.pack(pady=10)

    audio_title = Label(root, text="No audio loaded.", fg='red')
    audio_title.pack()

    time_label = Label(root, text="")
    time_label.pack()

    auto_update_time_label()

    toggle_button = Button(root, text="Play/Pause (Spacebar)", command=toggle_play_pause, font=('Arial', 10))
    toggle_button.pack(pady=4)

    skip_forward_button = Button(root, text=f"Skip Forward {seek_skip_duration}s (D)", command=lambda: seek_skip(2), font=('Arial', 10))
    skip_forward_button.pack(pady=4)

    skip_back_button = Button(root, text=f"Skip Back {seek_skip_duration}s (A)", command=lambda: seek_skip(-2), font=('Arial', 10))
    skip_back_button.pack(pady=4)

    seek_previous_button = Button(root, text="Seek to Previous Verse (F)", command=seek_previous_verse, font=('Courier New', 8))
    seek_previous_button.pack(pady=4)
    seek_next_button = Button(root, text="Seek to Next Verse (G)", command=seek_next_verse, font=('Courier New', 8))
    seek_next_button.pack(pady=4)
    seek_first_button = Button(root, text="Seek to First Verse (H)", command=seek_first_verse, font=('Courier New', 8))
    seek_first_button.pack(pady=4)
    seek_last_button = Button(root, text="Seek to Last Verse (J)", command=seek_last_verse, font=('Courier New', 8))
    seek_last_button.pack(pady=4)

    auto_verse_button = Button(root, text=f"Auto Verse Mode: {auto_verse_mode}", command=toggle_auto_verse, bg="green" if auto_verse_mode else "red", fg="white" if auto_verse_mode else "black", font=('Arial', 9))
    auto_verse_button.pack(pady=4)

    mark_verse_button = Button(root, text=f"Mark Verse: Start (S)", command=add_timestamp, bg="green", font=('Courier New', 12))
    mark_verse_button.pack(pady=8)

    # we will keep all the buttons related to audio in an array to disable/enable as needed easily
    main_buttons = [toggle_button, skip_forward_button, skip_back_button, seek_last_button, auto_verse_button, mark_verse_button]

    # Output text area
    output_text = Text(root, wrap="none", height=10, width=50)
    output_text.pack(pady=10)

    # output_scroll = Scrollbar(root, command=output_text.yview)
    # output_scroll.pack(side="right", fill="y")
    # output_text.config(yscrollcommand=output_scroll.set)

    # Start listening for keystrokes
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    update_gui()

    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", _quit)

    root.mainloop()

# Function to update parts of gui (to call when certain states have changed)
def update_gui():
    global playback, toggle_button, auto_verse_mode, auto_verse_button, main_buttons, audio_loaded

    if playback.playing:
        toggle_button.config(text="Pause (Spacebar)", bg="red")
    else:
        toggle_button.config(text="Play (Spacebar)", bg="green")

    if auto_verse_mode:
        auto_verse_button.config(text=f"Auto Verse Mode: On (T)", bg="green")
    else:
        auto_verse_button.config(text=f"Auto Verse Mode: Off (T)", bg="red")

    if click_count==1:
        mark_verse_button.config(text=f"Mark Verse: End (S)", command=add_timestamp, bg="red")
    else:
        mark_verse_button.config(text=f"Mark Verse: Start (S)", command=add_timestamp, bg="green")

    for btn in main_buttons:
        btn.configure(state="normal" if audio_loaded else "disabled")

# Seek to the beginning of the first verse
def seek_first_verse():
    if(not audio_loaded):
        return
    
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines:
                for line in lines:
                    if '-' in line:
                        start_time, _ = line.strip().split('-')
                        playback.seek(float(start_time))
                        update_time_label()
                        return

# Seek to the beginning of the next verse
def seek_next_verse():
    if(not audio_loaded):
        return
    
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines:
                current_time = playback.curr_pos
                for line in lines:
                    if '-' in line:
                        start_time, end_time = line.strip().split('-')
                        if float(start_time) > current_time:
                            playback.seek(float(start_time))
                            update_time_label()
                            return

# Seek to the beginning of the previous verse
def seek_previous_verse():
    if(not audio_loaded):
        return
    
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines:
                current_time = playback.curr_pos
                previous_verse_start_time = 0
                for line in reversed(lines):
                    if '-' in line:
                        start_time, end_time = line.strip().split('-')
                        if float(start_time)+0.4 < current_time:
                            playback.seek(float(start_time))
                            update_time_label()
                            return
                playback.seek(0)
                update_time_label()


# Function to seek to the last end timestamp in the output file
def seek_last_verse():
    if(not audio_loaded):
        return
    
    if os.path.exists(output_file):  # Check if the output file exists
        with open(output_file, 'r') as f:
            lines = f.readlines()
            if lines and len(lines) >= 2:
                last_line = lines[-1].strip()
                _, end_time = last_line.split('-')
                playback.seek(float(end_time))
                update_time_label()

# Function to handle file selection using GUI dialog
def select_audio_file():
    root = Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select Audio File", initialdir="../Recitations",
                                           filetypes=[("Audio Files", "*.wav *.mp3")])
    return file_path

# Function to toggle auto verse mode between on/off
def toggle_auto_verse():
    global auto_verse_mode
    auto_verse_mode = not auto_verse_mode
    update_gui()

def cancel_verse():
    click_count = 0
    update_output_text()

def delete_last_timestamp_and_verse():
    global output_file

    # Check if the output file exists
    if os.path.exists(output_file):
        # Read the contents of the output file
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        # Check if there are any lines in the file
        if lines and len(lines) >= 2:
            # If the last line contains a timestamp, remove it
            if '-' in lines[-1]:
                lines.pop()
                lines.pop()
                
                if len(lines) > 1:
                    lines.pop()
                
                # Write the updated lines back to the output file
                with open(output_file, 'w') as f:
                    f.writelines(lines)
                print("Last timestamp and verse deleted successfully.")

                # Resets variables and re-loads the last timestamp it's verse index if exists
                reset_verse_state()
                # Update the output text area
                update_output_text()
            else:
                print("No timestamp found in the last line.")
        # Check if there is only 1 line (probably some glitch, so delete it anyways)
        elif lines and len(lines) == 1:
            with open(output_file, 'w') as f:
                f.write("")
            print("File cleared. Removed everything!")
            
            # Resets variables and re-loads the last timestamp it's verse index if exists
            reset_verse_state()
            # Update the output text area
            update_output_text()
        else:
            print("Output file is empty.")
    else:
        print("Output file does not exist.")

# Function to reset variables that are used for capturing verses (audio changed, timestamp deleted, etc)
def reset_verse_state():
    global click_count, verse_index, last_saved_time
    click_count = 0
    verse_index = 1
    last_saved_time = 0
    load_last_time_and_verse()

# Function to display popup errors
def show_error(message):
    messagebox.showerror("Error", message)

# Function to exit the program when tkinter window is closed
def _quit():
    global root
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()
        root.destroy()
        sys.exit(0)

# Initialize playback object
playback = Playback()

# Initialize global variables
click_count = 0
start_time = 0
output_file = ""

create_gui()