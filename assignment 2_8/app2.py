import os
from moviepy.editor import AudioFileClip
import speech_recognition as sr
import re
from flask import Flask, request, render_template
import os
from moviepy.editor import AudioFileClip
import speech_recognition as sr
import re

wpm=None
transcript=None
src=None
app = Flask(__name__)

def convert_audio_to_wav(input_path, output_path):
    output_dir = "output_audio"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    audio = AudioFileClip(input_path)
    audio.write_audiofile(output_path, codec='pcm_s16le')

def transcribe_audio(audio_file_path):
    wav_file_path = "converted_audio.wav"
    convert_audio_to_wav(audio_file_path, wav_file_path)

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_sphinx(audio_data)
            global transcript
            transcript=transcription
            return transcription
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"

def count_words(text):
    words = re.findall(r'\w+', text)

    return len(words)

def words_per_minute(audio_file, recognizer):
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        word_count = count_words(text)
        global src
        src = word_count
        duration = len(audio_data.frame_data) / audio_data.sample_rate
        words_per_minute = (word_count / duration) * 60
        global wpm
        wpm = words_per_minute
        print(f"Words Per Minute: {wpm}")
        return words_per_minute
    except sr.UnknownValueError:
        return "Speech recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    message1 = None


    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
        file = request.files['file']
        if file.filename == '':
            message = 'No selected file'
        elif file:
            # Handle the uploaded file (e.g., save it or process it)
            file.save('uploads/' + file.filename)
            message1 = input()
    page = "Transcription: "
    if transcript is not None:
        page += f"{transcript}"

    page += "\nSearched Word occurs "
    if src is not None:
        page += f"{src} Times"

    page += "\nWords Per Minute: "
    if wpm is not None:
        page += f"{wpm:.2f}"

    #page = f"Transcription: {transcript}\nSearched Word occures {src} Times\n Words Per Minute: {wpm:.2f}"

    return render_template('upload.html', message=page)


def input():
    audio_file_path = "uploads/sample.mp3"  # Replace with the actual path to your input MP3 file
    recognizer = sr.Recognizer()  # Initialize the recognizer here
    transcription = transcribe_audio(audio_file_path)
    search_word = request.form.get('search_word')

    #search_word = "all"  # Replace with the word you want to search for

    print("Transcription:")
    print(transcription)

    pattern = re.compile(r'\b' + re.escape(search_word) + r'\b', re.IGNORECASE)
    matches = re.findall(pattern, transcription)

    if matches:
        print(f"Found '{search_word}' {len(matches)} time(s) in the transcription.")
    else:
        print(f"'{search_word}' not found in the transcription.")

    wpm = words_per_minute("converted_audio.wav", recognizer)
    global message

    message=""

    if isinstance(wpm, str):
        message =wpm

    else:
        message=f"Words Per Minute: {wpm:.2f}"
    return render_template('upload.html', word_count=message)

        #return render_template('upload.html',message1=text)




if __name__ == '__main__':
    app.run(debug=True)
# import os
# import re
# from flask import Flask, request, render_template
# import speech_recognition as sr
# from moviepy.editor import AudioFileClip
# import whisper
#
#
# app = Flask(__name__)
#
# def convert_audio_to_wav(input_path, output_path):
#     output_dir = "output_audio"
#
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#
#     audio = AudioFileClip(input_path)
#     audio.write_audiofile(output_path, codec='pcm_s16le')
#
# def transcribe_audio(audio_file_path):
#     wav_file_path = "converted_audio.wav"
#     convert_audio_to_wav(audio_file_path, wav_file_path)
#
#     # Load the Whisper model
#     model = whisper.load_model("base")
#
#     # Transcribe the file
#     transcription = model.transcribe("converted_audio.wav")
#
#     # Print the transcription
#     return transcription
#     #
#     # recognizer = sr.Recognizer()
#     #
#     # try:
#     #     with sr.AudioFile(wav_file_path) as source:
#     #         audio_data = recognizer.record(source)
#     #         transcription = recognizer.recognize_sphinx(audio_data)
#     #         return transcription
#     # except sr.UnknownValueError:
#     #     return "Could not understand audio"
#     # except sr.RequestError as e:
#     #     return f"Could not request results from Google Web Speech API; {e}"
#
# def count_words(text):
#     words = re.findall(r'\w+', text)
#     return len(words)
#
# def words_per_minute(audio_file, recognizer):
#     with sr.AudioFile(audio_file) as source:
#         audio_data = recognizer.record(source)
#
#     try:
#         text = recognizer.recognize_google(audio_data)
#         word_count = count_words(text)
#         duration = len(audio_data.frame_data) / audio_data.sample_rate
#         words_per_minute = (word_count / duration) * 60
#         return words_per_minute
#     except sr.UnknownValueError:
#         return "Speech recognition could not understand audio"
#     except sr.RequestError as e:
#         return f"Could not request results from Google Speech Recognition service; {e}"
#
# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     message = None
#     message1 = None
#     word=None
#
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             message = 'No file part'
#         file = request.files['file']
#         if file.filename == '':
#             message = 'No selected file'
#         elif file:
#             # Handle the uploaded file (e.g., save it or process it)
#             file.save('uploads/' + file.filename)
#             message = 'File uploaded successfully'
#             audio_file_path = 'uploads/' + file.filename
#
#             # Transcribe the uploaded audio
#             transcription = transcribe_audio(audio_file_path)
#             message1 = transcription
#
#     return render_template('upload.html', message=message, message1=message1)
#
# if __name__ == '__main__':
#     app.run(debug=True)
