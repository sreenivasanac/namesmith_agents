# Namesmith - Domain Research and Generation System

An intelligent multi-agent system that automates the generation, evaluation, and resale of high-quality, brandable domain names. Built using LangGraph, it orchestrates various specialized agents to perform market research, generate domain suggestions, evaluate names, and check availability.

## Quick Links
- [Live Dashboard](https://namesmith-console-qjzx.vercel.app/dashboard)
- [Project Documentation](https://coda.io/d/Domain-name-Bot-Agents-project_dfkJDNYF-UH)
- [Project Demo of Agents in action -- Youtube](https://www.youtube.com/watch?v=hF3eGLudxY4&list=PLB1nTQo4_y6u_4vzapND6Bm6J7M1KVurF&index=7)
- [Dashboard console UI Codebase](https://github.com/sreenivasanac/namesmith_console)
- [Agents Codebase](https://github.com/sreenivasanac/namesmith_agents)

## System Architecture

The system is built using LangGraph, a library for creating multi-agent workflows. The main orchestration logic is defined in `agents/domain_research_graph.py`, which coordinates the following specialized agents:

1. **Market Trends Bot** (`market_research_bot.py`):
   - Generates a list of notable companies in various tech sectors
   - Maps company details (name, category, description, keyword, domain)
   - Analyzes current market trends using GPT-4
   - Extracts key industry patterns and naming conventions

2. **Domain Generator Bot** (`domain_generator.py`):
   - Creates unique, brandable domain suggestions for AI SaaS B2B startups
   - Leverages market trends data for trend-aligned naming
   - Follows specific naming conventions for multiple TLDs (.com, .ai)

3. **Domain Scoring Bot** (`domain_name_scoring_bot.py`):
   - Evaluates domains on multiple criteria (1-10 scale):
     - Memorability
     - Pronounceability
     - Length
     - Brandability
   - Provides detailed scoring rationale
   - Assigns relevant categories and keywords

4. **Availability Checker** (`check_domain_name_availability.py`):
   - Validates domain availability via WHOISJSON API
   - Filters out registered domains
   - Updates availability status in database

5. **Database Integration**:
   - Saves domain information through REST API endpoints
   - Stores domain details, availability status, and evaluation scores
   - Uses Pydantic models for data validation

## Data Models

The system uses the following data models (`domain_schema.py`):

- `DomainName`: Basic domain information
- `DNAvailabilityStatus`: Domain availability status
- `DNEvaluation`: Detailed domain evaluation scores
- `DNSEOAnalysis`: SEO analysis data (prepared for future implementation)
- `DomainWithDetails`: Combines all domain-related information

## Running Instructions

1. Ensure you have Python 3.7+ installed

2. Clone the repository:   ```bash
   git clone <repository-url>
   cd <repository-directory>   ```

3. Install dependencies:   ```bash
   pip install -r requirements.txt   ```

4. Set up environment variables in `.env`:   ```
   OPENAI_API_KEY=your_openai_api_key_here
   WHOISJSON_API_KEY=your_whoisjson_api_key_here   ```

5. Run the main script:   ```bash
   python main.py   ```

## API Integration

The system integrates with:
- OpenAI API for AI-powered domain generation and evaluation
- WHOISJSON API for domain availability checking
- Custom REST API endpoints for database operations:
  - `/api/domains`: Create new domain entries
  - `/api/availability-status`: Store availability status
  - `/api/evaluation`: Store domain evaluations
  - `/api/seo-analysis`: Store SEO analysis (prepared for future use)

## Dependencies

Main dependencies include:
- langchain & langgraph: For workflow orchestration
- openai: For GPT-4 integration
- pydantic: For data validation
- requests: For API interactions
- python-dotenv: For environment variable management

For a complete list, see `requirements.txt`

## Note

This system uses the OpenAI GPT-4 model and WHOISJSON API, which may incur costs. Make sure you understand the pricing and usage limits of both APIs before running the script.

## Future Enhancements

The system is prepared for future enhancements including:
- SEO analysis implementation
- Extended domain availability checking features
- Additional domain evaluation metrics
- Enhanced market research capabilities
