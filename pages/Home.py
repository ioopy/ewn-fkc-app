import streamlit as st
from menu import menu_with_redirect
from utils.func import hide_header_icons

menu_with_redirect()
hide_header_icons()

st.title("เส้นไข่ขาว")
st.write("")

with open("data/ewn.pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

st.download_button(label="Export Report",
                    data=PDFbyte,
                    file_name="ewn.pdf",
                    mime='application/octet-stream')


