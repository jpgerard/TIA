#!/bin/bash

echo "Starting TariffDoc AI application..."
echo
echo "Make sure you have installed the required dependencies:"
echo "pip install -r requirements.txt"
echo
echo "If you encounter compatibility issues between NumPy and Pandas, run:"
echo "./reinstall_dependencies.sh"
echo
echo "If you want to use LLM features, make sure to set up your .env file with your OpenAI API key."
echo

streamlit run app.py

# Check if the application exited with an error
if [ $? -ne 0 ]; then
    echo
    echo "Error running the application. This might be due to package compatibility issues."
    echo "Try running ./reinstall_dependencies.sh to fix the issue."
    echo
    read -p "Press Enter to continue..."
fi
