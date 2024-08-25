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

# Función para la autenticación de usuario
def authenticate_user():
    st.session_state['authenticated'] = False
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if username == "usuario1" and password == "contraseña1":
            st.session_state['authenticated'] = True
        else:
            st.error("Usuario o contraseña incorrectos")

# Verificar si el usuario está autenticado
if 'authenticated' not in st.session_state:
    authenticate_user()

if st.session_state.get('authenticated', False):
    page_title = 'Generador de facturas'
    page_icon= "💭"
    layout="wide"
    euro_symbol = '\u20AC'
    total_expenses = 0
    final_price = 0
    df_expense = ""
    css= 'style/main.css'
    file_name_gs = ""
    google_sheet = ""
    sheet_name = ""
    to_email = ""
    sender = "Negocio***"
    code = ""
    scope = ""
    csv ="invoices.csv"
    logo = "Einnova"
    file_authentication_gs= "invoice-tool-authentication.json"
    google_sheet= "invoice-tool"
    sheet_name= "invoices"

    st.set_page_config(
        page_title='Ex-stream-ly- Cool App',
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state='expanded',
        menu_items={
            'Get Help': 'https://www.extremlycoolapp.com/help',
            'Report a bug': 'https://www.extremlycoolapp.com/bug',
            'About': "# This is a header. This is an extremly cool app!"
        }
    )

    hide_st_style = """
        <style>
        #Mainmenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """

    st.markdown(hide_st_style, unsafe_allow_html=True)

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return True
        else:
            return False

    def generate_uid():
        unique_id = uuid.uuid64()
        unique_id_str = str(unique_id)
        return unique_id_str

    def get_month_and_year():
        now = datetime.now()
        month = now.strftime("%B").lower()
        year = datetime.now().year
        return month,year

    if "first_time" not in st.session_state:
        st.session_state.first_time = ""

    if "items" not in st.session_state:
        st.session_state.items_invoice = []

    selected = option_menu(
        menu_title = None,
        options = ["Facturación", "Visualizador de datos"],
        icons=['receipt', 'bar-chart-fill'],
        orientation='horizontal'
    )

    if selected=="Facturación":

        with st.container():
            cc1,cc2 = st.columns(2)
            from_who = cc1.text_input("De: *",placeholder="Quien envía esta factura")
            to_who = cc1.text_input("Cobrar a: *", placeholder="Para quien es la factura")
            email = cc1.text_input("Enviar a: ", placeholder="Enviar correo (opcional)")

            if email:
                validation = validate_email(email)
                if validation == False:
                    st.warning("El E-mail no tiene un formato válido")
                else:
                    st.success("La factura generada sera enviada al destinatario")
            
            cc2.subheader("FACTURA")

            num_invoice = cc2.text_input("#", placeholder='Numero de factura')
            date_invoice = cc2.date_input("Fecha *")
            due_date = cc2.date_input("Fecha de vencimiento")
        
        with st.form("entry_form", clear_on_submit=True):
            if 'expense_data' not in st.session_state:
                st.session_state.expense_data = []
            if "invoice_data" not in st.session_state:
                st.session_state.invoice_data = []
            if "files" not in st.session_state:
                st.session_state.files = []
            
            cex1, cex2, cex3 = st.columns(3)
            articulo = cex1.text_input("Articulo",placeholder="Descripcion del servicio o producto")
            amount_expense = cex2.number_input("Cantidad", step=1, min_value=1)
            precio = cex3.number_input("Precio", min_value=0)
            submitted_expense = st.form_submit_button('Añadir artículo')

            if submitted_expense:
                if articulo == "":
                    st.warning("Añade una descripccion del articulo o servicio")
                else:
                    st.success("Articulo añadido")
                    st.session_state.expense_data.append({"Articulo": articulo,"Cantidad": amount_expense, "Precio": precio, "Total": amount_expense*precio})
                    st.session_state.invoice_data.append({'name': articulo, 'quantity': amount_expense, 'unit_cost':precio})

            if st.session_state.expense_data:
                df_expense = pd.DataFrame(st.session_state.expense_data)
                df_expense_invoice = pd.DataFrame(st.session_state.invoice_data)
                st.subheader("Articulos añadidos")
                st.table(df_expense)
                total_expenses = df_expense['Total'].sum()
                st.text(f"Total:{total_expenses}"+" "+euro_symbol)
                st.session_state.items_invoice = df_expense.to_dict('records')
                st.session_state.invoice_data = df_expense_invoice.to_dict('records')
                final_price = total_expenses

        with st.container():
            cc3, cc4 = st.columns(2)
            notes = cc3.text_area("Notas")
            term = cc4.text_area("Terminos")
            cc3.write("Subtotal: "+ str(total_expenses)+ " "+ euro_symbol)
            impuesto = cc3.number_input("Impuesto %: ", min_value=0)
            if impuesto:
                imp = float("1" + "." + str(impuesto))
                final_price = final_price * imp
            descuento= cc3.number_input("Descuento %: ", min_value=0)
            if descuento:
                final_price = final_price - ((descuento/100)*final_price)
            cc3.write("Total: " + str(final_price) + " " + euro_symbol)
        
        submit = st.button("Enviar")

        if submit:
            if not from_who or not to_who or not num_invoice or not date_invoice or not due_date:
                st.warning("Completa los campos obligatorios")
            elif len(st.session_state.items_invoice)==0:
                st.warning("Añade algún artículo")
            else:
                month,year = get_month_and_year()
                data= [str(from_who),str(to_who),str(logo),str(num_invoice), str(date_invoice),str(due_date),str(st.session_state.items_invoice),notes,term]
                try:
                    with open(csv, mode='r', encoding='latin-1') as file:
                        csv_file = CSVFile(csv)
                        csv_data = csv_file.read()
                        csv_data.append(data)
                        csv_file.write(csv_data)
                        st.success("Información enviada correctamente")

                    # Generar PDF
                    pdf_filename = f"factura_{num_invoice}.pdf"
                    pdf_path = os.path.join("invoices", pdf_filename)
                    generated_pdf = generate_pdf_from_last_csv_row(csv, pdf_path)

                    # Ofrecer el PDF para descarga
                    with open(generated_pdf, "rb") as pdf_file:
                        st.download_button(
                            label="Descargar Factura PDF",
                            data=pdf_file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )
                
                except Exception as e:
                    if "permission denied" in str(e).lower():
                        st.warning("Tienes que cerrar el documento csv para poder actualizar la información desde la aplicación")
                    else:
                        st.error(f"Error: {str(e)}")
else:
    st.warning("Por favor ingresa tu usuario y contraseña")
