import os
from crewai import Crew, Process
from agents import news_researcher, news_writer
from tasks import research_task, write_task

def generate_blog_content(topic, salted_api_key, salted_serper_api_key=None):
    try:
        # Debug API key issues if enabled
        debug_api_key = os.environ.get('DEBUG_API_KEY', 'false').lower() == 'true'
        
        # Remove the salt before using the API keys
        api_key_salt = os.environ.get('API_KEY_SALT', 'default_salt_value')
        
        # Extract the actual OpenAI API key
        if salted_api_key.endswith(api_key_salt):
            actual_api_key = salted_api_key[:-len(api_key_salt)]
        else:
            # If no salt is found, use as is (fallback)
            actual_api_key = salted_api_key
        
        # Extract the Serper API key if provided
        actual_serper_api_key = None
        if salted_serper_api_key:
            if salted_serper_api_key.endswith(api_key_salt):
                actual_serper_api_key = salted_serper_api_key[:-len(api_key_salt)]
            else:
                actual_serper_api_key = salted_serper_api_key
        
        # Print debug info if enabled
        if debug_api_key:
            print(f"OpenAI API Key - Salted length: {len(salted_api_key)}")
            print(f"Salt length: {len(api_key_salt)}")
            print(f"Extracted OpenAI API key length: {len(actual_api_key)}")
            # Only show first and last 4 chars for security
            masked_key = actual_api_key[:4] + '*' * (len(actual_api_key) - 8) + actual_api_key[-4:] if len(actual_api_key) > 8 else '****'
            print(f"Using OpenAI API Key (masked): {masked_key}")
            
            if actual_serper_api_key:
                masked_serper = actual_serper_api_key[:4] + '*' * (len(actual_serper_api_key) - 8) + actual_serper_api_key[-4:] if len(actual_serper_api_key) > 8 else '****'
                print(f"Using Serper API Key (masked): {masked_serper}")
        
        # Set the API keys in the environment for the agents to use
        os.environ["OPENAI_API_KEY"] = actual_api_key
        
        if actual_serper_api_key:
            os.environ["SERPER_API_KEY"] = actual_serper_api_key
        
        # Create crew with the configured LLM
        crew = Crew(
            agents=[news_researcher, news_writer],
            tasks=[research_task, write_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff(inputs={'topic': topic})
        
        # Ensure we get a string result
        if result is None:
            return "No content was generated. Please try again."
            
        return str(result)  # Ensure we return a string
        
    except Exception as e:
        print(f"Error in generate_blog_content: {str(e)}")
        raise ValueError(f"Failed to generate blog content: {str(e)}") 