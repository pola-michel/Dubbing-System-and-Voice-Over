from flask import Flask, request, jsonify, url_for, send_file
import subprocess
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="http://localhost:4200")

@app.route('/api/process-video', methods=['POST'])
def process_video():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL is required"}), 400
    
    url = data['url']
    try:
        result = subprocess.run(['python', 'dubbing.py', '--link', url], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            return jsonify({"error": f"An error occurred: {result.stderr}"}), 500
        
        filename = 'output_video_final.mp4'
        return jsonify({"message": "Video processed successfully", "download_url": url_for('download_file', filename=filename, _external=True)}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/media-links', methods=['GET'])
def media_links():
    files = {
        "video": url_for('download_file', filename='video.mp4', _external=True),
        "audio": url_for('download_file', filename='audio.srt', _external=True),
        "dubbed_video": url_for('download_file', filename='output_video_final.mp4', _external=True),
        "audio_ar": url_for('download_file', filename='audio_ar.srt', _external=True)
    }
    return jsonify(files)

@app.route('/media/<filename>')
def download_file(filename):
    return send_file(os.path.join(os.getcwd(), filename), as_attachment=True)

@app.route('/api/voice-over', methods=['POST'])
def voice_over():
    data = request.get_json()
    if not data or 'text' not in data or 'speaker_wav' not in data or 'language_idx' not in data:
        return jsonify({"error": "All parameters (text, model_name, speaker_wav, language_idx) are required"}), 400
    
    text = data['text']
    model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
    speaker_wav = data['speaker_wav']
    language_idx = data['language_idx']
    out_path = "voice_over.wav"
    
    try:
        command = f"tts --text \"{text}\" --model_name \"{model_name}\" --speaker_wav \"tones/{speaker_wav}.mp3\" --language_idx \"{language_idx}\" --out_path \"{out_path}\""
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            return jsonify({"error": f"An error occurred: {result.stderr}"}), 500
        
        return jsonify({"message": "Voice-over generated successfully", "download_url": url_for('download_file', filename=out_path, _external=True)}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/api/voice-over', methods=['GET'])
def get_voice_over():
    out_path = "voice_over.wav"
    file = {
        "voice_over": url_for('download_file', filename=out_path, _external=True)
        }
    return jsonify(file)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
