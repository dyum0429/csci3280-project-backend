from flask import Flask, jsonify, request
from flask_cors import CORS
import openai


app = Flask(__name__)
CORS(app)

# Initialize an empty list to store messages
messages = []

@app.route ('/')
def hello():
    return "Hello World!"

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Get user message from frontend
        data = request.get_json()
        user_message = data.get('message', '')
        print (user_message)

        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",  
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant responding to voice messages. Keep responses concise and conversational."},
        #         {"role": "user", "content": user_message}
        #     ],
        #     max_tokens=150,
        #     temperature=0.7
        # )
        # ai_response = response.choices[0].message['content'].strip()
        # return jsonify({
        #     'status': 'success',
        #     'response': ai_response
        # })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f"Error: {str(e)}"
        }), 500
    
@app.route ('/api/chat', methods=['GET'])
def get_message():
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

@app.route('/api/chat/<int:message_id>', methods=['PUT'])
def update_message(message_id):
    try:
        if message_id >= len(messages) or message_id < 0:
            return jsonify({
                'status': 'error',
                'message': 'Message ID out of range'
            }), 404

        data = request.get_json()
        new_content = data.get('content', '')

        if not new_content:
            return jsonify({
                'status': 'error',
                'message': 'No content provided'
            }), 400

        # Update the message content
        messages[message_id]['content'] = new_content

        return jsonify({
            'status': 'success',
            'message': messages[message_id]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)




# from fastapi import FastAPI, UploadFile, File
# from fastapi.responses import StreamingResponse
# from asr import transcribe_audio
# from llm import generate_response
# from tts import text_to_speech
# import io

# app = FastAPI()

# @app.post("/voice-chat")
# async def voice_chat(audio: UploadFile = File(...)):
#     try:
#         # Read audio file from frontend
#         audio_bytes = await audio.read()
    
#         # Step 1: ASR - Convert audio to text
#         transcript = transcribe_audio(audio_bytes)
    
#         # Step 2: LLM - Generate response
#         response_text = generate_response(transcript)
    
#         # Step 3: TTS - Convert response to audio
#         audio_response = text_to_speech(response_text)
    
#         # Return audio as a streaming response
#         return StreamingResponse(
#             io.BytesIO(audio_response),
#             media_type="audio/mp3",
#             headers={"transcript": transcript, "response": response_text}
#         )
#     except Exception as e:
#         return {"error": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)