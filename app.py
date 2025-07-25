import streamlit as st
import os
import openai
import requests

st.set_page_config(page_title="TV Script Comparative Analysis", layout="wide")
st.title("📺 TV Serial Script Comparative Analyzer")
st.markdown("Upload up to **5 scripts**, select an AI model, and get deep narrative insights.")

# ---------------------------
# 1. Upload Scripts
# ---------------------------
uploaded_files = st.file_uploader("📂 Upload up to 5 script files (.txt only)", type=['txt'], accept_multiple_files=True)

# ---------------------------
# 2. Select Model
# ---------------------------
model_choice = st.selectbox("🧠 Choose AI Model", ["GPT-4 (OpenAI)", "Gemini Pro (Google AI)", "Hugging Face"])

# ---------------------------
# 3. Enter API Key
# ---------------------------
api_key = st.text_input("🔑 Enter your API Key for the selected model", type="password")

# ---------------------------
# 4. Generate Analysis
# ---------------------------
if uploaded_files and model_choice and api_key:
    if st.button("🚀 Run Comparative Analysis"):

        def read_scripts(files):
            return [f.read().decode("utf-8") for f in files]

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

        # ---------------------------
        # Call GPT-4 (OpenAI)
        # ---------------------------
        def analyze_with_gpt4(prompt, key):
            openai.api_key = key
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response['choices'][0]['message']['content']

        # ---------------------------
        # Call Gemini Pro (Google AI)
        # ---------------------------
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

        # ---------------------------
        # Call Hugging Face
        # ---------------------------
        def analyze_with_huggingface(prompt, key):
            url = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
            headers = {"Authorization": f"Bearer {key}"}
            response = requests.post(url, headers=headers, json={"inputs": prompt})
            return response.json()[0]['generated_text']

        # ---------------------------
        # Perform Analysis
        # ---------------------------
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

