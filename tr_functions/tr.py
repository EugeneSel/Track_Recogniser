import time
import numpy as np
from pydub import AudioSegment
from scipy.fftpack import fft
from dao.functions_procedures import *
#from fft_release import custom_fft as fft

RANGE = np.array([40, 80, 120, 180, 300])


def getIndex(freq):
    i = 0
    while RANGE[i] < freq:
        i += 1
    return i


def cust_hash(p1, p2, p3, p4, p5):
    noise_level = 2
    return int((p4 - (p4 % noise_level)) * 10000000 + (p3 - (p3 % noise_level)) * 10000 + \
           (p2 - (p2 % noise_level)) * 100 + (p1 - (p1 % noise_level)))


def read_frames(file_name, read_type, track_name=None, track_artist=None):
    CHUNK = 4096
    sound = AudioSegment.from_file(file_name)
    samples = sound.get_array_of_samples()

    totalSize = len(samples)
    sampledChunkSize = int(totalSize / CHUNK) + 1
    result = np.zeros([sampledChunkSize, CHUNK], dtype=np.complex128)

    for i in range(sampledChunkSize):
        complexArray = np.zeros(CHUNK, dtype=np.complex128)

        for j in range(CHUNK):
            if (CHUNK * i) + j == totalSize:
                complexArray = complexArray[0:j - 1]
                break
            real = samples[(CHUNK * i) + j]
            complexArray[j] = complex(real, 0)

        newComplexArray = fft(complexArray)

        for j in range(len(newComplexArray)):
            result[i, j] = newComplexArray[j]

    points = np.zeros([sampledChunkSize, 5])
    highscores = np.zeros([sampledChunkSize, 5])
    hashes = np.zeros([sampledChunkSize, 2])
    for t in range(sampledChunkSize):
        for freq in range(30, 300):
            mag = abs(result[t, freq])
            index = getIndex(freq)

            if mag > highscores[t, index]:
                highscores[t, index] = mag
                points[t, index] = freq

        h = cust_hash(points[t, 0], points[t, 1], points[t, 2], points[t, 3], points[t, 4])
        if read_type == 'a':
            time.sleep(0.025)
            addTrackHash(h, track_name, track_artist, t)
        elif read_type == 'r':
            hashes[t, 0] = h
            hashes[t, 1] = t

    if read_type == 'a':
        return 0
    elif read_type == 'r':
        return hashes


def add_track(file_name, track_name, track_artist, track_album=None):
    trackList = getTrackList()

    is_exist = False
    for track in trackList:
        if track[0] == track_name and track[1] == track_artist:
            is_exist = True
            break

    if is_exist:
        return "Current track is already present in our database!"
    else:
        src = file_name
        dst = "test.wav"

        # convert wav to mp3
        try:
            sound = AudioSegment.from_mp3(src)
        except FileNotFoundError:
            return "Could not find current file. Please, check the correctness of entered file name!"

        if track_name == '' or track_artist == '':
            if track_name == '':
                return "You can not add new track without name. Please, enter the track name!"
            if track_artist == '':
                return "You can not add new track without artist. Please, enter the track artist!"

        if not track_album or track_album == '':
            track_name = addTrack(track_name, track_artist)
        else:
            track_name = addTrack(track_name, track_artist, track_album)

        sound.export(dst, format="wav")

        read_frames(dst, 'a', track_name, track_artist)

        return "Track %s successfully added!" % track_name


