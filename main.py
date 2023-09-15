import requests
import json
from bs4 import BeautifulSoup
import streamlit as st
import openai
import replicate
import os

BROWSERLESS_API_KEY = 'your key'
openai.api_key = 'your key'
os.environ["REPLICATE_API_TOKEN"] = "your key"


def scrape_website(url: str):
    headers = {'Cache-Control': 'no-cache', 'Content-Type': 'application/json'}
    data = {"url":url}
    data_json = json.dumps(data)
    post_url = f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}"
    response = requests.post(post_url, headers=headers, data=data_json)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        if text != "" and text != None:
            return text
        else:
            st.text("Couldn't fetch article")
            return None

    else:
        print(f"HTTP request failed with status code {response.status_code}")



st.markdown("<h1 style='text-align: center;'>Summarize Anything</h1>", unsafe_allow_html=True)

# Centered text
st.markdown("<p style='text-align: center;'>PASTE URL BELOW: </p>", unsafe_allow_html=True)


def generate_summary(article):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"summarize the following article only mentioning the main ideas, don't go on a seperate tangent, as if a reporter wrote it, use over 180 words: {article}"}],
        temperature=.88
    )
    total_tokens_used_c = response['usage']['total_tokens']
    price = (total_tokens_used_c / 1000) * .0015
    actual_response = response['choices'][0]['message']['content']
    return actual_response

def generate_images(text):
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::7ytneB65",
        messages=[{"role": "system",
                   "content": "You are a prompt engineer who is tasked to write simple visual descriptions to encapsulate abstract text summaries. You will create 3 visual description prompts that take a summary and generate these prompts."},
                  {"role": "user","content": text}],
        temperature=.88
    )
    total_tokens_used_c = response['usage']['total_tokens']
    price = (total_tokens_used_c / 1000) * .0015
    actual_response = response['choices'][0]['message']['content']
    for i in range(2, 4):
        actual_response = actual_response.replace(f"{i}.", "#")
    p = actual_response.split("#")
    for i in p:
        output = replicate.run(
            "stability-ai/sdxl:d830ba5dabf8090ec0db6c10fc862c6eb1c929e1a194a5411852d25fd954ac82",
            input={
                "prompt": f"{i}, RAW candid cinema, 16mm, color graded portra 400 film, remarkable color, ultra realistic, textured skin",
                "negative_prompt": "scary, evil, horrible, ugly, disfigured, disgusting, destroyed"}
        )
        st.image(output[0])

url = st.text_input("")
if url != "":
    print(f"url: {url}")
    try:
        article_text = scrape_website(url)
        #st.write(article_text)
        if article_text != None:
            summary = generate_summary(article_text)

            st.title("Summary:")

            st.write(summary)
            st.text("Generating Images")
            generate_images(summary)
    except:
        st.text("ERROR: THIS ARTICLE CAN'T BE SUMMARIZED")