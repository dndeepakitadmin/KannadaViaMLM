import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process as aksharamukha_process
from gtts import gTTS
from io import BytesIO
import pandas as pd

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Malayalam → Kannada Learning",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------ HIDE STREAMLIT UI ------------------ #
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden !important;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ------------------ AUDIO GENERATOR ------------------ #
def make_audio(text, lang="kn"):
    fp = BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# ------------------ PAGE TITLE ------------------ #
st.title("📝 Learn Kannada using Malayalam Script")
st.subheader("മലയാളം ഉപയോഗിച്ച് ಕನ್ನಡ പഠിക്കുക")

text = st.text_area("Enter Malayalam text here:", height=120)

if st.button("Translate"):
    if text.strip():
        try:
            # FULL SENTENCE PROCESSING -----------------------------

            # Malayalam → Kannada sentence
            kannada = GoogleTranslator(source="ml", target="kn").translate(text)

            # Kannada → Malayalam script
            kannada_in_malayalam = aksharamukha_process("Kannada", "Malayalam", kannada)

            # Kannada → English phonetics
            kannada_english = transliterate(kannada, sanscript.KANNADA, sanscript.ITRANS)

            # Kannada audio (sentence)
            audio_sentence = make_audio(kannada)

            # ---------------- OUTPUT ---------------- #
            st.markdown("## 🔹 Translation Results")

            st.markdown(f"**Malayalam Input:**  \n:blue[{text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada}]")
            st.markdown(f"**Kannada in Malayalam Script:**  \n:orange[{kannada_in_malayalam}]")
            st.markdown(f"**English Phonetics:**  \n`{kannada_english}`")

            st.markdown("### 🔊 Kannada Audio (Sentence)")
            st.audio(audio_sentence, format="audio/mp3")
            st.download_button("Download Sentence Audio", audio_sentence, "sentence.mp3")

            # WORD-BY-WORD FLASHCARDS -------------------------------

            st.markdown("---")
            st.markdown("## 🃏 Flashcards (Word-by-Word)")

            mal_words = text.split()
            kan_words = kannada.split()

            # Prevent mismatch crashes (Google sometimes merges or splits words)
            limit = min(len(mal_words), len(kan_words))

            for i in range(limit):
                mw = mal_words[i]
                kw = kan_words[i]

                # Kannada → Malayalam script (word)
                kw_ml = aksharamukha_process("Kannada", "Malayalam", kw)

                # Phonetic (word)
                kw_ph = transliterate(kw, sanscript.KANNADA, sanscript.ITRANS)

                # Audio (word)
                kw_audio = make_audio(kw)

                with st.expander(f"Word {i+1}: {mw}", expanded=False):
                    st.write("**Malayalam word:**", mw)
                    st.write("**Kannada word:**", kw)
                    st.write("**Kannada in Malayalam script:**", kw_ml)
                    st.write("**Phonetics:**", kw_ph)

                    st.audio(kw_audio, format="audio/mp3")
                    st.download_button(
                        f"Download Audio (Word {i+1})",
                        kw_audio,
                        f"word_{i+1}.mp3"
                    )

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.warning("Please enter Malayalam text.")
