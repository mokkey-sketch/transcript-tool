from google.oauth2.service_account import Credentials
import streamlit as st
import json
import gspread

def get_gc():
    # These are the two necessary scopes for gspread to function
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # Load credentials from Streamlit Secrets
    creds_dict = json.loads(st.secrets["GCP_CREDENTIALS"])
    
    # Create credentials with the specific scopes attached
    creds = Credentials.from_service_account_info(
        creds_dict, 
        scopes=SCOPES
    )
    
    return gspread.authorize(creds)
