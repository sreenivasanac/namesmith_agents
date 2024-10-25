from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TrendResearchQueries(BaseModel):
    queries: List[str] = Field(
        description="Comprehensive search queries to discover latest trends across technology, business, and user behavior"
    )

# Create a parser
parser = PydanticOutputParser(pydantic_object=TrendResearchQueries)

# Create the prompt template
template = """
Generate a comprehensive set of search queries designed to uncover 
the latest trends in technology, business, and user behavior. Your queries 
should be crafted to work across multiple platforms and 
reveal emerging patterns.

Consider these key areas when generating queries:

TECHNOLOGY LANDSCAPE:
- Programming languages and frameworks gaining traction
- New developer tools and platforms
- Cloud services and infrastructure trends
- AI/ML technologies and applications
- Emerging technologies (AR/VR, blockchain, etc.)

BUSINESS & STARTUP ACTIVITY:
- Recent funding patterns
- New business models
- Industry disruptions
- Market opportunities
- Successful product launches

USER BEHAVIOR & DEMANDS:
- Pain points and problems
- Feature requests and user needs
- Community discussions and feedback
- Usage patterns and adoption trends
- User satisfaction and complaints

MARKET DYNAMICS:
- Competition and alternatives
- Pricing strategies
- Distribution channels
- Growth metrics
- Market size and potential


QUERY GUIDELINES:
1. Use platform-specific search operators where applicable
2. Include timeframe parameters (last month, quarter, year)
3. Combine multiple relevant keywords
4. Focus on measurable metrics and concrete data
5. Include queries for both broad trends and specific niches
6. Consider geographical and demographic factors
7. Look for numerical indicators (growth rates, adoption metrics)
8. Include sentiment and reaction analysis

{format_instructions}

Generate queries that are:
- Specific enough to get meaningful results
- Broad enough to capture emerging trends
- Focused on recent activities (last 3-12 months)
- Designed to reveal actual usage and adoption
- Capable of showing growth patterns
- Aimed at discovering underserved needs
"""

prompt = PromptTemplate(
    template=template,
    partial_variables={"format_instructions": parser.get_format_instructions()},
    input_variables=[]
)

# Get the API key from environment variables
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Initialize the LLM
llm = ChatOpenAI(temperature=0.7, openai_api_key=api_key)

# Create the chain
chain = prompt | llm | parser

def generate_research_queries() -> TrendResearchQueries:
    """Generate a comprehensive set of trend research queries"""
    return chain.invoke({})
