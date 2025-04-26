@echo off
echo Reinstalling dependencies with compatible versions...
echo.

echo Uninstalling existing packages...
pip uninstall -y numpy pandas streamlit openai requests reportlab python-dotenv beautifulsoup4

echo.
echo Installing packages with specific versions...
pip install -r requirements.txt

echo.
echo Dependencies reinstalled. You can now run the application with:
echo streamlit run app.py
