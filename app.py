from flask import Flask, jsonify, request
from flask_cors import CORS
import openai
import io
import speech_recognition as sr
import pyttsx3
import time
import logging
import os


app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize an empty list to store messages
messages = []

openai.api_key = os.getenv('OPENAI_API_KEY')
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# testing for the backend functionality
# @app.route ('/')
# def hello():
#     return "Hello World!"

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    try:
        # Get user message from frontend
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
        audio = request.files['audio']

        # ASR using speech_recognition
        logger.info("Processing audio with SpeechRecognition")
        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)
            try:
                user_message = recognizer.recognize_google(audio_data)
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

        # LLM using OpenAI
        logger.info(f"Generating response using LLM: {user_message}")   
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant responding to voice messages. Keep responses concise and conversational."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        ai_response = response.choices[0].message['content'].strip()

        # TTS using pyttsx
        logger.info(f"AI response: {ai_response}")
        audio_buffer = io.BytesIO()
        tts_engine.save_to_file(ai_response, 'temp_response.wav')
        tts_engine.runAndWait()
        with open('temp_response.wav', 'rb') as f:
            audio_buffer.write(f.read())
        audio_buffer.seek(0)

        # Record interaction with latency
        latency = time.time() - start_time
        messages.append({
            "user": user_message,
            "ai": ai_response,
            "timestamp": time.ctime(),
            "latency": f"{latency:.2f}s"
        })

        logger.info(f"Request processed in {latency:.2f}s")
        return jsonify({
            'status': 'success',
            'transcript': user_message,
            'response_text': ai_response,
            'audio': audio_buffer.getvalue().hex(),
            'latency': latency
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 500
    
@app.route ('/api/chat-history', methods=['GET'])
def get_chat_history():
    """"Endpoint to get chat history"""
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
    app.run(debug=True, host='0.0.0.0', port=5000)
