import streamlit as st
from streamlit.components.v1 import html

def store_in_local_storage(token, username, api_key):
    """Store authentication data in browser's localStorage"""
    js_code = f"""
    <script>
        localStorage.setItem('access_token', '{token}');
        localStorage.setItem('username', '{username}');
        localStorage.setItem('api_key', '{api_key}');
        
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
    js_code = """
    <script>
        const token = localStorage.getItem('access_token') || '';
        const username = localStorage.getItem('username') || '';
        const api_key = localStorage.getItem('api_key') || '';
        
        // Send data back to Streamlit
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: JSON.stringify({token, username, api_key})
        }, "*");
    </script>
    """
    result = html(js_code, height=0)
    if result:
        try:
            import json
            data = json.loads(result)
            return data['token'], data['username'], data['api_key']
        except:
            pass
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