from moviepy.editor import VideoFileClip
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import os, json
from dotenv import load_dotenv
load_dotenv()
from transformers import pipeline, VitsModel, AutoTokenizer
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from IPython.display import Audio
import torch, scipy

model_id = "masakhane/m2m100_418M_fr_fon_rel_news"
model = M2M100ForConditionalGeneration.from_pretrained(model_id)
tokenizer = M2M100Tokenizer.from_pretrained(model_id)

model_yoruba_tts = VitsModel.from_pretrained("facebook/mms-tts-yor")
tokenizer_yoruba_tts = AutoTokenizer.from_pretrained("facebook/mms-tts-yor")

VIDEO_FOLDER = os.getenv("VIDEO_FOLDER")
AUDIO_FOLDER = os.getenv("AUDIO_FOLDER")
SUBTITLE_FOLDER = os.getenv("SUBTITLE_FOLDER")
STS_FOLDER = os.getenv("STS_FOLDER")

# Fonction pour transcrire un enregistrement vocal en texte
async def upload(video_file, duration, title):
    subtitles_yoruba = []
    subtitles_fon = []
    # video_name_extension = video_file.split("/").pop()
    video_name = video_file.filename.split(".")[0]
    video_path = f"{VIDEO_FOLDER}{video_name}.mp4"
    # video_path = video_file.save(os.path.join(VIDEO_FOLDER, video_name))
    contents = await video_file.read()
    with open(video_path, "wb") as f:
      f.write(contents)
    audio_path = AUDIO_FOLDER+video_name.split(".")[0]+".wav"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)
    r = sr.Recognizer()
    translator = Translator()

    with sr.AudioFile(audio_path) as source:
      try:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data, language='fr-FR')
        yoruba_text = translator.translate(text, dest="yo").text
        inputs = tokenizer_yoruba_tts(yoruba_text, return_tensors="pt")
        with torch.no_grad():
          yo_audio = model_yoruba_tts(**inputs).waveform
        yo_audio_path = STS_FOLDER+video_name+".wav"
        audio = Audio(yo_audio, rate=model_yoruba_tts.config.sampling_rate)
        with open(yo_audio_path, 'wb') as f:
          f.write(audio.data)
      except sr.UnknownValueError:
        raise "error"

    start_time = 0
    limit = False
    while((start_time + duration) <= clip.audio.duration and limit == False):
      if (start_time + duration) > clip.audio.duration:
        duration = clip.audio.duration - start_time
        limit = True
      with sr.AudioFile(audio_path) as source:
        try:
          audio_data = r.record(source, offset=start_time, duration=duration)
          text = r.recognize_google(audio_data, language='fr-FR')
          encoded_source = tokenizer(text.lower(), return_tensors="pt")
          generated_tokens = model.generate(**encoded_source)
          fon_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
          yoruba_text = translator.translate(text, dest="yo").text
          inputs = tokenizer_yoruba_tts(yoruba_text, return_tensors="pt")
          with torch.no_grad():
            yo_audio = model_yoruba_tts(**inputs).waveform
          yo_audio_path = STS_FOLDER+video_name+".wav"
          audio = Audio(yo_audio, rate=model_yoruba_tts.config.sampling_rate)
          with open(yo_audio_path, 'wb') as f:
            f.write(audio.data)
            # print(output_text)
          end_time = start_time + duration
          subtitles_fon.append({
                "text": fon_text,
                "start_time": str(start_time),
                "end_time": str(end_time)  # Durée d'affichage de chaque sous-titre (5 secondes)
            })
          subtitles_yoruba.append({
                "text": yoruba_text,
                "start_time": str(start_time),
                "end_time": str(end_time)  # Durée d'affichage de chaque sous-titre (5 secondes)
          })
        except sr.UnknownValueError:
          break
        start_time = end_time - 3
    video_path = "https://vocom.org/mt/fr/videos/"+video_name+".mp4"
    yo_audio_path = "https://vocom.org/sts/fr/audios/"+video_name+".wav"
    cover_path = "https://vocom.org/mt/fr/covers/"+video_name+".PNG"
    subtitles_data = {
        "subtitles_fon": subtitles_fon,
        "subtitles_yoruba": subtitles_yoruba,
        "title": title,
        "language": "fr",
        "duration": clip.audio.duration,
        "audio_yoruba": yo_audio_path,
        "cover": cover_path,
        "path": video_path
    }
    subtitles_json_path = SUBTITLE_FOLDER+video_name.split(".")[0]+".txt"
    with open(subtitles_json_path, "w") as file:
        file.write(str(subtitles_data))

    return subtitles_data


async def list_videos():
  v_list = []
  fichiers = os.listdir(SUBTITLE_FOLDER)
  for fichier in fichiers:
    path = os.path.join(SUBTITLE_FOLDER, fichier)
    if os.path.isfile(path) and fichier.endswith('.txt'):
      with open(path, 'r', encoding='utf-8') as f:
        v_list.append(f.read())
  
  return v_list
