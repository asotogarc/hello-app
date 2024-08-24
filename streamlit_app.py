import streamlit as st
import re
import csv
import locale
import os
from datetime import datetime
import pandas as pd
import uuid
from class_csv import CSVFile
from google_sheets import GoogleSheet
from generate_invoice_pdf import generate_pdf_from_last_csv_row
from streamlit_elements import ElementsError
from streamlit_option_menu import option_menu
from google_auth_oauthlib.flow import Flow


# Agregar CSS para cambiar el color de fondo, el color del texto y ocultar la cabecera
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f0f0; /* Cambia este valor al color que desees */
    }
    .black-text {
        color: black; /* Cambia el color del texto a negro */
    }
    header {
        display: none; /* Oculta la cabecera */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write('<p class="black-text">Hello world!!!</p>', unsafe_allow_html=True)
