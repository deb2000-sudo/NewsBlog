import streamlit as st
from streamlit.components.v1 import html

def store_in_local_storage(token, username, api_key, serper_api_key):
    """Store authentication data in browser's localStorage"""
    js_code = f"""
    <script>
        localStorage.setItem('access_token', '{token}');
        localStorage.setItem('username', '{username}');
        localStorage.setItem('api_key', '{api_key}');
        localStorage.setItem('serper_api_key', '{serper_api_key}');
        
        // Signal to Streamlit that storage is complete
        window.parent.postMessage({{
            type: "streamlit:setComponentValue",
            value: true
        }}, "*");
    </script>
    """
    html(js_code, height=0)

def get_from_local_storage():
    """Retrieve authentication data from browser's localStorage"""
    # Since localStorage interaction doesn't fully work with Streamlit,
    # we'll just return empty values and rely on session state instead
    print("Notice: localStorage access not fully supported in this Streamlit version")
    return None, None, None

def clear_local_storage():
    """Clear all authentication data from localStorage"""
    js_code = """
    <script>
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
        localStorage.removeItem('api_key');
        
        // Signal to Streamlit that clearing is complete
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: true
        }, "*");
    </script>
    """
    html(js_code, height=0) 