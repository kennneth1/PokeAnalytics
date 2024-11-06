import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')


# If the environment variables are not set (e.g., not in Docker), load them from .env
if db_host is None or db_user is None or db_password is None or db_name is None:
    print("Environment variables not set, attempting to load from .env file...")
    load_dotenv(".env")  # load the .env file
    db_host = os.getenv('DB_HOST')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    
# If no env vars still, we are deployed and live
if db_host is None or db_user is None or db_password is None or db_name is None:
    print("getting st env vars")
    db_host = st.secrets["DB_HOST"]
    db_user = st.secrets["DB_USER"]
    db_password = st.secrets["DB_PASSWORD"]
    db_name = st.secrets["DB_NAME"]

connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
engine = create_engine(connection_string)

@st.cache_data
def query_feature_set(limit=10000):
    try:
        query = "SELECT * FROM feature_set LIMIT %s"
        data = pd.read_sql(query, engine, params=(limit,))
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return None

@st.cache_data
def query_all_card_types(limit=10000):
    try:
        query = """
        SELECT card_type, COUNT(*) as count
        FROM psa_data
        GROUP BY card_type
        HAVING COUNT(*) >= 50 LIMIT %s"""
        data = pd.read_sql(query, engine, params=(limit,))
        return data
    except Exception as e:
        st.error(f"Error: {e}")
        return None