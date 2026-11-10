import mysql.connector
import streamlit as st

def get_connection():
    try:
        config = st.secrets["mysql"]

        conn = mysql.connector.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            port=int(config.get("port", 3306))
        )

        return conn

    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None