from dotenv import load_dotenv
from crewai_tools import SerperDevTool
import os

load_dotenv()

# Initialize the tool for internet searching capabilities
tool = SerperDevTool() 