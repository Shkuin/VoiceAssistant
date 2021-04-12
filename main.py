import json
import threading
import time

import pyaudio
import pyttsx3
import speech_recognition as sr
from vosk import KaldiRecognizer, Model


def speak(data):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0')
    engine.say(data)
    engine.runAndWait()


# Отдельный поток


def record_recognize_audio(*args: tuple):
    recognized_data = ""
    with microphone as source:
        try:
            speak("Я слушаю вас! ")
            print("я вас слушаю!")
            audio = recognizer.listen(source)

        except sr.WaitTimeoutError:
            speak("Сэр, проверьте ваш микрофон, я вас не слышу...")

    try:
        print("сейчас что-нибудь пиздану...")
        recognized_data = recognizer.recognize_google(audio, language="ru").lower()

    except sr.UnknownValueError:
        speak("Мне не удалось вас понять, извините, сэр, но вы можете повторить, а пока я перейду в режим горячего слова.")
        return

    except sr.RequestError:
        speak("Проверьте ваше интернет соединение, сэр, а пока я перейду в автономный режим.")
        offline_record_recognize_audio()

    return recognized_data


def offline_record_recognize_audio():
    model = Model(r"D:\pythonProject1\models")  # полный путь к модели
    rec = KaldiRecognizer(model, 8000)
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=8000,
        input=True,
        frames_per_buffer=8000
    )
    stream.start_stream()

    while True:
        data = stream.read(4000)
        if len(data) == 0:
            break

        print(rec.Result() if rec.AcceptWaveform(data) else rec.PartialResult())

    print(rec.FinalResult())


def hot_words_listen():
    model = Model("model")
    rec = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            x = json.loads(rec.Result())
            print(x["text"])
            if x["text"] == "маша":
                return True
            elif x["text"]=="поговорим потом":
                speak("Ладно, досвидания")
                return False


if __name__ == "__main__":  # так это условие никак не повлияет на код import-а
    recognizer = sr.Recognizer()  # целью экземпляра являетсся распознование речи
    microphone = sr.Microphone()  # создаем объект микрофон, для начала захвата звука
    # ( аргументом пердаем необходимый фикрофон для прослушивания ) из списка микрофонов
    # device_index = 3 Например

    while True:
        if not hot_words_listen():
            break
        voice_input = record_recognize_audio()
        if voice_input is not None:
            speak(voice_input)
