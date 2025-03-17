from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from asr import transcribe_audio
from llm import generate_response
from tts import text_to_speech
import io

app = FastAPI()

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    # Read audio file from frontend
    audio_bytes = await audio.read()

    # Step 1: ASR - Convert audio to text
    transcript = transcribe_audio(audio_bytes)

    # Step 2: LLM - Generate response
    response_text = generate_response(transcript)

    # Step 3: TTS - Convert response to audio
    audio_response = text_to_speech(response_text)

    # Return audio as a streaming response
    return StreamingResponse(
        io.BytesIO(audio_response),
        media_type="audio/mp3",
        headers={"transcript": transcript, "response": response_text}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)