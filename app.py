
import streamlit as st
from openai import OpenAI
import requests
from docx import Document

st.set_page_config(page_title="TV Serial Script Comparative Analyzer", layout="wide")
st.title("📺 TV Serial Script Comparative Analyzer")
st.markdown("Upload up to **5 scripts**, select an AI model, and get deep narrative insights.")

uploaded_files = st.file_uploader(
    "📂 Upload up to 5 script files (.txt or .docx)",
    type=['txt', 'docx'],
    accept_multiple_files=True
)

model_choice = st.selectbox("🧠 Choose AI Model", ["GPT-4 (OpenAI)", "Gemini Pro (Google AI)", "Hugging Face"])
api_key = st.text_input("🔑 Enter your API Key for the selected model", type="password")

def read_scripts(files):
    contents = []
    for f in files:
        if f.name.endswith(".txt"):
            try:
                text = f.read().decode("utf-8")
            except UnicodeDecodeError:
                f.seek(0)
                text = f.read().decode("latin1", errors="ignore")
        elif f.name.endswith(".docx"):
            doc = Document(f)
            text = "\n".join([p.text for p in doc.paragraphs])
        contents.append(text)
    return contents

def analyze_with_gpt4(prompt, key):
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content

def analyze_with_gemini(prompt, key):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key
    }
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    response = requests.post(url, headers=headers, json=body)
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {e}\n{response.text}"

def analyze_with_huggingface(prompt, key):
    url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    try:
        return response.json()[0]['generated_text']
    except Exception as e:
        return f"Error: {e}\n{response.text}"

if uploaded_files and model_choice and api_key:
    if st.button("🚀 Run Comparative Analysis"):
        scripts = read_scripts(uploaded_files)

        prompt = f"""
You are an expert in television drama analysis. Analyze and compare the following {len(scripts)} Hindi TV serial scripts in detail. The scripts contain dialogues in English and Hindi (written in English script). DO NOT translate Hindi parts — instead, extract and highlight them.

Your response should include the following structured sections:
1. EXECUTIVE SUMMARY: Key takeaways about tone, themes, character shifts, and language use.
2. SCRIPT SYNOPSIS: 150–200 word summary for each episode.
3. HINDI DIALOGUES: List 8–10 notable Hindi (Roman-script) lines that reflect character emotion or plot.
4. COMPARATIVE ANALYSIS:
   - Narrative Structure: Beginning, conflict, climax, resolution comparison
   - Character Development: Presence, emotional arc, maturity, conflict
   - Dialogue Style: Hinglish patterns, casual vs poetic tone
   - Themes and Morality: Love, betrayal, revenge, tradition, modernity
   - Sentiment Arcs: Emotional tone changes across scenes
   - Scene Variety and Pacing
   - Visual Imagination and Setting

Make the response comprehensive and creatively narrated.
""" + "\n\n---\n\n".join([f"Script {i+1}:\n{scripts[i]}" for i in range(len(scripts))])

        with st.spinner("Analyzing scripts..."):
            try:
                if model_choice == "GPT-4 (OpenAI)":
                    result = analyze_with_gpt4(prompt, api_key)
                elif model_choice == "Gemini Pro (Google AI)":
                    result = analyze_with_gemini(prompt, api_key)
                elif model_choice == "Hugging Face":
                    result = analyze_with_huggingface(prompt, api_key)
                else:
                    result = "Invalid model selected."
            except Exception as e:
                result = f"Error during analysis: {e}"

        st.subheader("🧾 Detailed Script Analysis")
        st.markdown(result)
        st.download_button("💾 Download Analysis", result, file_name="detailed_script_analysis.txt")
else:
    st.info("Upload at least one script, select a model, and enter API key.")
