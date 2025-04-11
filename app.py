from flask import Flask, jsonify, request
from flask_cors import CORS
#from deepseek import DeepSeekAPI  # Correct import name based on latest package
from openai import OpenAI
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

# Initialize Deepseek client
client = OpenAI(api_key="deep seek key", base_url="https://api.deepseek.com")
# deepseek_client = DeepSeekAPI(api_key="deepseek key")  


recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    audio_path = "temp_audio.wav"
    response_path = "temp_response.wav"
    
    try:
        if not client:
            return jsonify({
                'status': 'error',
                'message': 'DeepSeek client not initialized'
            }), 500

        # Get user message from frontend
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
        
        audio = request.files['audio']
        audio.save(audio_path)

        try:
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

            # LLM using Deepseek - Correct API call
            logger.info(f"Generating response using Deepseek: {user_message}")
            # response = client.chat.completions.create(
            #     model="deepseek-chat",
            #     messages=[
            #         {"role": "system", "content": "You are a helpful assistant. Keep responses concise."},
            #         {"role": "user", "content": user_message}
            #     ],
            #     max_tokens=150,
            #     temperature=0.7
            # )

            
            # ai_response = response.choices[0].message.content.strip()
            # logger.info(f"AI response generated: {ai_response}")
            ai_response = f"(MOCK) You said: {user_message}"


            # TTS using pyttsx
            audio_buffer = io.BytesIO()
            tts_engine.save_to_file(ai_response, response_path)
            tts_engine.runAndWait()
            
            with open(response_path, 'rb') as f:
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

            return jsonify({
                'status': 'success',
                'transcript': user_message,
                'response_text': ai_response,
                'audio': audio_buffer.getvalue().hex(),
                'latency': latency
            })

        finally:
            # Clean up temporary files
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if os.path.exists(response_path):
                os.remove(response_path)

    except Exception as e:
        logger.error(f"Error in /api/chat: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 500

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