from crewai import Crew, Process
from agents import news_researcher, news_writer
from tasks import research_task, write_task
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file
load_dotenv()

def generate_blog(topic):
    # Create crew with the configured LLM
    crew = Crew(
        agents=[news_researcher, news_writer],
        tasks=[research_task, write_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff(inputs={'topic': topic})
    return str(result)  # Convert CrewOutput to string

# Streamlit UI
st.set_page_config(page_title="AI Blog Generator in Real Time", layout="wide")
st.title("AI Blog Generator in Real Time")

# Add some custom CSS to improve the appearance
st.markdown("""
    <style>
    .blog-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# User input
topic = st.text_input("Enter the blog topic:", "AI in Healthcare")

# Generate button
if st.button("Generate Blog"):
    try:
        with st.spinner("Generating your blog..."):
            blog_content = generate_blog(topic)
            
            # Display the blog content in a container with better formatting
            st.markdown("### Generated Blog")
            st.markdown('<div class="blog-content">', unsafe_allow_html=True)
            st.markdown(blog_content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="Download Blog",
                data=blog_content,
                file_name=f"{topic.lower().replace(' ', '_')}_blog.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")