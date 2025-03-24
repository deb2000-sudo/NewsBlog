from crewai import Agent

# Create the researcher agent
news_researcher = Agent(
    role='Research Analyst',
    goal='Conduct thorough research on given topics and identify key trends and insights',
    backstory="""You are an expert research analyst with years of experience in 
    analyzing trends and gathering comprehensive information on various topics.""",
    verbose=True,
    allow_delegation=False
)

# Create the writer agent
news_writer = Agent(
    role='Content Writer',
    goal='Write engaging and informative blog posts based on research',
    backstory="""You are a professional content writer with expertise in creating 
    engaging blog posts that are both informative and easy to understand.""",
    verbose=True,
    allow_delegation=False
) 