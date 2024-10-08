import pandas as pd
import streamlit as st

def convert_amount_sold(amount_str):
    if pd.isna(amount_str):
        return 0
    
    amount_str = amount_str.replace('ขายแล้ว', '').replace('ชิ้น', '').strip()
    if 'K' in amount_str:
        return int(float(amount_str.replace('K', '')) * 1000)
    elif 'พัน' in amount_str:
        return int(float(amount_str.replace('พัน', '')) * 1000)
    else:
        return int(amount_str)
    

def hide_header_icons():
    hide_github_icon = """
                    <style>
                    .stActionButton {
                        visibility: hidden;
                    }
                    </style>
                    """
    st.markdown(hide_github_icon, unsafe_allow_html=True)

def break_page():
    st.markdown(
        """
            <style type="text/css" media="print">
            div.page-break
            {
                page-break-after: always;
                page-break-inside: avoid;
            }
            </style>
            <div class="page-break">
                <!-- Content goes here -->
            </div>
        """,
        unsafe_allow_html=True,
    )