from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import io
import speech_recognition as sr
import time
import logging
import os
from gtts import gTTS  
from pydub import AudioSegment #for turning mp3 to wav

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize an empty list to store messages
messages = []

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "Please create your own deepseek api key here"  

recognizer = sr.Recognizer()

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    audio_path = "temp_audio.wav"
    response_path = "temp_response.wav"
    
    try:
        # Get user message from frontend
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
        
        audio = request.files['audio']
        audio.save(audio_path)

        # ASR using speech_recognition
        logger.info("Processing audio with SpeechRecognition")
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            try:
                user_message = recognizer.recognize_google(audio_data)
                logger.info(f"Recognized text: {user_message}")
            except sr.UnknownValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Could not understand audio'
                }), 400
            except sr.RequestError as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Speech recognition error: {str(e)}'
                }), 500

        # LLM using Deepseek API
        logger.info(f"Generating response using Deepseek: {user_message}")
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Keep responses concise."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'DeepSeek API error: {response.text}'
            }), 500
            
        response_data = response.json()
        ai_response = response_data['choices'][0]['message']['content'].strip()
        logger.info(f"AI response generated: {ai_response}")

        # TTS using gTTS and convert to WAV
        try:
            # Generate MP3 with gTTS
            tts = gTTS(text=ai_response, lang='en')
            temp_mp3_path = "temp_response.mp3"
            tts.save(temp_mp3_path)

            # Convert MP3 to WAV using pydub
            audio = AudioSegment.from_mp3(temp_mp3_path)
            audio.export(response_path, format="wav", codec="pcm_s16le", parameters=["-ar", "44100"])

            # Read WAV file into buffer
            audio_buffer = io.BytesIO()
            with open(response_path, 'rb') as f:
                audio_buffer.write(f.read())
            audio_buffer.seek(0)

            # Clean up temporary MP3 file
            if os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)
        except Exception as tts_error:
            logger.error(f"TTS failed: {str(tts_error)}")
            raise
        
        # Record interaction with latency
        latency = time.time() - start_time
        messages.append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": time.ctime(),
            "latency": f"{latency:.2f}s"
        })

        return jsonify({
            'status': 'success',
            'transcript': user_message,
            'response_text': ai_response,
            'audio': audio_buffer.getvalue().hex(),
            'latency': latency
        })
        audio_hex = audio_buffer.getvalue().hex()
        logger.info(f"Audio hex length: {len(audio_hex)}")

    except Exception as e:
        logger.error(f"Error in /api/chat: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 500
    finally:
        # Clean up temporary files
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(response_path):
            os.remove(response_path)

@app.route('/api/chat-history', methods=['GET'])
def get_chat_history():
    """Endpoint to get chat history"""
    try:
        return jsonify({
            'status': 'success',
            'messages': messages
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)