import streamlit as st
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from aksharamukha.transliterate import process as aksharamukha_process
from gtts import gTTS
from io import BytesIO
import pandas as pd
import base64

# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Learn Kannada using Malayalam script",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Learn Kannada using Malayalam script — created with Streamlit"
    }
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

# ------------------ SESSION STATE SETUP ------------------ #
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []  # each item: dict with keys below

# ------------------ HELPERS ------------------ #
def generate_kannada_audio_bytes(kannada_text: str) -> bytes:
    """
    Generate Kannada TTS audio bytes using gTTS (lang='kn').
    Returns MP3 bytes.
    """
    fp = BytesIO()
    tts = gTTS(text=kannada_text, lang="kn")
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def add_flashcard(mal_text, kannada_text, kannada_in_malayalam, phonetics, audio_bytes):
    card = {
        "malayalam_input": mal_text,
        "kannada": kannada_text,
        "kannada_in_malayalam": kannada_in_malayalam,
        "phonetics": phonetics,
        "audio_bytes": audio_bytes
    }
    st.session_state.flashcards.append(card)

def flashcards_to_df(cards):
    """Return a DataFrame without the raw audio bytes for CSV export."""
    rows = []
    for c in cards:
        rows.append({
            "malayalam_input": c["malayalam_input"],
            "kannada": c["kannada"],
            "kannada_in_malayalam": c["kannada_in_malayalam"],
            "phonetics": c["phonetics"]
        })
    return pd.DataFrame(rows)

def download_bytes_as_file(bytes_data: bytes, filename: str):
    st.download_button(label=f"Download {filename}", data=bytes_data, file_name=filename, mime="audio/mpeg")

# ------------------ APP UI ------------------ #
st.title("📚 Learn Kannada using Malayalam script")
st.markdown("Input Malayalam text; app will translate to Kannada, show Kannada in Malayalam script, give Latin phonetics, and provide Kannada audio (gTTS).")

with st.expander("Examples / Notes"):
    st.markdown("""
    - Input should be **Malayalam** text (e.g., എന്റെ പേര് രാജുയാണ്).  
    - The app uses `GoogleTranslator` (ml→kn) for translation, `Aksharamukha` for script conversions, and `gTTS` for Kannada audio.  
    - Add translations to Flashcards to build your study set. You can download flashcards as CSV.  
    """)

# Input
mal_text = st.text_area("Enter Malayalam text here (മലയാളം)", height=140, placeholder="Type Malayalam text...")

col1, col2 = st.columns([1,1])
with col1:
    translate_clicked = st.button("Translate")
with col2:
    clear_cards = st.button("Clear flashcards")

if clear_cards:
    st.session_state.flashcards = []
    st.success("All flashcards cleared.")

if translate_clicked:
    if not mal_text.strip():
        st.warning("Please enter some Malayalam text to translate.")
    else:
        try:
            # 1) Malayalam → Kannada translation
            kannada_text = GoogleTranslator(source="ml", target="kn").translate(mal_text)

            # 2) Kannada → Malayalam script (transliteration so Kannada reads in Malayalam letters)
            # Aksharamukha: source 'Kannada', target 'Malayalam'
            kannada_in_malayalam = aksharamukha_process('Kannada', 'Malayalam', kannada_text)

            # 3) Kannada → English phonetics (ITRANS/Latin)
            kannada_phonetics = transliterate(kannada_text, sanscript.KANNADA, sanscript.ITRANS)

            # 4) Kannada audio (gTTS, language code 'kn')
            audio_bytes = generate_kannada_audio_bytes(kannada_text)

            # ---------------- OUTPUT ---------------- #
            st.markdown("### 🔹 Translation Results")
            st.markdown(f"**Malayalam Input:**  \n:blue[{mal_text}]")
            st.markdown(f"**Kannada Translation:**  \n:green[{kannada_text}]")
            st.markdown(f"**Kannada (in Malayalam script):**  \n:orange[{kannada_in_malayalam}]")
            st.markdown(f"**English phonetics (ITRANS):**  \n`{kannada_phonetics}`")

            st.markdown("**Kannada audio (play):**")
            st.audio(audio_bytes, format="audio/mp3")

            # Download audio
            st.download_button("Download Kannada audio (MP3)", data=audio_bytes, file_name="kannada_audio.mp3", mime="audio/mpeg")

            # Button to add to flashcards
            if st.button("➕ Add this to Flashcards"):
                add_flashcard(mal_text, kannada_text, kannada_in_malayalam, kannada_phonetics, audio_bytes)
                st.success("Added to flashcards.")

        except Exception as e:
            st.error(f"Error during translation/transliteration/audio: {e}")

# ------------------ FLASHCARDS SECTION ------------------ #
st.markdown("---")
st.header("🃏 Flashcards (User-added)")
if not st.session_state.flashcards:
    st.info("No flashcards yet. Translate some Malayalam text and click 'Add this to Flashcards'.")
else:
    for idx, card in enumerate(st.session_state.flashcards):
        with st.expander(f"Card {idx+1}: {card['malayalam_input']}", expanded=False):
            st.write("**Malayalam input:**", card["malayalam_input"])
            st.write("**Kannada:**", card["kannada"])
            st.write("**Kannada (in Malayalam script):**", card["kannada_in_malayalam"])
            st.write("**Phonetics (ITRANS):**", f"`{card['phonetics']}`")

            # Play audio
            st.audio(card["audio_bytes"], format="audio/mp3")
            # Download audio per card
            st.download_button(
                label="Download audio (MP3)",
                data=card["audio_bytes"],
                file_name=f"flashcard_{idx+1}_kannada.mp3",
                mime="audio/mpeg"
            )

    # CSV export of flashcards (no audio)
    df = flashcards_to_df(st.session_state.flashcards)
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download flashcards as CSV", data=csv_bytes, file_name="flashcards.csv", mime="text/csv")

    # Export full package (CSV + audio files in zip) - optional advanced (not implemented here)
    st.write("Tip: use the CSV to import into other flashcard apps (Anki, Quizlet) and use the MP3 downloads for pronunciations.")

st.markdown("---")
st.caption("Built with GoogleTranslator, Aksharamukha, indic-transliteration, and gTTS.")
