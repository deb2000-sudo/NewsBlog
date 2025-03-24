import os
from crewai import Crew, Process, Task
from app.agents.news_agents import news_researcher, news_writer
from app.utils.tools import tool

def generate_blog_content(topic, salted_api_key):
    try:
        # Debug API key issues if enabled
        debug_api_key = os.environ.get('DEBUG_API_KEY', 'false').lower() == 'true'
        
        # Remove the salt before using the API key
        api_key_salt = os.environ.get('API_KEY_SALT', 'default_salt_value')
        
        # Better approach to extract the actual API key
        if salted_api_key.endswith(api_key_salt):
            actual_api_key = salted_api_key[:-len(api_key_salt)]
        else:
            actual_api_key = salted_api_key  # If no salt is found, use as is
        
        # Print debug info if enabled
        if debug_api_key:
            print(f"Salted key length: {len(salted_api_key)}")
            print(f"Salt length: {len(api_key_salt)}")
            print(f"Extracted key length: {len(actual_api_key)}")
            # Only show first and last 4 chars for security
            masked_key = actual_api_key[:4] + '*' * (len(actual_api_key) - 8) + actual_api_key[-4:] if len(actual_api_key) > 8 else '****'
            print(f"Using API Key (masked): {masked_key}")
        
        # Set the API key in the environment for the agents to use
        os.environ["OPENAI_API_KEY"] = actual_api_key
        
        # Create tasks for the crew
        research_task = Task(
            description=f"Research the topic: {topic}. Focus on latest trends and key insights.",
            expected_output="Comprehensive research notes",
            agent=news_researcher,
            tools=[tool]
        )
        
        write_task = Task(
            description=f"Write a blog post about: {topic}. Make it engaging and informative.",
            expected_output="Complete blog post",
            agent=news_writer,
            tools=[tool]
        )
        
        # Create crew with the configured LLM
        crew = Crew(
            agents=[news_researcher, news_writer],
            tasks=[research_task, write_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = crew.kickoff(inputs={'topic': topic})
        return str(result)
        
    except Exception as e:
        print(f"Error in generate_blog_content: {str(e)}")
        raise Exception(f"Failed to generate blog content: {str(e)}") 