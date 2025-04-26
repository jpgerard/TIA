# TariffDoc AI

TariffDoc AI is a Streamlit-based application that streamlines tariff documentation for global manufacturing. It allows users to input a part number or product description, fetch relevant tariff information from the USITC Harmonized Tariff Schedule, and generate a downloadable PDF document for compliance purposes.

## Features

- **Tariff Intelligence Assistant**: Search for HTS codes based on product descriptions
- **LLM-Enhanced Search**: Improve search accuracy with AI-powered query enhancement
- **Trade Agreement Analysis**: Identify eligibility for trade agreements and potential duty savings
- **Document Generation**: Create professional, compliance-ready PDF documents
- **Expert Analysis**: Get AI-generated explanations of tariff implications

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository to your local machine.

2. Navigate to the project directory:
   ```
   cd TIA
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   **Note**: If you encounter compatibility issues between NumPy and Pandas (such as `ValueError: numpy.dtype size changed, may indicate binary incompatibility`), use the provided reinstallation scripts:
   - On Windows: Run `.\reinstall_dependencies.bat` (PowerShell) or `reinstall_dependencies.bat` (Command Prompt)
   - On Unix-based systems: Run `./reinstall_dependencies.sh`

4. (Optional) Set up OpenAI API for enhanced features:
   - Copy the `.env.example` file to `.env`:
     ```
     copy .env.example .env
     ```
   - Edit the `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Usage

1. Start the Streamlit application:
   - On Windows (PowerShell):
     ```
     .\run_app.bat
     ```
   - On Windows (Command Prompt):
     ```
     run_app.bat
     ```
   - On Unix-based systems:
     ```
     ./run_app.sh
     ```
   - Or directly with Streamlit:
     ```
     streamlit run app.py
     ```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

3. Use the application:
   - Enter a product description in the Search tab
   - Select the country of origin and destination country
   - Click "Search for HTS Codes" to find matching tariff classifications
   - In the Results tab, select an HTS code and click "Generate Document"
   - In the Document tab, view the tariff information and download the PDF

## Project Structure

```
TIA/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .env.example                # Example environment variables
├── README.md                   # Project documentation
├── run_app.bat                 # Windows run script
├── run_app.sh                  # Unix run script
├── reinstall_dependencies.bat  # Windows dependency reinstall script
├── reinstall_dependencies.sh   # Unix dependency reinstall script
├── utils/
│   ├── api_client.py           # USITC API client
│   ├── llm_service.py          # LLM integration
│   ├── pdf_generator.py        # PDF generation
│   └── product_analyzer.py     # Product analysis logic
├── data/
│   ├── country_codes.json      # Country information
│   └── trade_agreements.json   # Trade agreement data
└── assets/
    └── multifactor_logo.png    # Multifactor logo for branding
```

## API Integration

This application integrates with the USITC Harmonized Tariff Schedule API to retrieve tariff information. The API is used to:

1. Search for HTS codes based on product descriptions
2. Retrieve detailed information about specific HTS codes
3. Determine trade agreement eligibility

## LLM Integration

When configured with an OpenAI API key, the application uses AI to enhance functionality:

1. Improve search queries by generating industry-specific terminology
2. Analyze confidence levels for HTS code matches
3. Generate plain-language explanations of tariff implications

## Troubleshooting

### NumPy and Pandas Compatibility Issues

If you encounter an error like:
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

This indicates a compatibility issue between NumPy and Pandas. To resolve:

1. Use the provided reinstallation scripts:
   - On Windows (PowerShell): Run `.\reinstall_dependencies.bat`
   - On Windows (Command Prompt): Run `reinstall_dependencies.bat`
   - On Unix-based systems: Run `./reinstall_dependencies.sh`

2. Or manually reinstall the packages with compatible versions:
   ```
   pip uninstall -y numpy pandas
   pip install numpy==1.23.5 pandas==1.5.3
   ```

### PowerShell Script Execution

If you're using PowerShell and get an error like:
```
The term 'run_app.bat' is not recognized as the name of a cmdlet, function, script file, or executable program.
```

Use the `.\` prefix to run scripts in the current directory:
```
.\run_app.bat
```

### OpenAI API Issues

If LLM features are not working:

1. Verify your API key is correctly set in the `.env` file
2. Check your OpenAI account has sufficient credits
3. Ensure your internet connection allows access to the OpenAI API

## Limitations

This is a proof-of-concept application with the following limitations:

1. The USITC API integration is simplified and may not capture all nuances of the actual API
2. Trade agreement eligibility is determined using basic rules and may not reflect all requirements
3. The application focuses on US imports (with the US as the destination country)
4. PDF generation uses a basic template that may need customization for production use

## Future Enhancements

Potential enhancements for future versions:

1. Integration with additional tariff databases (TARIC, etc.)
2. Support for Bill of Materials (BOM) uploads
3. Tariff-minimization advisor functionality
4. Real-time regulatory monitoring
5. Enhanced audit trail and export history

## License

This project is proprietary software developed for Multifactor AI.

## Acknowledgments

- USITC for providing the Harmonized Tariff Schedule data
- Streamlit for the web application framework
- OpenAI for the language model capabilities
