import io
import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder

import speech_recognition as sr

r = sr.Recognizer()


st.set_page_config(page_title="Stealth Co. B2B", layout="wide")

st.title("Audio Recorder and Transcriber")

tabs = st.tabs(["File Uploader", "Audio Recorder"])

with tabs[0]:
    file = st.file_uploader("Upload a file 1", type=["csv", "xlsx"])
    # do_basic_cleaning = st.checkbox("Do basic cleaning 1")  # Commented out as unused

    if file:
        try:
            # Assuming you have a function `clean_data` for cleaning the file
            cleaned_df, cleaned_file = clean_data(file)  # Removed do_basic_cleaning as it's not used
            st.dataframe(cleaned_df)
            st.download_button(
                label="Download cleaned file",
                data=cleaned_file,
                file_name="cleaned_data.csv"
            )
        except Exception as e:
            st.error("Error during cleaning:", str(e))

with tabs[1]:

    audio_bytes = audio_recorder(
        text="Rec_Your_Voice",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="user",
        icon_size="6x",
    )

    if audio_bytes:
        try:
            st.audio(audio_bytes, format="audio/wav")

            type(audio_bytes)
            audio_file = io.BytesIO(audio_bytes)  # Create audio source from bytes
            
            with sr.WavFile(audio_file) as source:
                audio = r.record(source)  # Now pass the audio source
                text_question = r.recognize_google(audio)
                print('Here ' , text_question)


            
        except Exception as e:
            st.error("\n\n\nVoice Not Recognized:"+ e)
        finally:
            audio_bytes = None



    # if audio_bytes:
    #     try:
    #         print(type(audio_bytes))
    #         audio_bytes = io.BytesIO(audio_bytes)  # Create an in-memory audio file from bytes
    #         print(type(audio_bytes))
            
    #         with sr.WavFile(audio_bytes) as source:  # Ensure proper closing of the audio source
    #             audio = r.record(source)  # Now `audio` holds the recorded audio data


    #         #st.audio(audio_bytes, format="audio/wav")
    #         print(type(audio_bytes))

    #     except Exception as e:
    #         st.error("Voice Not Recognized Properly:", e)


        if st.button("Record and Transcribe"):
            # Assuming you have a function `record_and_transcribe_audio`
            record_and_transcribe_audio(audio_bytes)  # Pass the recorded audio bytes