def recognise_track(file_name, audio_time, recognize_type):
    hashes = read_frames(file_name, 'r')

    if recognize_type == 'f':
        match_coefficient = 0.2
        etalon_duration = 20
    else:
        match_coefficient = 0.4
        etalon_duration = 10

    track_number = getNumberOfTracks()[0]
    track_number = track_number[0]
    tracks = getTrackList()
    match_array = np.array([])
    sequences = np.zeros([track_number, 4])
    for i in range(track_number):
        matches = 0
        cur_track = tracks[i]
        track_hashes = getTrackHashList(cur_track[0], cur_track[1])

        sample_time = np.array([])
        track_time = np.array([])
        for j in range(len(hashes)):
            for k in range(len(track_hashes)):
                cur_track_hash = track_hashes[k]
                if hashes[j, 0] == cur_track_hash[0]:
                    sample_time = np.append(sample_time, [j], axis=0)
                    track_time = np.append(track_time, [k], axis=0)
                    matches += 1

        max_sequence = 1
        number_of_valuable_sequences = 0
        matches_left = matches
        j = 0
        while j < matches_left:
            sequence = 1

            k = j + 1
            while k < matches_left:

                if abs(sample_time[j] - sample_time[k]) == abs(
                        track_time[j] - track_time[k]):
                    sequence += 1
                    if sequence > max_sequence:
                        max_sequence = sequence

                    sample_time = np.delete(sample_time, k)
                    track_time = np.delete(track_time, k)
                    k -= 1
                    matches_left -= 1

                k += 1
            if audio_time < etalon_duration:
                if sequence > 4:
                    number_of_valuable_sequences += 1
            else:
                if sequence / audio_time > match_coefficient:
                    number_of_valuable_sequences += 1

            sample_time = np.delete(sample_time, j)
            track_time = np.delete(track_time, j)
            matches_left -= 1
            if matches_left == 0:
                break

        match_info = "%s - %s: " % (cur_track[0], cur_track[1])
        match_array = np.append(match_array, [match_info], axis=0)
        sequences[i, 0] = i
        sequences[i, 1] = max_sequence
        sequences[i, 2] = number_of_valuable_sequences
        sequences[i, 3] = matches

    new_sec = np.array([0, 0, 0, 0])
    for i in range(track_number):
        for j in range(i + 1, track_number):
            if sequences[j, 1] > sequences[i, 1]:
                new_sec[0] = sequences[j, 0]
                new_sec[1] = sequences[j, 1]
                new_sec[2] = sequences[j, 2]
                new_sec[3] = sequences[j, 3]
                sequences[j] = sequences[i]
                sequences[i, 0] = new_sec[0]
                sequences[i, 1] = new_sec[1]
                sequences[i, 2] = new_sec[2]
                sequences[i, 3] = new_sec[3]
            elif sequences[j, 1] == sequences[i, 1] and sequences[j, 2] > sequences[i, 2]:
                new_sec[0] = sequences[j, 0]
                new_sec[1] = sequences[j, 1]
                new_sec[2] = sequences[j, 2]
                new_sec[3] = sequences[j, 3]
                sequences[j] = sequences[i]
                sequences[i, 0] = new_sec[0]
                sequences[i, 1] = new_sec[1]
                sequences[i, 2] = new_sec[2]
                sequences[i, 3] = new_sec[3]
            elif sequences[j, 1] == sequences[i, 1] and sequences[j, 2] == sequences[i, 2] and sequences[j, 3] > sequences[i, 3]:
                new_sec[0] = sequences[j, 0]
                new_sec[1] = sequences[j, 1]
                new_sec[2] = sequences[j, 2]
                new_sec[3] = sequences[j, 3]
                sequences[j] = sequences[i]
                sequences[i, 0] = new_sec[0]
                sequences[i, 1] = new_sec[1]
                sequences[i, 2] = new_sec[2]
                sequences[i, 3] = new_sec[3]

    input_info_array = np.array(["Criteria: max sequence - big sequences - matches"])

    for i in range(track_number):
        if i >= 10:
            break
        input_info = "%d. " %(i + 1) + match_array[int(sequences[i, 0])] + "%d - %d - %d." %(sequences[i, 1], sequences[i, 2], sequences[i, 3])
        input_info_array = np.append(input_info_array, [input_info], axis=0)

    return input_info_array
