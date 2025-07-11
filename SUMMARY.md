# GPT-Researcher Repository Summary

## Overview

This repository is an enhanced version of the [original GPT-Researcher project](https://github.com/assafelovic/gpt-researcher), designed to be an AI-powered autonomous research assistant that generates comprehensive, well-structured research reports on any given topic using Large Language Models (LLMs) and web crawling technologies.

### Relationship to Original Project

The author acknowledges being inspired by the original GPT-Researcher project but wanted "something more," leading to several days of refactoring and improvements. This version maintains the core concept while adding significant enhancements for better reliability, configurability, and functionality.

## What This Repository Does

**GPT-Researcher** is an intelligent research automation tool that:

1. **Takes a research topic as input** (e.g., "How to evaluate Alfred Hitchcock and his movies?")
2. **Automatically generates comprehensive research reports** in both Markdown and PDF formats
3. **Conducts autonomous web research** by searching, crawling, and analyzing relevant online content
4. **Uses AI to ensure quality and relevance** through content filtering and introspection mechanisms
5. **Provides detailed cost tracking** for LLM API usage

## Key Features & Improvements

### 🔄 **Pipeline Architecture**
- Serialized all research steps into a structured pipeline object (`pipeline/pipeline.py`)
- Enables better error handling and resumption of interrupted tasks
- Saves all intermediate results for debugging and recovery

### 🌐 **Proxy Support** 
- Added comprehensive proxy server configuration
- Essential for users in regions with restricted internet access
- Configurable through the config system

### 🕷️ **Enhanced Web Crawling**
- Refactored crawler architecture for easy extensibility
- Support for custom website-specific crawlers
- Selenium-based web scraping with headless browser support
- Can even process local files as research materials

### 🎯 **Intelligent Content Filtering**
- **Report Outline Generation**: Creates structured outlines before research begins
- **Introspection Mechanism**: Uses LLM to judge content relevance and discard irrelevant information
- **Timeliness Filtering**: Automatically discards potentially outdated documents

### 💰 **Cost Tracking**
- Detailed token usage statistics for different LLM models
- Price calculation based on current API pricing
- Transparent billing information for each research task

### 🌍 **Multi-language Support**
- Native language indication in all prompts
- Output language matches the input question language
- Tested with Chinese and English

## Repository Structure

```
gpt-researcher/
├── main.py                    # Entry point and CLI interface
├── config/                    # Configuration files
│   ├── config.default.json    # Default configuration
│   └── config.private.template.json  # Template for API keys
├── pipeline/                  # Research workflow orchestration
│   ├── pipeline.py            # Main research pipeline
│   └── pipeline_factory.py    # Pipeline configuration factory
├── llms/                      # Language model integrations
│   ├── openai_util.py         # OpenAI API wrapper
│   ├── role_prompt_generator.py  # AI persona creation
│   ├── question_expander.py   # Query expansion logic
│   ├── report_agent.py        # Report generation
│   ├── report_outline_generator.py  # Structure planning
│   └── self_reflection.py     # Content quality assessment
├── search/                    # Search engine integrations
│   ├── search_engine.py       # Search interface
│   └── duckduckgo_engine.py   # DuckDuckGo implementation
├── crawlers/                  # Web crawling system
│   ├── crawler.py             # Base crawler implementation
│   ├── crawler_manager.py     # Crawler coordination
│   ├── selenium_driver_pool.py  # Browser management
│   └── zhihu.py               # Zhihu-specific crawler
├── components/                # Data structures and models
├── utils/                     # Utility functions
└── output/                    # Generated reports (created at runtime)
```

## Architecture Components

### **Pipeline System**
- **Pipeline Factory**: Creates and configures the research pipeline
- **Pipeline Manager**: Orchestrates the entire research workflow
- **Task Management**: Generates unique task IDs and manages intermediate states

### **Large Language Model Integration**
- **Role Prompt Generator**: Creates specialized AI agent personas for research topics
- **Question Expander**: Breaks down topics into specific searchable queries  
- **Report Outline Generator**: Creates structured report frameworks
- **Report Agent**: Generates the final research content
- **Self-Reflection Module**: Evaluates content quality and relevance

### **Search & Crawling System**
- **Search Engine**: DuckDuckGo integration for finding relevant sources
- **Crawler Manager**: Coordinates multiple web crawlers
- **Selenium Driver Pool**: Manages browser instances for web scraping
- **Custom Crawlers**: Specialized crawlers for specific websites (e.g., Zhihu)

### **Configuration Management**
- **Config Center**: Centralized configuration management
- **API Key Management**: Secure handling of LLM API credentials
- **Proxy Configuration**: Network settings for restricted environments

## Research Workflow

1. **Topic Input**: User provides a research question or topic
2. **Role Assignment**: AI generates an appropriate expert persona (e.g., "Film Critic Agent")
3. **Outline Creation**: Structured report outline with sections and word targets
4. **Query Expansion**: Topic broken into specific search queries
5. **Web Search**: Multiple search engines find relevant sources
6. **Content Crawling**: Web pages are scraped and content extracted
7. **Content Filtering**: AI evaluates relevance and discards poor content
8. **Report Generation**: Comprehensive report written following the outline
9. **Output Creation**: Final report exported as both Markdown and PDF

## Usage Example

```bash
# Clone the repository
git clone git@github.com:godisboy0/gpt-researcher.git
cd gpt-researcher

# Setup configuration
cp config/config.private.template.json config/config.private.json
# Edit config.private.json with your OpenAI API key

# Run research
python main.py -t "How to evaluate Alfred Hitchcock and his movies?"
```

## Output Formats

- **Markdown Report**: Structured text format with proper headings and formatting
- **PDF Report**: Professional document format suitable for sharing
- **Intermediate Files**: JSON files containing search results, crawled content, and analysis
- **Log Files**: Detailed execution logs for debugging and monitoring

## Cost Management

The system provides detailed tracking of:
- Token usage per LLM model (GPT-4, GPT-3.5-turbo variants)
- Cost breakdown by operation type
- Total research cost calculation
- Usage history and statistics

## Technical Requirements

### Python Dependencies
- **selenium**: Web browser automation for crawling
- **openai**: OpenAI API client for GPT models
- **beautifulsoup4**: HTML parsing and content extraction
- **markdown2**: Markdown processing and conversion
- **weasyprint**: PDF generation from HTML/CSS
- **duckduckgo-search**: Search engine integration
- **requests**: HTTP client for API calls

### System Requirements
- **Python 3.7+**: Modern Python environment
- **OpenAI API Key**: Valid API key for GPT models
- **Web Browser**: Chrome/Chromium for Selenium WebDriver
- **Network Access**: Internet connection (proxy support available)
- **System Libraries**: Dependencies for PDF generation (weasyprint requires system libraries)

## Limitations

- **No Web UI**: Command-line interface only (author noted this as too difficult to implement)
- **Dependency on External APIs**: Requires OpenAI API access
- **Language Support**: Currently optimized for English and Chinese

## Target Users

- **Researchers**: Academic and professional researchers needing comprehensive topic analysis
- **Content Creators**: Writers and journalists requiring background research
- **Students**: Those needing structured research for assignments
- **Analysts**: Business and market researchers requiring detailed reports
- **Anyone**: Who needs automated, high-quality research on any topic

This repository transforms manual research processes into an automated, AI-driven workflow that produces professional-quality research reports with minimal human intervention.