import streamlit as st
from freeGPTFix import Client
from PIL import Image
from io import BytesIO

# Título de la aplicación
st.title("Generador de Imágenes con AI")
st.markdown("Usando el proveedor `pollinations`.")

# Input del usuario
prompt = st.text_input("Ingresa tu prompt para generar una imagen:")

if st.button("Generar Imagen", use_container_width=True):
    if prompt:
        provider = "pollinations"
        st.subheader(f"Usando proveedor: `{provider}`")
        with st.spinner(f"Generando imagen con {provider}..."):
            try:
                # Intentar generar la imagen con el proveedor actual
                image_bytes = Client.create_generation(provider, prompt)
                if image_bytes:
                    try:
                        # Intentar abrir los datos como una imagen
                        image = Image.open(BytesIO(image_bytes))
                        st.image(image, caption=f"Imagen generada por {provider}", use_column_width=True)
                        st.success(f"¡El proveedor `{provider}` funciona correctamente!")
                    except Exception as img_error:
                        # Si no es una imagen, mostrar lo que devolvió el proveedor
                        st.error(f"El proveedor `{provider}` no devolvió una imagen válida. Error: {img_error}")
                        st.info("Respuesta recibida del proveedor (puede ser un mensaje de error o HTML):")
                        # Intentamos decodificar la respuesta como texto para poder leerla
                        st.text(image_bytes.decode('utf-8', errors='ignore'))
                else:
                    st.warning(f"El proveedor `{provider}` no devolvió datos de imagen.")
            except Exception as e:
                st.error(f"El proveedor `{provider}` falló: {e}")
    else:
        st.warning("Por favor, ingresa un prompt.")