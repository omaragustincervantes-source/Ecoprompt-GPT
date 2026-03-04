import streamlit as st
from openai import OpenAI
import os

# -----------------------------
# CONFIGURE OPENAI
# -----------------------------

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# SESSION STATE
# -----------------------------

if "daily_energy" not in st.session_state:
    st.session_state.daily_energy = 0.0

if "total_savings" not in st.session_state:
    st.session_state.total_savings = 0.0

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# ENERGY ESTIMATION
# -----------------------------

def calculate_energy_from_tokens(tokens):
    # Estimated kWh per 1000 tokens (science-fair friendly estimate)
    return tokens * 0.000002


# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}
textarea {
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------

st.title("🌿 EcoPrompt Pro")
st.write("Measure real AI token usage and reduce digital energy waste 🌎")

# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.title("🌎 Daily Impact Tracker")

st.sidebar.write(f"Energy Used Today: {st.session_state.daily_energy:.6f} kWh")
st.sidebar.write(f"Energy Saved Today: {st.session_state.total_savings:.6f} kWh")

if st.sidebar.button("🔄 Reset Daily Tracker"):
    st.session_state.daily_energy = 0.0
    st.session_state.total_savings = 0.0
    st.session_state.history = []
    st.success("Tracker Reset!")

# -----------------------------
# USER INPUT
# -----------------------------

user_prompt = st.text_area("Enter your AI prompt below:")

# -----------------------------
# MAIN BUTTON
# -----------------------------

if st.button("Analyze with Real AI 🌿"):

    if user_prompt.strip() == "":
        st.warning("Please enter a prompt first.")
    else:

        # -----------------------------
        # ORIGINAL AI RESPONSE
        # -----------------------------

        original_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_prompt}]
        )

        original_tokens = original_response.usage.total_tokens
        original_energy = calculate_energy_from_tokens(original_tokens)

        # -----------------------------
        # AI REWRITE PROMPT
        # -----------------------------

        rewrite_instruction = f"""
Rewrite this prompt to be shorter, clearer, and more energy-efficient
while keeping the same meaning:

{user_prompt}
"""

        improved_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": rewrite_instruction}]
        )

        improved_prompt = improved_response.choices[0].message.content
        improved_tokens = improved_response.usage.total_tokens
        improved_energy = calculate_energy_from_tokens(improved_tokens)

        # -----------------------------
        # CALCULATE SAVINGS
        # -----------------------------

        energy_saved = original_energy - improved_energy
        percent_saved = (energy_saved / original_energy) * 100 if original_energy > 0 else 0

        st.session_state.daily_energy += original_energy
        st.session_state.total_savings += max(energy_saved, 0)

        st.session_state.history.append({
            "original": user_prompt,
            "improved": improved_prompt,
            "saved": percent_saved
        })

        # -----------------------------
        # DISPLAY RESULTS
        # -----------------------------

        st.subheader("📊 Token Usage")

        st.write(f"Original Tokens Used: {original_tokens}")
        st.write(f"Improved Tokens Used: {improved_tokens}")

        st.subheader("⚡ Energy Comparison")

        st.write(f"Original Energy: {original_energy:.6f} kWh")
        st.write(f"Improved Energy: {improved_energy:.6f} kWh")

        st.success(f"You saved approximately {percent_saved:.1f}% energy!")

        st.subheader("✨ AI Suggested Improved Prompt")
        st.info(improved_prompt)

        st.subheader("🤖 Original AI Response")
        st.write(original_response.choices[0].message.content)

# -----------------------------
# HISTORY
# -----------------------------

if len(st.session_state.history) > 0:
    st.subheader("📜 Recent Prompt History")

    for i, item in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.write(f"*Attempt {i}*")
        st.write("Original:", item["original"])
        st.write("Improved:", item["improved"])
        st.write(f"Energy Saved: {item['saved']:.1f}%")
        st.write("---")

# -----------------------------
# SCIENCE FAIR MODE
# -----------------------------

with st.expander("🔬 Science Fair Explanation for Judges"):
    st.write("""
This version uses real OpenAI token usage data.
Tokens represent pieces of words processed by AI.
More tokens require more computational power.
More computation requires more electricity.
This app estimates energy use based on token count
to demonstrate digital sustainability.
""")