# TariffDoc AI - Technical Context

## Technologies Used

### Core Technologies

1. **Python 3.8+**: Primary programming language
2. **Streamlit (1.22.0)**: Web application framework for the user interface
3. **OpenAI API (0.27.8)**: For LLM-enhanced features (optional)
4. **ReportLab (3.6.12)**: PDF generation library
5. **Pandas (1.5.3)** & **NumPy (1.23.5)**: Data manipulation libraries
6. **Requests (2.28.2)**: HTTP client for API communication
7. **Python-dotenv (1.0.0)**: Environment variable management
8. **BeautifulSoup4 (4.13.4)**: HTML parsing for potential web scraping

### External Services

1. **USITC Harmonized Tariff Schedule API**: Source of tariff data
2. **OpenAI GPT-4**: For enhanced search and analysis capabilities

## Development Setup

### Environment Setup

1. **Python Environment**: Python 3.8 or higher is required
2. **Dependencies**: Installed via pip using requirements.txt
3. **Environment Variables**: Configured through .env file
   - OPENAI_API_KEY: Required for LLM features
   - OPENAI_MODEL: Optional, defaults to gpt-4

### Running the Application

1. **Windows**:
   - PowerShell: `.\run_app.bat`
   - Command Prompt: `run_app.bat`

2. **Unix-based Systems**:
   - `./run_app.sh`

3. **Direct Execution**:
   - `streamlit run app.py`

### Dependency Management

1. **Primary Installation**:
   - `pip install -r requirements.txt`

2. **Compatibility Issues**:
   - Windows: `reinstall_dependencies.bat`
   - Unix: `./reinstall_dependencies.sh`
   - Manual: `pip uninstall -y numpy pandas && pip install numpy==1.23.5 pandas==1.5.3`

## Technical Constraints

### API Limitations

1. **USITC API**:
   - Limited documentation
   - Potential rate limiting
   - Inconsistent response formats
   - Fallback to mock data when API fails

2. **OpenAI API**:
   - Requires API key
   - Usage costs
   - Rate limits
   - Potential latency

### Performance Considerations

1. **Caching**:
   - API responses cached to improve performance
   - LLM responses cached to reduce API calls
   - Streamlit's caching for data loading

2. **Response Times**:
   - LLM calls may introduce latency
   - PDF generation can be resource-intensive

### Browser Compatibility

1. **Streamlit Limitations**:
   - Best experienced in modern browsers
   - Some features may not work in older browsers

### Deployment Considerations

1. **Environment Variables**:
   - Secure management of API keys
   - Configuration for different environments

2. **Scaling**:
   - Streamlit has limitations for high-traffic applications
   - Consider API rate limits for production use

## Development Workflow

1. **Local Development**:
   - Run with `streamlit run app.py`
   - Streamlit auto-reloads on file changes

2. **Testing**:
   - Manual testing of UI flows
   - Verify API integration
   - Test PDF generation

3. **Deployment**:
   - Streamlit Cloud (for demo purposes)
   - Docker containerization (for production)

This technical context provides the foundation for understanding the development environment, technologies, and constraints of the TariffDoc AI application.
