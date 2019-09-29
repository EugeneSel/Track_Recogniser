import contextlib
import wave

import pyaudio

from tr_functions.tr import *
from pydub import AudioSegment
from tkinter import *


class Error(Exception):
   pass


class TooManyTimeError(Error):
   pass


def exitWin():
    global root
    root.destroy()


def restart():
    global root
    root.destroy()
    main()


def new_track_info():
    track_info = np.array([])

    for i, row in enumerate(rows_add):
        for j, cell in enumerate(row):
            track_info = np.append(track_info, [cell.get()], axis=0)
    message = add_track(track_info[0], track_info[1], track_info[2], track_info[3])
    dim_label.config(text=message)


def file_analysis():
    file_name = ''
    for i, row in enumerate(rows_rec):
        for j, cell in enumerate(row):
            file_name = cell.get()

    src = file_name
    dst = "test.wav"

    count = 0

    # convert wav to mp3
    try:
        sound = AudioSegment.from_mp3(src)

        sound.export(dst, format="wav")

        with contextlib.closing(wave.open(dst, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        print(duration)

        result = recognise_track(dst, duration, 'f')
        message = ''
        count = len(result)
        for i in range(count):
            message += result[i]
            message += '\n'
    except FileNotFoundError:
        message = "Could not find current file.\nPlease, check the correctness of entered file name!"
        count += 2

    result_label.config(text=message)
    result_label.place(relx=0.5, rely=0.45, anchor="c", height=30 * count, width=270)


def record_analysis():

    try:
        RECORD_SECONDS = int(seconds.get())
        if RECORD_SECONDS > 30:
            raise TooManyTimeError
        elif RECORD_SECONDS < 1:
            raise ValueError
    except ValueError:
        seconds_label.config(text="Invalid time syntax. Please, repeat entering!")
    except TooManyTimeError:
        seconds_label.config(text="Maximal record duration - 30 seconds. Please, repeat entering!")
    else:
        CHUNK = 4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        WAVE_OUTPUT_FILENAME = "output.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        # record_label.config(text="* Finished recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        result = recognise_track(WAVE_OUTPUT_FILENAME, RECORD_SECONDS, 'r')
        message = ''
        count = len(result)
        for i in range(count):
            message += result[i]
            message += '\n'
        message += "Record saved into output.wav"

        result_label = Label(text=message)
        result_label.place(relx=0.25, rely=0.5, height=15 * (count + 1), width=270)


def delete_track_info():
    track_info = np.array([])
    trackList = getTrackList()

    for i, row in enumerate(rows_del):
        for j, cell in enumerate(row):
            track_info = np.append(track_info, [cell.get()], axis=0)

    is_exist = False
    for track in trackList:
        if track[0] == track_info[0] and track[1] == track_info[1]:
            is_exist = True
            break

    if is_exist:
        message = deleteTrack(track_info[0], track_info[1])
    else:
        message = "Track with current name or artist is not found. Please, check the correctness of entering!"
    dim_label.config(text=message)


def add_t():
    dim_label.config(text="Enter the track info:")
    recognise_from_file.destroy()
    recognise_from_record.destroy()
    delete.destroy()
    add.place(relx=0.32, rely=0.95, anchor="c", height=30, width=210, bordermode=OUTSIDE)
    add.config(command=new_track_info)
    submit.config(text="Back")

    global enter_file_name
    global enter_track_name
    global enter_track_author
    global enter_track_album

    enter_file_name = Label(text="Enter the file path:")
    enter_file_name.grid(row=1, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    enter_track_name = Label(text="Enter the track name:")
    enter_track_name.grid(row=2, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    enter_track_author = Label(text="Enter the track artist:")
    enter_track_author.grid(row=3, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    enter_track_album = Label(text="Enter the track album:")
    enter_track_album.grid(row=4, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    global rows_add
    global cols_add

    rows_add = []
    for i in range(4):
        cols_add = []
        for j in range(1):
            enter_field = Entry(relief=RIDGE, text='%d.%d' % (i, j))
            enter_field.grid(row=i + 1, column=j + 1, ipadx=10, ipady=6, padx=10, pady=2)
            cols_add.append(enter_field)
        rows_add.append(cols_add)


def recognise_from_file_t():
    global enter_file_name_rec

    dim_label.config(text="Enter the file info:")
    enter_file_name_rec = Label(text="Enter the file path:")
    enter_file_name_rec.grid(row=1, column=0, ipadx=10, ipady=6, padx=10, pady=5)
    add.destroy()
    recognise_from_record.destroy()
    delete.destroy()

    global result_label
    result_label = Label(text="")
    result_label.place(relx=0.5, rely=0.45, anchor="c", height=30, width=270)
    recognise_from_file.place(relx=0.32, rely=0.95, anchor="c", height=30, width=210, bordermode=OUTSIDE)
    recognise_from_file.config(command=file_analysis)
    submit.config(text="Back")

    global rows_rec
    global cols_rec

    rows_rec = []
    for i in range(1):
        cols_rec = []
        for j in range(1):
            enter_field = Entry(relief=RIDGE, text='%d.%d' % (i, j))
            enter_field.grid(row=i + 1, column=j + 1, ipadx=10, ipady=6, padx=10, pady=2)
            cols_rec.append(enter_field)
        rows_rec.append(cols_rec)


def recognise_from_record_t():
    dim_label.config(text="Click on the button below to start record:")
    add.destroy()
    recognise_from_file.destroy()
    delete.destroy()

    global seconds_label
    seconds_label = Label(text="Choose the record duration in seconds (Not more than 30s):")
    seconds_label.grid(row=1, column=0, ipadx=10, ipady=6, padx=10, pady=10)

    global seconds
    seconds = Spinbox(from_=1, to=30)
    seconds.grid(row=1, column=1, ipadx=10, ipady=6, padx=10, pady=10)

    # global record_label
    # record_label = Label(text="")
    # record_label.grid(row=2, columnspan=2, column=0, ipadx=10, ipady=6, padx=10, pady=10)

    recognise_from_record.place(relx=0.5, rely=0.45, anchor="c", height=30, width=130, bordermode=OUTSIDE)
    recognise_from_record.config(text="Start record", command=record_analysis)
    submit.config(text="Back")


def delete_t():
    dim_label.config(text="Enter the track info:")
    recognise_from_file.destroy()
    recognise_from_record.destroy()
    add.destroy()
    delete.place(relx=0.32, rely=0.95, anchor="c", height=30, width=210, bordermode=OUTSIDE)
    delete.config(command=delete_track_info)
    submit.config(text="Back")

    global enter_track_name_del
    global enter_track_author_del

    enter_track_name_del = Label(text="Enter the track name:")
    enter_track_name_del.grid(row=1, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    enter_track_author_del = Label(text="Enter the track artist:")
    enter_track_author_del.grid(row=2, column=0, ipadx=10, ipady=6, padx=10, pady=5)

    global rows_del
    global cols_del

    rows_del = []
    for i in range(2):
        cols_del = []
        for j in range(1):
            enter_field = Entry(relief=RIDGE, text='%d.%d' % (i, j))
            enter_field.grid(row=i + 1, column=j + 1, ipadx=10, ipady=6, padx=10, pady=2)
            cols_del.append(enter_field)
        rows_del.append(cols_del)


def main():
    global root
    root = Tk()
    root.title("Track Recogniser 1.0.0")
    root.geometry("550x550+500+200")

    global dim_label
    global add

    global recognise_from_record

    file_menu = Menu()
    file_menu.add_command(label="Restart", command=restart)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=exitWin)

    main_menu = Menu()
    main_menu.add_cascade(label="Menu", menu=file_menu)
    main_menu.add_cascade(label="Exit", command=exitWin)

    root.config(menu=main_menu)

    dim_label = Label(text="Choose the action to perform:")
    dim_label.grid(columnspan=2, column=0, ipadx=10, ipady=6, padx=10, pady=10)

    add = Button(
        text="Add new track",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=add_t
    )
    add.place(relx=0.5, rely=0.34, anchor="c", height=35, width=210, bordermode=OUTSIDE)

    global recognise_from_file
    recognise_from_file = Button(
        text="Recognise from file",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=recognise_from_file_t
    )
    recognise_from_file.place(relx=0.5, rely=0.4, anchor="c", height=35, width=210, bordermode=OUTSIDE)

    recognise_from_record = Button(
        text="Recognise from record",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=recognise_from_record_t
    )
    recognise_from_record.place(relx=0.5, rely=0.46, anchor="c", height=35, width=210, bordermode=OUTSIDE)

    global delete
    delete = Button(
        text="Delete track",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=delete_t
    )
    delete.place(relx=0.5, rely=0.52, anchor="c", height=35, width=210, bordermode=OUTSIDE)

    global submit
    submit = Button(
        text="Restart",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=restart
    )
    submit.place(relx=0.62, rely=0.95, anchor="c", height=30, width=130, bordermode=OUTSIDE)

    exit = Button(
        text="Exit",
        background="#555",
        foreground="#ccc",
        padx="20",
        pady="8",
        font="16",
        command=exitWin
    )
    exit.place(relx=0.85, rely=0.95, anchor="c", height=30, width=130, bordermode=OUTSIDE)

    root.mainloop()


main()
