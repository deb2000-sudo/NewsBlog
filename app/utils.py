from openai import OpenAI

def generate_blog_content(topic, api_key):
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional blog writer."},
                {"role": "user", "content": f"Write a comprehensive blog post about {topic}. Include a title, introduction, main content with subheadings, and conclusion."}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in blog generation: {str(e)}")
        raise Exception("Failed to generate blog content") 