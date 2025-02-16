import streamlit as st
import speech_recognition as sr
import threading
import queue

class SpeechTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.transcript_queue = queue.Queue()
        self.is_listening = False
        self.thread = None

    def transcribe_audio(self):
        with self.microphone as source:
            # Adjust for ambient noise before starting transcription
            self.recognizer.adjust_for_ambient_noise(source)
            st.write("Listening...")

            while self.is_listening:
                try:
                    # Listen for audio input
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    
                    # Recognize speech asynchronously
                    text = self.recognizer.recognize_google(audio)
                    self.transcript_queue.put(text)

                except sr.UnknownValueError:
                    st.write("Could not understand audio")
                except sr.RequestError as e:
                    st.write(f"Could not request results; {e}")
                except Exception as e:
                    st.write(f"An error occurred: {e}")

    def start_transcription(self):
        self.is_listening = True
        self.thread = threading.Thread(target=self.transcribe_audio)
        self.thread.start()

    def stop_transcription(self):
        self.is_listening = False
        if self.thread:
            self.thread.join()

def main():
    st.title("Real-Time Speech Transcription")
    
    # Initialize transcriber
    transcriber = SpeechTranscriber()
    
    # Transcript display area
    transcript_area = st.empty()
    
    # Control buttons
    col1, col2 = st.columns(2)
    
    with col1:
        start_button = st.button("Start Transcription")
    with col2:
        stop_button = st.button("Stop Transcription")
    
    # Transcript storage
    transcript_history = []
    
    # Transcription control logic
    if start_button:
        transcriber.start_transcription()
    
    if stop_button:
        transcriber.stop_transcription()
    
    # Real-time transcript update
    while transcriber.is_listening:
        try:
            # Get transcript without blocking
            transcript = transcriber.transcript_queue.get(block=False)
            transcript_history.append(transcript)
            
            # Display full transcript history
            transcript_area.text_area(
                "Transcript", 
                value="\n".join(transcript_history), 
                height=300
            )
        except queue.Empty:
            pass

if __name__ == "__main__":
    main()