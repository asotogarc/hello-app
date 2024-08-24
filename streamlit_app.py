import streamlit as st

# Agregar CSS para cambiar el color de fondo
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0; /* Cambia este valor al color que desees */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write('Hello world')
