import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from frontend_components import store_in_local_storage, get_from_local_storage, clear_local_storage

# Load environment variables
load_dotenv()

# API URL - get from environment or default to localhost
API_URL = os.environ.get("API_URL", "http://localhost:5000/api")

# Page configuration
st.set_page_config(page_title="AI Blog Generator", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .blog-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .sidebar-content {
        padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
    
if 'username' not in st.session_state:
    st.session_state.username = None

if 'api_key' not in st.session_state:
    st.session_state.api_key = None

if 'serper_api_key' not in st.session_state:
    st.session_state.serper_api_key = None

if 'blogs' not in st.session_state:
    st.session_state.blogs = []

# Check for stored auth data in localStorage
try:
    token, username, api_key, serper_api_key = get_from_local_storage()
    # Since localStorage likely won't work, just silently continue
    # The session state initialization above will handle default values
except Exception as e:
    print(f"Error initializing from localStorage: {e}")
    # Silently continue with session state

# Authentication functions
def login(username, password):
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            
            # Print token format for debugging
            token = data['access_token']
            print(f"Received token (first 10 chars): {token[:10]}...")
            
            # Store token in session state
            st.session_state.access_token = token
            st.session_state.username = data['user']['username']
            st.session_state.api_key = data['user']['api_key']
            st.session_state.serper_api_key = data['user']['serper_api_key']
            
            # Store in browser's localStorage (but don't rely on it working)
            try:
                store_in_local_storage(
                    token,
                    data['user']['username'], 
                    data['user']['api_key'],
                    data['user']['serper_api_key']
                )
            except Exception as e:
                # Just log the error but continue - this is non-critical
                print(f"Notice: localStorage may not be fully supported: {e}")
            
            # Fetch blogs - but don't fail if this fails
            try:
                st.session_state.blogs = get_user_blogs()
            except Exception as e:
                print(f"Error fetching blogs: {e}")
                
            return True
        else:
            st.error(f"Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Error during login: {str(e)}")
        return False

def register(username, email, password, api_key, serper_api_key):
    data = {
        "username": username, 
        "email": email, 
        "password": password, 
        "api_key": api_key,
        "serper_api_key": serper_api_key  # Always include serper_api_key
    }
        
    response = requests.post(
        f"{API_URL}/auth/register",
        json=data
    )
    if response.status_code == 201:
        st.success(f"Registration successful!")
        return True
    else:
        st.error(f"Registration failed: {response.json().get('error', 'Unknown error')}")
        return False

def update_api_key(api_key):
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.put(
        f"{API_URL}/auth/update-api-key",
        headers=headers,
        json={"api_key": api_key}
    )
    if response.status_code == 200:
        st.session_state.api_key = api_key
        return True
    return False

def get_user_blogs():
    if not st.session_state.access_token:
        return []
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(f"{API_URL}/blogs/", headers=headers)
        if response.status_code == 200:
            return response.json()['blogs']
        else:
            print(f"Error fetching blogs: {response.status_code} - {response.text}")
            # If we get a 401, log out the user
            if response.status_code == 401:
                st.session_state.access_token = None
                st.session_state.username = None
                st.session_state.api_key = None
                st.session_state.serper_api_key = None
                st.session_state.blogs = []
            return []
    except Exception as e:
        print(f"Exception in get_user_blogs: {e}")
        return []

def generate_blog(topic):
    if not st.session_state.access_token:
        st.error("You must be logged in to generate blogs")
        return None
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(
            f"{API_URL}/blogs/generate",
            headers=headers,
            json={"topic": topic}
        )
        
        if response.status_code == 201:
            data = response.json()
            # Refresh the blogs list
            st.session_state.blogs = get_user_blogs()
            return data['blog']
        else:
            try:
                error_message = response.json().get('error', 'Unknown error')
            except:
                error_message = f"Status code: {response.status_code}"
                
            if response.status_code == 401:
                # Handle unauthorized errors specifically
                st.warning("Your session has expired. Please log in again.")
                st.session_state.access_token = None
                st.session_state.username = None
                st.session_state.api_key = None
                st.session_state.serper_api_key = None
                st.session_state.blogs = []
                st.rerun()
            else:
                st.error(f"Blog generation failed: {error_message}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def refresh_token():
    """Refresh the access token"""
    if not st.session_state.access_token:
        return False
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.post(f"{API_URL}/auth/refresh", headers=headers)
        if response.status_code == 200:
            st.session_state.access_token = response.json()['access_token']
            return True
        return False
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return False

def check_token_validity():
    if not st.session_state.access_token:
        return False
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        response = requests.get(f"{API_URL}/auth/check-token", headers=headers)
        return response.status_code == 200
    except:
        return False

def update_serper_api_key(serper_api_key):
    if not st.session_state.access_token:
        st.error("You must be logged in to update your API key")
        return False
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.put(
        f"{API_URL}/auth/update-serper-api-key",
        headers=headers,
        json={"serper_api_key": serper_api_key}
    )
    if response.status_code == 200:
        st.session_state.serper_api_key = serper_api_key
        return True
    else:
        try:
            error_msg = response.json().get('error', 'Unknown error')
            print(f"Error updating Serper API key: {error_msg}")
        except:
            print(f"Error updating Serper API key: {response.status_code}")
        return False

# Main UI logic
def main():
    # Check token validity at start
    if st.session_state.access_token:
        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        try:
            # Test token validity
            response = requests.get(f"{API_URL}/blogs/", headers=headers)
            if response.status_code == 401:
                st.warning("Your session has expired. Please log in again.")
                st.session_state.access_token = None
                st.session_state.username = None
                st.session_state.api_key = None
                st.session_state.serper_api_key = None
                st.session_state.blogs = []
                st.rerun()
        except:
            pass
    
    # Sidebar for authentication
    with st.sidebar:
        st.header("Account")
        
        # Check if token is valid at the start
        if st.session_state.access_token:
            if not verify_token():
                st.warning("Your session has expired. Please log in again.")
        
        if st.session_state.access_token:
            st.write(f"Logged in as: {st.session_state.username}")
            
            st.subheader("API Key Management")
            # OpenAI API Key Management
            current_api_key = "******" + st.session_state.api_key[-4:] if st.session_state.api_key else "Not set"
            st.text_input("Current OpenAI API Key", value=current_api_key, disabled=True)
            
            new_api_key = st.text_input("New OpenAI API Key", type="password", 
                                       help="Your OpenAI API key for generating blogs")
            if st.button("Update OpenAI API Key"):
                if update_api_key(new_api_key):
                    st.success("OpenAI API key updated successfully")
                else:
                    st.error("Failed to update OpenAI API key")
            
            # Add Serper API Key Management
            st.markdown("---")
            current_serper_key = "******" + st.session_state.serper_api_key[-4:] if st.session_state.serper_api_key else "Not set"
            st.text_input("Current Serper API Key", value=current_serper_key, disabled=True)
            
            new_serper_key = st.text_input("New Serper API Key", type="password", 
                                          help="Your Serper API key for enhanced web search")
            if st.button("Update Serper API Key"):
                if update_serper_api_key(new_serper_key):
                    st.success("Serper API key updated successfully")
                else:
                    st.error("Failed to update Serper API key")
            
            if st.button("Logout"):
                # Clear both session state and localStorage
                st.session_state.access_token = None
                st.session_state.username = None
                st.session_state.api_key = None
                st.session_state.serper_api_key = None
                st.session_state.blogs = []
                
                # Clear browser's localStorage
                clear_local_storage()
                
                st.rerun()
                
        else:
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("Login"):
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            with tab2:
                reg_username = st.text_input("Username", key="reg_username")
                reg_email = st.text_input("Email", key="reg_email")
                reg_password = st.text_input("Password", type="password", key="reg_password")
                reg_api_key = st.text_input("Your OpenAI API Key", type="password", key="reg_api_key", 
                                           help="Required to generate blogs. Will be stored securely.")
                reg_serper_api_key = st.text_input("Your Serper API Key", type="password", key="reg_serper_api_key", 
                                                  help="Required for web search functionality in blog generation.")
                
                if st.button("Register"):
                    if not reg_api_key:
                        st.error("OpenAI API Key is required to register")
                    elif not reg_serper_api_key:
                        st.error("Serper API Key is required to register")
                    else:
                        if register(reg_username, reg_email, reg_password, reg_api_key, reg_serper_api_key):
                            st.info("Registration successful! Please login with your new account")
    
    # Main content
    st.title("AI Blog Generator")
    
    if not st.session_state.access_token:
        st.info("Please login or register to use the blog generator")
        return
    
    if not st.session_state.api_key:
        st.warning("You need to set your API key in the sidebar to generate blogs")
        return
    
    # Blog generation form
    topic = st.text_input("Enter the blog topic:", "AI in Healthcare")
    
    if st.button("Generate Blog"):
        with st.spinner("Generating your blog..."):
            try:
                blog = generate_blog(topic)
                if blog:
                    st.success("Blog generated successfully!")
                    
                    # Display the blog
                    st.subheader(blog['topic'])
                    st.markdown('<div class="blog-content">', unsafe_allow_html=True)
                    st.markdown(blog['content'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download button
                    st.download_button(
                        label="Download Blog",
                        data=blog['content'],
                        file_name=f"{blog['topic'].lower().replace(' ', '_')}_blog.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Previous blogs section
    st.header("Your Previous Blogs")
    
    # Force refresh blogs from server
    blogs = get_user_blogs()
    
    if blogs:
        for blog in blogs:
            with st.expander(f"{blog['topic']} - {blog['created_at']}"):
                st.markdown(blog['content'])
                st.download_button(
                    label="Download",
                    data=blog['content'],
                    file_name=f"{blog['topic'].lower().replace(' ', '_')}_blog.txt",
                    mime="text/plain",
                    key=f"download_{blog['id']}"
                )
    else:
        st.info("You don't have any blogs yet. Create your first blog using the form above!")

def verify_token():
    """Verify if the current token is valid"""
    if not st.session_state.access_token:
        return False
        
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    try:
        # Try to get user blogs as a simple verification
        response = requests.get(f"{API_URL}/blogs/", headers=headers)
        valid = response.status_code == 200
        
        # If token is invalid, clear session
        if not valid and response.status_code == 401:
            st.session_state.access_token = None
            st.session_state.username = None
            st.session_state.api_key = None
            st.session_state.serper_api_key = None
            st.session_state.blogs = []
            
            # Try to clear localStorage but don't fail if it doesn't work
            try:
                clear_local_storage()
            except:
                pass
            
        return valid
    except:
        return False

if __name__ == "__main__":
    main() 