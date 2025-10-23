import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# 🌸 CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="🌷 Traductor ",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🌷 ESTILO PERSONALIZADO CON FONDOS DORADOS Y DETALLES FEMENINOS
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
        color: #5a4b43;
        font-family: 'Trebuchet MS', sans-serif;
    }

    /* Panel lateral */
    section[data-testid="stSidebar"] {
        background-color: #fff8f0;
        border-right: 3px solid #d6b25e;
    }

    /* Títulos principales */
    h1, h2, h3 {
        color: #b48b28;
        font-family: 'Georgia', serif;
        text-align: center;
    }

    /* Botones */
    div.stButton > button {
        background-color: #d6b25e;
        color: white;
        font-weight: bold;
        border-radius: 15px;
        padding: 12px 24px;
        font-size: 17px;
        border: none;
        box-shadow: 2px 2px 8px rgba(212, 176, 82, 0.4);
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #f1d07e;
        color: #5a4b43;
        transform: scale(1.05);
    }

    /* Selectores */
    div[data-baseweb="select"] {
        background-color: #fff4e1 !important;
        border-radius: 10px;
        color: #5a4b43;
    }

    /* Checkbox y radio */
    label {
        color: #5a4b43 !important;
    }

    /* Audios */
    audio {
        border: 2px solid #d6b25e;
        border-radius: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# 🌺 ENCABEZADO PRINCIPAL
st.title("🌷 Traductor Dorado")
st.subheader("✨ Escucho lo que dices y lo traduzco con estilo ✨")

# Imagen decorativa (asegúrate de tener una imagen floral o dorada)
if os.path.exists("OIG7.jpg"):
    image = Image.open("OIG7.jpg")
    st.image(image, width=300)
else:
    st.info("Sube una imagen decorativa llamada 'OIG7.jpg' para personalizar el diseño 🌸")

# 🌼 PANEL LATERAL
with st.sidebar:
    st.markdown("## 💐 Configuración del Traductor")
    st.write("Presiona el botón para hablar. Luego elige el idioma de entrada y salida para escuchar tu traducción 🌟")

# 🌸 BOTÓN DE VOZ
st.markdown("### 🎙️ Toca el botón y habla lo que quieres traducir")
stt_button = Button(label="💛 Escuchar", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# 🌼 PROCESO DE TRADUCCIÓN
if result and "GET_TEXT" in result:
    st.markdown("### 🌸 Texto detectado:")
    st.write(result.get("GET_TEXT"))
    
    try:
        os.mkdir("temp")
    except:
        pass
    
    translator = Translator()
    text = str(result.get("GET_TEXT"))
    
    st.markdown("### 🌼 Parámetros de Traducción")
    
    in_lang = st.selectbox("🌻 Lenguaje de entrada", ("Inglés", "Español", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("🌷 Lenguaje de salida", ("Español", "Inglés", "Coreano", "Mandarín", "Japonés"))
    
    accent = st.selectbox("🌺 Acento", ("Defecto", "Reino Unido", "Estados Unidos", "Australia", "Irlanda", "Sudáfrica", "España"))
    
    # Asignación de códigos
    lang_map = {
        "Inglés": "en", "Español": "es", "Coreano": "ko",
        "Mandarín": "zh-cn", "Japonés": "ja"
    }
    tld_map = {
        "Defecto": "com", "Reino Unido": "co.uk", "Estados Unidos": "com",
        "Australia": "com.au", "Irlanda": "ie", "Sudáfrica": "co.za", "España": "es"
    }
    
    input_language = lang_map.get(in_lang, "en")
    output_language = lang_map.get(out_lang, "es")
    tld = tld_map.get(accent, "com")

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        my_file_name = text[:15] if len(text) > 0 else "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("💫 Mostrar texto traducido")
    
    if st.button("✨ Convertir a Audio ✨"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("#### 🎧 Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)
    
        if display_output_text:
            st.markdown("#### 💬 Texto traducido:")
            st.success(f"**{output_text}**")
    
    def remove_files(n):
        mp3_files = glob.glob("temp/*.mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Eliminado ", f)

    remove_files(7)

