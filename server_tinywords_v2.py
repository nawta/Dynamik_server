import zmq
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    AbstractSummaryAction,
)
from datetime import datetime as dt
import openai
from groq import Groq
import spacy
import os
from os.path import join, dirname
from dotenv import load_dotenv
from langdetect import detect
import pathlib
import textwrap
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import anthropic
import re

dotenv_path = join("./", '.env')
load_dotenv(dotenv_path)

endpoint = "https://<your Azure service name>.cognitiveservices.azure.com/" 
azure_key = os.environ.get('AZURE_SPEECH_KEY')

groq_key = os.environ.get('GROQ_API_KEY')
openai.api_key = os.environ.get('OPENAI_API_KEY')
genai.configure(api_key= os.environ.get('GEMINI_API_KEY'))
claude_key = os.environ.get('CLAUDE_API_KEY')

tdatetime = dt.now()

#####################################################################################################
# ツール関数
#####################################################################################################
def write_log(text: str, text_summarized: str)->None:
    with open("logs/log" + tdatetime.strftime("%Y-%m-%d-%H:%M:%S") + ".txt", "a") as f:
        f.write(text.rstrip() + ", " + text_summarized + "\n")            


# 言語判断(language detection)
def detect_language(text: str) -> str:
    try:
        result = detect(text)
    except:
        result = "err"
    return result


######################################################################################################
# Tiny Words
######################################################################################################
# Spacy Languageクラス 変数名をnlpで宣言するのが一般的（spaCy推奨）
def tinywords_spacy(text: str)-> str:
    
    doc = nlp(text)
    ret = []

    # 動詞、名詞、形容詞を抽出. https://qiita.com/kei_0324/items/400f639b2f185b39a0cf
    for token in doc:
        if token.pos_ in ['NOUN', 'VERB', 'ADJ', 'PRON', 'PROPN', 'PART', 'NUM', 'AUX', 'ADV']: 
            ret.append("<size=90>" + token.text + "</size>") #  this<size=50>is</size>a<size=50>pen</size>みたいな感じ
        else:
            ret.append("<size=60>" + token.text + "</size>")
    return ' '.join(ret).replace(" '", "'").replace(" .", ".").replace(" ,", ",")
        
def start_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5557")
    # sudo lsof -i :5557でポートのOccupationを確認

    print("Server startup.")
    
    while True:
        try:
            message = socket.recv_string()
            print(" ")
            print("Received message = %s" % message)

            message = tinywords_spacy(message)

            socket.send_string("%s" % message)
            # socket.send_string("Reply: %s" % message)
        except KeyboardInterrupt:
            socket.close()
            context.destroy() 
        except Exception as e:
            socket.send_string("Error occured: " + e)


if __name__ == "__main__":
    # nlp = spacy.load('en_core_web_sm')
    nlp = spacy.load("en_core_web_sm", exclude=["parser", "tagger", "lemmatizer", "ner"])
    nlp.enable_pipe("senter")
    start_server()

