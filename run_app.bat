@echo off
echo Starting TariffDoc AI application...
echo.
echo Make sure you have installed the required dependencies:
echo pip install -r requirements.txt
echo.
echo If you encounter compatibility issues between NumPy and Pandas, run:
echo reinstall_dependencies.bat
echo.
echo If you want to use LLM features, make sure to set up your .env file with your OpenAI API key.
echo.
streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo Error running the application. This might be due to package compatibility issues.
    echo Try running reinstall_dependencies.bat to fix the issue.
    echo.
    pause
)
