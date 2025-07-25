import streamlit as st
import openai
import requests
from docx import Document

st.set_page_config(page_title="TV Serial Script Comparative Analyzer", layout="wide")
st.title("📺 TV Serial Script Comparative Analyzer")
st.markdown("Upload up to **5 scripts**, select an AI model, and get deep narrative insights.")

# -------------------------------
# File Upload Section
# -------------------------------
uploaded_files = st.file_uploader(
    "📂 Upload up to 5 script files (.txt or .docx)",
    type=['txt', 'docx'],
    accept_multiple_files=True
)

# -------------------------------
# Model Selection
# -------------------------------
model_choice = st.selectbox("🧠 Choose AI Model", ["GPT-4 (OpenAI)", "Gemini Pro (Google AI)", "Hugging Face"])

# -------------------------------
# API Key Input
# -------------------------------
api_key = st.text_input("🔑 Enter your API Key for the selected model", type="password")

# -------------------------------
# Script Reader with Error Handling
# -------------------------------
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

# -------------------------------
# Model Callers
# -------------------------------
def analyze_with_gpt4(prompt, key):
    openai.api_key = key
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response['choices'][0]['message']['content']

def analyze_with_gemini(prompt, key):
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    response = requests.post(url, headers=headers, json=body)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error: {e}\n{response.text}"

def analyze_with_huggingface(prompt, key):
    url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {"Authorization": f"Bearer {key}"}
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    try:
        return response.json()[0]['generated_text']
    except Exception as e:
        return f"Error: {e}\n{response.text}"

# -------------------------------
# Analysis Trigger
# -------------------------------
if uploaded_files and model_choice and api_key:
    if st.button("🚀 Run Comparative Analysis"):
        scripts = read_scripts(uploaded_files)

        prompt = f"""Compare and analyze the following {len(scripts)} Hindi TV serial scripts.

Do a detailed comparative breakdown of:
1. Narrative structure (beginning, conflict, resolution)
2. Character development and screen presence
3. Dialogue style and language (code-mixed Hinglish, formal, casual)
4. Sentiment/emotion arc per episode
5. Themes or moral messaging
6. Scene transitions and pacing
7. Any plot inconsistencies or unique twists

Scripts:
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

        st.subheader("🧾 Analysis Result")
        st.markdown(result)
        st.download_button("💾 Download Analysis", result, file_name="script_analysis.txt")
else:
    st.info("Upload at least one script, select a model, and enter API key.")
