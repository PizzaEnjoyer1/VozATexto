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
import base64

st.title("TRADUCTOR.")
st.subheader("Escucho lo que quieres traducir.")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal "
             "habla lo que quieres traducir, luego selecciona"
             " la configuración de lenguaje que necesites.")

st.write("Toca el Botón y habla lo que quieres traducir")

stt_button = Button(label=" Escuchar  🎤 (Solo presiona una vez y luego habla)", width=300, height=50)

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
        if (value != "") {
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
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        captured_text = result.get("GET_TEXT")
        st.write(captured_text)

        # Detección de idioma
        detected_language = Translator().detect(captured_text).lang
        language_names = {
            "en": "Inglés",
            "es": "Español",
            "bn": "Bengalí",
            "ko": "Coreano",
            "zh-cn": "Mandarín",
            "ja": "Japonés",
            "fr": "Francés",
            "de": "Alemán",
            "pt": "Portugués",
            "ru": "Ruso"
        }
        st.markdown(f"**El idioma que hablaste fue: {language_names.get(detected_language, 'Desconocido')}**")

    try:
        os.mkdir("temp")
    except:
        pass

    st.title("Texto a Audio")
    translator = Translator()

    text = str(captured_text)
    language_options = [
        "Inglés", "Español", "Bengalí", "Coreano", "Mandarín",
        "Japonés", "Francés", "Alemán", "Portugués", "Ruso"
    ]
    
    in_lang = st.selectbox("Selecciona el lenguaje de Entrada", language_options)
    out_lang = st.selectbox("Selecciona el lenguaje de salida", language_options)

    language_codes = {
        "Inglés": "en",
        "Español": "es",
        "Bengalí": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
        "Francés": "fr",
        "Alemán": "de",
        "Portugués": "pt",
        "Ruso": "ru"
    }

    input_language = language_codes[in_lang]
    output_language = language_codes[out_lang]

    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canada",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )

    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "Español":
        tld = "com.mx"
    elif english_accent == "Reino Unido":
        tld = "co.uk"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Canada":
        tld = "ca"
    elif english_accent == "Australia":
        tld = "com.au"
    elif english_accent == "Irlanda":
        tld = "ie"
    elif english_accent == "Sudáfrica":
        tld = "co.za"

    # Función de conversión de texto a voz
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar el texto")

    # Mostrar GIF de carga mientras se procesa el audio
    loading_gif = 'assets/loading.gif'  # Ruta al GIF de carga

    if st.button("Convertir"):
        gif_placeholder = st.empty()

        # Mostrar GIF de carga
        with gif_placeholder:
            st.markdown(
                f'<img src="data:image/gif;base64,{base64.b64encode(open(loading_gif, "rb").read()).decode()}" width="100" alt="Loading...">',
                unsafe_allow_html=True
            )

        # Simular tiempo de procesamiento
        time.sleep(2)

        # Generar audio y texto traducido
        result, output_text = text_to_speech(input_language, output_language, text, tld)

        # Detener el GIF de carga
        gif_placeholder.empty()

        # Reproducir audio generado
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Mostrar texto traducido si se selecciona
        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f"{output_text}")

    # Función para eliminar archivos antiguos
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)
