
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
custom_prompt = st.text_area("➕ Add Additional Instructions (Optional)", placeholder="E.g., include tone analysis, focus on visual cues, explore backstory hints...")

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
You are an expert in Indian television serial screenwriting and professional script evaluation.

The user has uploaded {len(scripts)} scripts. These scripts contain English and Hindi (in English alphabets). DO NOT translate Hindi lines — interpret their tone, emotion, and relevance in context.

You MUST produce an extremely detailed, structured report using the following layout. Ensure comparison and growth tracking across episodes — not summaries per script.

-----------------
1. EXECUTIVE SUMMARY (300 words)
- Compare overall tone, emotion, plot coherence, scene transitions, dialogue maturity
- Highlight what has evolved well from one episode to the next, and what has regressed
- Clearly call out progression using ✅ GOOD, ⚠️ NEEDS WORK, 🔴 CRITICAL markers

-----------------
2. SYNOPSIS PER EPISODE (150–200 words each)
- Short descriptive plot summary with emotional tone, family tension, turning points

-----------------
3. HINDI DIALOGUES
- List 10 emotionally rich Hindi lines written in Roman script
- Mention character name and what makes that line powerful
- Don't translate, just interpret in context

-----------------
4. COMPARATIVE DEVELOPMENT ANALYSIS (STRUCTURED)
For each of the following areas, do a side-by-side comparison between episodes AND explain:
- What improved?
- What got diluted or regressed?
- What new things were introduced and how well?

Areas:
  a. Narrative structure and pacing  
  b. Subplot development  
  c. Character arcs and screen presence  
  d. Dialogue realism, Hinglish balance  
  e. Thematic maturity and symbolism  
  f. Sentiment/emotional tone per episode  
  g. Scene design and cinematic flow  
  h. Continuity and logical flow  
  i. Vocabulary, cultural cues, modern relevance  

-----------------
5. RECOMMENDATIONS (ACTIONABLE)
- What should improve in Episode 3?
- List 5 concrete writing/structure/dialogue recommendations
- Don’t be generic

""" + (f"\n\n### Additional User Prompt:\n{custom_prompt}" if custom_prompt else "") + "\n\n---\n\n" + "\n\n---\n\n".join([f"Script {i+1}:\n{scripts[i]}" for i in range(len(scripts))])

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

        st.subheader("📊 Final Comparative Analysis Report")
        st.markdown(result)
        st.download_button("💾 Download Full Report", result, file_name="final_episode_comparison.txt")
else:
    st.info("Upload at least one script, select a model, and enter API key.")
