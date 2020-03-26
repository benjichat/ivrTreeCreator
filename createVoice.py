import string
import random
import os

def createSSML(text):
    """Synthesizes speech from the input string of ssml.

    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/

    Example: <speak>Hello there.</speak>
    """
    from google.cloud import texttospeech
    client = texttospeech.TextToSpeechClient()

    ssml = "<speak> "
    ssml += text
    ssml += "</speak>"

    input_text = texttospeech.types.SynthesisInput(ssml=ssml)

    # Note: the voice can also be specified by name.
    # https://cloud.google.com/text-to-speech/docs/voices for possible voices
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        name='en-GB-Wavenet-A',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    def id_generator(size=5, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    # The response's audio_content is binary.
    audioFile = id_generator()+".mp3"
    with open(os.path.join('static/',audioFile), 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file ' + audioFile)
    
    audioLocation = "https://dca8234f.ngrok.io/static/"+audioFile
    
    return audioLocation