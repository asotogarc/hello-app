import streamlit as st

# Agregar CSS para cambiar el color de fondo y el color del texto
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0; /* Cambia este valor al color que desees */
    }
    .black-text {
        color: black; /* Cambia el color del texto a negro */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write('<p class="black-text">Hello world</p>', unsafe_allow_html=True)
