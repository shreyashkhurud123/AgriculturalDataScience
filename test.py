import pandas as pd
import streamlit as st
import openpyxl
import os

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType

import os
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")



import matplotlib
matplotlib.use('TkAgg')



#print('API Key',openai_api_key)

#image_output = gr.Image(None) 

from PIL import Image


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
            print('Filled_na')
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # If missing values are within the threshold, drop the column
            print('Dropped_na')
            df = df.dropna(subset=[col])
    
    


    return df

#======================================================== DATA CLEANING ================================================================================


def clean_data(file_path , basic_cleaning ):
    print('\tHERE\t',file_path)
    #if basic_cleaning:
    if (file_path.rsplit('.', 1)[-1] if '.' in file_path else None) == 'csv':
        print(file_path)
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    
    if basic_cleaning:
        df = df.drop_duplicates()

        df = fillna_or_drop_numerical(df)

        df = df

    return df, None # return None for image output

def ask_question(file, question , data_cleaning = 0):
    
    if data_cleaning:
        df , temp = clean_data(file , 1)
    
    agent = create_pandas_dataframe_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"),
        df,
        verbose=True,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    result = agent.run(question)
    
    print(type(df) , df.columns , len(df))
    #result = df[df['year'] == 2018].sort_values('total_ghg', ascending=False).head(10)[['country', 'total_ghg']]

    # check if the result contains an image path
    has_image = isinstance(result, str) and result.endswith(".png")

    return result , df, has_image


st.title('Data Analysis')

file = st.file_uploader('Upload file', type=['csv', 'xlsx'])
question = st.text_input('Enter your question')
data_cleaning = st.checkbox('Do a Basic Cleaning on this file')

if file and question:
    result, df, has_image = ask_question(file, question, data_cleaning)
    st.write(result)
    st.dataframe(df)
    if has_image:
        st.image(result, use_column_width=True)
