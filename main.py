from pytube import YouTube
from transformers import pipeline
import whisper
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Initialize the summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def download_audio(youtube_url):
    try:
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_file = audio_stream.download(filename="audio.mp3")
        return audio_file
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def transcribe_audio(audio_file):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    return result['text']

def summarize_text(text):
    # Summarize the text using the NLP model
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False, clean_up_tokenization_spaces=True)
    return summary[0]['summary_text']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    youtube_url = request.form['youtube_url']
    agenda_input = request.form['agenda']  # Ensure agenda input is received from form

    # Step 1: Download and check if audio is downloaded correctly
    audio_file = download_audio(youtube_url)
    if audio_file is None:
        return jsonify({"error": "Failed to download audio from YouTube."}), 500

    # Convert agenda input to a dictionary
    agenda = {}
    for line in agenda_input.splitlines():
        if line.strip():
            time_str, topic = line.split(')', 1)
            minutes, seconds = map(int, time_str.strip('()').split(':'))
            time_in_seconds = minutes * 60 + seconds
            agenda[topic.strip()] = time_in_seconds

    # Step 2: Transcribe audio
    full_transcript = transcribe_audio(audio_file)

    # Step 3: Segment transcript and generate summaries
    summaries = {}
    agenda_items = list(agenda.items())

    for i in range(len(agenda_items)):
        topic, start = agenda_items[i]
        end = agenda_items[i + 1][1] if i + 1 < len(agenda_items) else len(full_transcript)
        segment = full_transcript[start:end]
        summary = summarize_text(segment)
        summaries[topic] = summary

    return jsonify(summaries)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
