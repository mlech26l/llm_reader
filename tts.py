from playsound import playsound
from transformers import AutoProcessor, BarkModel
import scipy
import threading
from transformers import pipeline


class TTS:
    def __init__(self):
        self.processor = None
        self.lock = threading.Lock()
        # for playing note.wav file
        # playsound("/path/note.wav")

    def generate(self, text):
        if self.processor is None:
            print("[TTS] Loading model...")
            # self.processor = AutoProcessor.from_pretrained("suno/bark")
            # self.model = BarkModel.from_pretrained("suno/bark")
            self.processor = AutoProcessor.from_pretrained( "suno/bark-small")
            self.model = BarkModel.from_pretrained("suno/bark-small")
            #
            # self.synthesiser = pipeline("text-to-speech", "suno/bark-small")

            # self.voice_preset = "v2/en_speaker_6"


        MAX_LENGTH = 50
        text = text[:min(MAX_LENGTH, len(text))]
        # inputs = self.processor(text, voice_preset=self.voice_preset)
        inputs = self.processor(text)

        print("[TTS] Generating audio of length", len(text), "characters")
        audio_array = self.model.generate(**inputs)
        audio_array = audio_array.cpu().numpy().squeeze()

        # speech = self.synthesiser(text, forward_params={"do_sample": True})
        # scipy.io.wavfile.write("temp.wav", rate=speech["sampling_rate"], data=speech["audio"])

        sample_rate = self.model.generation_config.sample_rate
        scipy.io.wavfile.write("temp.wav", rate=sample_rate, data=audio_array)
        print("[TTS] Playing...")
        playsound("temp.wav", block=False)
        self.lock.release()

    def generate_background(self, text):
        if self.lock.locked():
            print("[TTS] Already generating, skipping.")
            return
        self.lock.acquire()
        thread = threading.Thread(
            target=self.generate,
            args=(text,),
        )
        thread.start()