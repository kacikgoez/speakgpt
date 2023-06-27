import azure.cognitiveservices.speech as speechsdk
from gpt import SimpleGPT
from labrador import Labrador, audioFiles
from elevenlabs import play, stream


# Makes ChatGPT API easy to use
gptModel = SimpleGPT()

# Uses threading to create multiple requests. Does not work if you do not have premium ElevenLabs!
lab = Labrador()

count = []
read = True
GPTOff = True

# Replace with your subscription key and service region.
subscription_key = "API KEY FOR AZURE WITH SPEECH RECOG. SUBSCRIPTION"
service_region = "eastus"

speech_config = speechsdk.SpeechConfig(
    subscription=subscription_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config)


def speech_recognized(args):
    # Not the best implementation, but hey ¯\_(ツ)_/¯
    global read
    global count
    global GPTOff
    global gptModel

    result = args.result.text
    if read and GPTOff and result.strip() != "":
        GPTOff = False
        for i in gptModel.respond(result):
            if i["choices"][0].get("delta", {}).get("content") is not None:
                lab.add(i["choices"][0].get("delta", {}).get("content"))
                count.append(i["choices"][0].get("delta", {}).get("content"))
        lab.finish()
        read = False
        GPTOff = True


# Connect the recognized event to the callback function.
speech_recognizer.recognized.connect(speech_recognized)

# Start continuous recognition.
speech_recognizer.start_continuous_recognition()

played = 0
while True:
    try:
        if not read and GPTOff:
            if len(count) > 0:
                x = "".join(count).strip()
                gptModel.add_stream_response(x)
                count = []
            for i in range(len(audioFiles)):
                play(audioFiles[played])
                audioFiles.pop(played)
                played += 1
            read = True
    except KeyboardInterrupt:
        break

# Stop continuous recognition and clean up.
speech_recognizer.stop_continuous_recognition()
