import time

from transformers import AutoProcessor, BarkModel
import time
import playsound
from transformers import pipeline
import torch
from datasets import load_dataset
# processor = AutoProcessor.from_pretrained("suno/bark")
# model = BarkModel.from_pretrained("suno/bark")
#
# voice_preset = "v2/en_speaker_6"
#
# inputs = processor("Hello, my dog is cute", voice_preset=voice_preset)

synthesiser = pipeline("text-to-speech", "microsoft/speech_tt5")

embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
# You can replace this embedding with your own as well.



print("generating...")
start = time.time()
speech = synthesiser("Hello, my dog is cooler than you!", forward_params={"speaker_embeddings": speaker_embedding})
# audio_array = model.generate(**inputs)
# audio_array = audio_array.cpu().numpy().squeeze()
print("done")
print("took", time.time() - start, "seconds")

import scipy
scipy.io.wavfile.write("bark_out.wav", rate=speech["sampling_rate"], data=speech["audio"])

# sf.write("speech.wav", speech["audio"], samplerate=speech["sampling_rate"])

# sample_rate = model.generation_config.sample_rate
# scipy.io.wavfile.write("bark_out.wav", rate=sample_rate, data=audio_array)
playsound.playsound("bark_out.wav", block=False)

time.sleep(10)