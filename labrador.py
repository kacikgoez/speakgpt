from elevenlabs import generate, stream, play, set_api_key, Voices
import threading
from keymanager import KeyManager
import azure.cognitiveservices.speech as speechsdk

# API KEY FOR ELEVENLABS
set_api_key("API KEY")

voices = Voices.from_api()
my_voice = voices[0]
my_voice.settings.stability = 0.8
my_voice.settings.similarity_boost = 0.7
audioFiles = {}

keymanager = KeyManager()

# Replace with your subscription key and service region.
subscription_key = "API KEY FOR MICROSOFT AZURE"
service_region = "eastus"

speech_config = speechsdk.SpeechConfig(
    subscription=subscription_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


class Labrador:
    ''' Using ElevenLabs to create speech synthesis the easy and consistent way '''
    buffer: list = []
    min_buffer: int = 5
    ahead_buffer: int = min_buffer + 2
    newSentence: bool = False
    order = 0

    def __init__(self, min_buffer=5) -> None:
        self.min_buffer = min_buffer

    def add(self, word: str):
        global currentOrder
        if word.strip() in ["?", ".", "!", ","]:
            self.newSentence = True
            if len(self.buffer) > 0:
                self.buffer[-1] = self.buffer[-1] + word
        elif word.strip()[0] in ["'", "`"]:
            if len(self.buffer) > 0:
                self.buffer[-1] = self.buffer[-1] + word
        elif word is not None:
            self.newSentence = False
            self.buffer.append(word)

        if len(self.buffer) > 5 and self.newSentence:
            to_say = ("".join(self.buffer))
            thread = threading.Thread(target=speak, args=(to_say, self.order,))
            thread.daemon = True
            thread.start()
            self.order += 1

            self.buffer = []
            self.newSentence = False

    def finish(self):
        to_say = ("".join(self.buffer))
        thread = threading.Thread(target=speak, args=(to_say, self.order,))
        thread.daemon = True
        thread.start()
        self.order += 1

        self.buffer = []
        self.newSentence = False


def speak(to_say, order):
    global currentOrder
    for _ in range(1):
        api_key, sema = keymanager.get_key(to_say)
        print(api_key, sema)
        set_api_key(api_key)
        print("ACQUIRED BY ", order)
        to_say.strip()
        audio = generate(text=to_say, voice=my_voice,
                         model="eleven_monolingual_v1")

        audioFiles[order] = audio
        print("RELEASED BY ", order)
        sema.release()
        break


def speak_microsoft(text):
    speech_config.speech_synthesis_language = "en-US"
    speech_config.speech_synthesis_voice_name = "en-US-ChristopherNeural"

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config)

    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis was successful.")
    else:
        print("Speech synthesis failed. Reason: ", result.reason)
