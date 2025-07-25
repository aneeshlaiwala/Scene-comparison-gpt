
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
You are an expert in Indian TV serial screenwriting and narrative evaluation.

Your task is to provide a **professional comparative analysis** of {len(scripts)} episodes of a Hindi-English TV serial. These scripts are written in English and Hindi (in Roman/English script). The focus is not just to summarize, but to compare and evaluate how the script has evolved across episodes and what could be improved.

### DELIVER THE FOLLOWING SECTIONS:

1. **EXECUTIVE SUMMARY**  
   Provide a concise 250-word summary that compares how the story, emotion, pacing, and characters have shifted across the scripts. Highlight what’s working well and where the creative direction seems weak.

2. **SYNOPSIS FOR EACH EPISODE**  
   Provide a 150–200 word summary per script, covering story arc, emotional tone, and setting.

3. **NOTABLE HINDI (ROMANIZED) DIALOGUES**  
   List 10 strong or emotionally significant Hindi-in-English lines across all episodes. Identify the speaker and briefly explain their emotional or narrative importance.

4. **DETAILED COMPARATIVE DEVELOPMENT ANALYSIS**  
   For each area below, provide side-by-side comparison AND explain how the script has improved, stagnated, or declined in Episode 2 vs Episode 1:

   - **Narrative Structure**  
     (What new conflicts are introduced? Are subplots resolving or dragging?)
   - **Character Development**  
     (Which characters have shown growth? Who is becoming flat or inconsistent?)
   - **Dialogues and Language**  
     (Changes in tone, more poetic, sharper, or more cliché? Any noticeable shifts in Hinglish usage?)
   - **Themes and Moral Messaging**  
     (What underlying values or messages are becoming prominent or diluted?)
   - **Emotional & Sentiment Flow**  
     (Pacing of emotional highs/lows—what works, what feels forced?)
   - **Scene Pacing and Visual Rhythm**  
     (Has pacing improved? Are transitions smoother? Visual imagination better?)

5. **RECOMMENDATIONS**  
   Offer creative suggestions on how the storyline, character portrayal, and dialogues can be elevated in the next episodes. Be specific and not generic.

Be detailed, use full paragraphs. Focus on evolution across episodes. Don't summarize section-wise without analysis. Do not translate Hindi lines—interpret them contextually.

Here are the scripts:
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

        st.subheader("🧾 Final Script Evolution Analysis")
        st.markdown(result)
        st.download_button("💾 Download Analysis", result, file_name="script_comparative_analysis.txt")
else:
    st.info("Upload at least one script, select a model, and enter API key.")
