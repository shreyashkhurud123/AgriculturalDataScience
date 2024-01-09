from pathlib import Path
import streamlit as st
import io
from audio_recorder_streamlit import audio_recorder
import os

# Create the main app structure
st.set_page_config(page_title="Stealth Co. B2B ", layout="wide")  # Optional: set page title and layout

import speech_recognition as sr



r = sr.Recognizer()

import pandas as pd



from pandasai import SmartDataframe
from pandasai import SmartDatalake
from pandasai.llm import OpenAI



import openpyxl
import os

# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain.chat_models import ChatOpenAI
# from langchain.agents.agent_types import AgentType

import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_token =openai_api_key)



#Dealing with missing Data
def fillna_or_drop_numerical(df, threshold=0.05):

    total_entries =  len(df)
    threshold_count = total_entries * threshold

    columns_to_drop = [col for col in df.columns if df[col].count() < threshold_count]
    df.drop(columns=columns_to_drop, inplace=True)

    

    num_vars = [fea for fea in df.columns if df[fea].dtypes != 'O']
    #categ_vars =[fea for fea in df.columns if df[fea].dtypes == 'O']

    
    for col in num_vars:
        missing_count = df[col].isna().sum()

        if missing_count > threshold_count:
            # If missing values exceed the threshold, fill with mean
            #print('Filled_na')
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # If missing values are within the threshold, drop the column
            #print('Dropped_na')
            df = df.dropna(subset=[col])
    
    


    return df


#Function for Data Cleaning
def clean_data(file , basic_cleaning ):
    #print('\tHERE\t',file , '\n\n\n\n\n\n\n' , type(file) , file.name)
    #if basic_cleaning:

    if file.name.rsplit('.', 1)[-1] == 'csv':
        print(file.name)
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    
    if basic_cleaning:
        df = df.drop_duplicates()

        df = fillna_or_drop_numerical(df)

        df = df.dropna()

        # Convert string columns to lowercase
        #df = df.apply(lambda x: x.astype(str).str.lower() if x.dtype == 'O' else x)

        # Remove leading and trailing whitespaces in string columns
        df = df.apply(lambda x: x.strip() if isinstance(x, str) else x)

        # Reset index
        df = df.reset_index(drop=True)

    

    #Saving the cleaned file so that user can export it
    cleaned_file = 'cleaned_' + file.name
    df.to_csv(cleaned_file, index=False)
    return df , cleaned_file
    

#function for Data Analysis
def ask_question(file, question , data_cleaning = 0):

    print('\n\n\n\nhere' , type(file.name) , file.name.rsplit('.', 1)[-1] , '\n\n\n')



    if data_cleaning:
        df , temp = clean_data(file , 1)
    else:
        if file.name.rsplit('.', 1)[-1] == 'csv':
            print(file.name)
            df = pd.read_csv(file ,  delimiter=",")
        else:
            df = pd.read_excel(file)
    

        
    df = SmartDataframe(df , config={"llm": llm} )

    if os.path.exists('./exports/charts/temp_chart.png'):
        os.remove('./exports/charts/temp_chart.png')

    response = df.chat(question)

    if type(response) == str and response.endswith('.png'):
        result = question
        image_path = response
        print(image_path)
        with open(image_path, "rb") as f:
            image = f.read()
    else:
        image = None
        result = response

    return result  , df, image



    return result  , df, image


#function for USDA Data Analysis
def query_data(query):

    #folder = 'Agricultual_data/'

    folder = Path("Agricultual_data")



    df_list = []


    for filename in os.listdir(folder):
        file = folder/filename
        if filename.rsplit('.', 1)[-1] == 'csv':
            #print(file.name)
            df = pd.read_csv(file  ,  delimiter=",")
        else:
            df = pd.read_excel(file)
        df_list.append(df)

    



    
    # file = 'Agricultual_data/Production_Crops_Livestock_Normalized.csv'
    # df = pd.read_csv(file ,  delimiter=",")

    df = SmartDatalake(df_list, config={"llm": llm})



    if os.path.exists('./exports/charts/temp_chart.png'):
        os.remove('./exports/charts/temp_chart.png')


    response = df.chat(query)
    



    if type(response) == str and response.endswith('.png'):
        result = query
        image_path = response
        print(image_path)
        with open(image_path, "rb") as f:
            image = f.read()
    else:
        image = None
        result = response

    return result  , image


    return 0



tabs = st.tabs([
    "Data Cleaning",
    "Data Analysis",
    "USDA Agro"
])

# Data Cleaning tab
with tabs[0]:
    file = st.file_uploader("Upload a file 1", type=["csv", "xlsx"])
    do_basic_cleaning = st.checkbox("Do basic cleaning 1")

    if file:
        try:
            cleaned_df, cleaned_file = clean_data(file, do_basic_cleaning)
            st.dataframe(cleaned_df)
            st.download_button(
                label="Download cleaned file",
                data=cleaned_file,
                file_name="cleaned_data.csv"  # Adjust as needed
            )
        except Exception as e:
            st.error("Error during cleaning:", str(e))

# Data Analysis tab
with tabs[1]:
    file = st.file_uploader("Upload a file 2", type=["csv", "xlsx"])
    text_question = st.text_input("Ask a question")
    do_basic_cleaning = st.checkbox("Do basic cleaning 2")

    audio_bytes = audio_recorder(
        text="Rec_Your_Voice",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="user",
        icon_size="6x",
    )



    if file and audio_bytes:
        try:
            st.audio(audio_bytes, format="audio/wav")
            audio_file = io.BytesIO(audio_bytes)  # Create audio source from bytes
            with sr.WavFile(audio_file) as source:
                audio = r.record(source)  # Now pass the audio source
                text_question = r.recognize_google(audio)
                print(text_question)

            
        except Exception as e:
            st.error("Voice Not Recognized:", e)
        audio_bytes = None


    if file and text_question:
        try:
            answer_text, answer_df, answer_image_link = ask_question(file, text_question, do_basic_cleaning)
            st.write("Answer:", answer_text)
            if answer_image_link:
                st.image(answer_image_link, use_column_width=True)
            st.dataframe(answer_df)
            answer_image_link = None
            answer_text = None
            
        except Exception as e:
            st.error("Error during analysis:", e)

# USDA Agro tab
with tabs[2]:
    text_question = st.text_input("Enter Your Query On Agricultural Data !")


    audio_bytes = audio_recorder(
        text="Question?",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="user",
        icon_size="6x",
    )



    if audio_bytes:
        try:
            st.audio(audio_bytes, format="audio/wav")
            audio_file = io.BytesIO(audio_bytes)  # Create audio source from bytes
            with sr.WavFile(audio_file) as source:
                audio = r.record(source)  # Now pass the audio source
                text_question = r.recognize_google(audio)
                print(text_question)

            
        except Exception as e:
            st.error("Voice Not Recognized:", e)

        audio_bytes = None







    # if query:
    #     try:
    #         query_result = query_data(query)
    #         st.write("Query result:", query_result)
    #     except Exception as e:
    #         st.error("Error during query:", e)

    if text_question:
        try:
            answer_text, answer_image_link = query_data(text_question)
            st.write("Answer:", answer_text)
            if answer_image_link:
                st.image(answer_image_link, use_column_width=True)
            #st.dataframe(answer_df)
            answer_image_link = None
            answer_text = None

            
        except Exception as e:
            st.error("Error during analysis:", e)

if __name__ == "__main__":
    st.write("Start")
    #st.run_app()


