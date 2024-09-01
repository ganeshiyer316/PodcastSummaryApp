import os
import re
from flask import Flask, request, jsonify, send_from_directory
from transformers import pipeline
import yt_dlp

app = Flask(__name__, static_folder='.')

# Load Hugging Face models for summarization
#summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
# Load a smaller model for summarization
summarization_pipeline = pipeline("summarization", model="t5-small")  # T5-small is faster than BART


def extract_video_id(youtube_url):
    # Regular expression to extract the video ID from different YouTube URL formats
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, youtube_url)
    return match.group(1) if match else None

def get_youtube_transcript(youtube_url):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return None

    # Enhanced yt-dlp configuration to fetch subtitles
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,  # Also try to get automatic subtitles
        'subtitleslangs': ['en'],   # Set this to the desired language code
        'subtitlesformat': 'vtt',
        'outtmpl': '%(id)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
            subtitle_file = f'{video_id}.en.vtt'

            if os.path.exists(subtitle_file):
                with open(subtitle_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    transcript = []
                    for line in lines:
                        if '-->' not in line and line.strip() != '':
                            transcript.append(line.strip())
                    return ' '.join(transcript)
            else:
                return None

    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def summarize_text(text, max_chunk_length=400, chunk_limit=20):
    # Split text into smaller chunks
    text_chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)][:chunk_limit]
    summaries = []

    for chunk in text_chunks:
        # Adjust max_length based on input length
        input_length = len(chunk.split())
        max_length = min(250, input_length // 2)  # Ensure max_length is half of the input length or less
        # Generate summary for each chunk
        summary = summarization_pipeline(chunk, max_length=max_length, min_length=30, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    # Combine summaries of all chunks
    combined_summary = " ".join(summaries)

    # Short form summary of the combined summary
    short_summary = summarization_pipeline(combined_summary, max_length=100, min_length=30, do_sample=False)[0]['summary_text']

    return combined_summary, short_summary



@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/summarize', methods=['POST'])
def summarize_youtube():
    youtube_url = request.json.get('youtube_url')
    if not youtube_url:
        return jsonify({'error': 'YouTube URL is required'}), 400

    try:
        transcript = get_youtube_transcript(youtube_url)
        if transcript is None:
            return jsonify({'error': 'No transcript available for this video or transcripts are disabled.'}), 400

        long_summary, short_summary = summarize_text(transcript)

        return jsonify({
            'long_summary': long_summary,
            'short_summary': short_summary
        })

    except Exception as e:
        # Log the error and return a JSON response
        app.logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing the request. Please check the server logs for more details.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
