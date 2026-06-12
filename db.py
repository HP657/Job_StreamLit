import streamlit as st
from sqlalchemy import create_engine
import pandas as pd


DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_HOST = st.secrets["DB_HOST"]
DB_PORT = st.secrets["DB_PORT"]
DB_NAME = st.secrets["DB_NAME"]

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require",
    pool_pre_ping=True,
)


@st.cache_data(ttl=300)
def load_df(query: str, params=None) -> pd.DataFrame:
    # params가 존재할 때만 전달하고, 없으면 query만 전달하도록 개선
    if params:
        return pd.read_sql(query, engine, params=params)
    else:
        return pd.read_sql(query, engine)