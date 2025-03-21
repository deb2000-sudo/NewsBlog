from crewai import Agent
from dotenv import load_dotenv
from tools import tool
load_dotenv()
import os


os.environ["OPENAI_MODEL_NAME"]=os.getenv("OPENAI_MODEL_NAME")
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")



# llm=ChatGoogleGenerativeAI(model="huggingface/starcoder",verbose=True,temperature=0.5,google_api_key=google_api_key)


#creating a Senior reseacher agent with memory and verbose mode

news_researcher=Agent(role="Senior Researcher",
                goal='Uncover ground breaking technologies in {topic}',
                verbose=True,
                memory=True, 
                backstory=("Driven by curiosity, you are at the forefront of""innovation, eager to explore and share knowledge that could change""the world."),
                tools=[tool],
                allow_delegation=True)

#createing a write agent with custom tools responsible in writing news blog
news_writer=Agent(role="Writer",
                goal='Narrate compelling tech stories about {topic}',
                verbose=True,
                memory=True, 
                backstory=(
                    "With a flair for simplifying complex topics,you craft"
                    "engaging narratives that captivate and educate, bringing new"
                    "discoveries to light in an accessible manner."),
                tools=[tool],
                allow_delegation=True)
