import os
import ssl
import locale
import argparse
import subprocess
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
from whisper.utils import get_writer
from deep_translator import GoogleTranslator
from subtoaudio import SubToAudio
from pydub import AudioSegment
import sys

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# Set preferred encoding to UTF-8
locale.getpreferredencoding = lambda: "UTF-8"
ssl._create_default_https_context = ssl._create_unverified_context

# Create argument parser
parser = argparse.ArgumentParser(description='Dubbing Parameters')
parser.add_argument('--link', type=str, help='Link of Youtube video', required=True)
parser.add_argument('--tempo', type=int, default=3, help='Tempo value')
args = parser.parse_args()

# Access parameters
link = args.link
tempo = float(args.tempo)

# Function to download YouTube video
def download_video_with_resolution_and_name(youtube_url, save_path, resolution, file_name):
    try:
        yt = YouTube(youtube_url)
        filtered_streams = yt.streams.filter(res=f'{resolution}p', progressive=True, file_extension='mp4', mime_type='video/mp4')
        if not filtered_streams:
            print(f"No streams available for resolution {resolution}p.")
            return
        stream = filtered_streams[0]
        stream.download(output_path=save_path, filename=file_name)
        print("Video downloaded successfully!")
    except Exception as e:
        print("Error:", str(e))

# Download the video
video_url = link
save_directory = os.getcwd()
desired_resolution = 360
custom_file_name = "video.mp4"
download_video_with_resolution_and_name(video_url, save_directory, desired_resolution, custom_file_name)

# Extract audio from the video
mp4_file = os.path.join(save_directory, "video.mp4")
audio_file = os.path.join(save_directory, "audio.mp3")
video_clip = VideoFileClip(mp4_file)
audio_clip = video_clip.audio
audio_clip.write_audiofile(audio_file)
audio_clip.close()
video_clip.close()

# Transcribe audio to generate subtitles
model = whisper.load_model("medium")
result = model.transcribe(audio_file)
txt_writer = get_writer("srt", save_directory)
txt_writer(result, audio_file)

# Translate subtitles
srt_aud_file = audio_file.split('.')[0]
translated_subs = ''
with open(f"{srt_aud_file}.srt", "r", encoding="utf-8") as txt:
    for line in txt.readlines():
        translated_subs += f"{GoogleTranslator(source='en', target='ar').translate(line)}\n"
with open(f"{srt_aud_file}_ar.srt", mode='w', encoding="utf-8") as sub_output:
    sub_output.write(translated_subs)

# Convert translated subtitles to speech
sub = SubToAudio(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
sub_file_name = f'{srt_aud_file}_ar.srt'
subtitle = sub.subtitle(sub_file_name)
sub.convert_to_audio(sub_data=subtitle, output_path=f"{srt_aud_file}_ar", tempo_mode='overflow', speaker_wav=audio_file, language='ar', tempo_limit=tempo)

# Use Spleeter to separate vocals and accompaniment
output_dir = save_directory
subprocess.run(["spleeter", "separate", "-o", output_dir, "-c", "wav", mp4_file], check=True)

# Merge generated audio with the original video's accompaniment
accompaniment_path = os.path.join(output_dir, "video", "accompaniment.wav")
if not os.path.exists(accompaniment_path):
    raise FileNotFoundError(f"File not found: {accompaniment_path}")

# Load and trim the base audio to match the original video duration
base_audio = AudioSegment.from_file(f"{srt_aud_file}_ar.wav")
original_audio = AudioSegment.from_file(audio_file)
base_audio = base_audio.set_frame_rate(44100)
layer_audio = AudioSegment.from_file(accompaniment_path).set_frame_rate(44100)
merged_audio = base_audio.overlay(layer_audio, loop=True)

# Trim the merged audio to the original audio duration
final_audio_duration = len(original_audio)
if len(merged_audio) > final_audio_duration:
    merged_audio = merged_audio[:final_audio_duration]

output_path = 'final_output_audio.wav'
merged_audio.export(output_path, format='wav')

# Combine the final audio with the video
final_video = VideoFileClip(mp4_file).without_audio().set_audio(AudioFileClip(output_path))
final_video.write_videofile("output_video_final.mp4", codec="libx264", audio_codec="aac")

print("Process completed successfully!")
