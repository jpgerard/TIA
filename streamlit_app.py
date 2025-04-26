"""
Streamlit Cloud entry point for TariffDoc AI application.
This file serves as the entry point for Streamlit Cloud deployment.
"""

import streamlit as st

# Add error handling to catch any issues
try:
    # Import the minimal application
    from minimal_app import *
    
    # Add a message to confirm the app is running
    st.sidebar.success("Application loaded successfully!")
    
except Exception as e:
    # Display any errors that occur during import
    st.error(f"Error loading application: {str(e)}")
    st.write("Detailed error information:")
    import traceback
    st.code(traceback.format_exc())
    
    # Display environment information
    st.write("## Environment Information")
    import sys
    st.write(f"Python version: {sys.version}")
    st.write(f"Streamlit version: {st.__version__}")
    
    # Try to import other dependencies to check if they're available
    st.write("## Dependency Check")
    try:
        import pandas
        st.write(f"pandas version: {pandas.__version__}")
    except ImportError:
        st.write("pandas: Not available")
    
    try:
        import numpy
        st.write(f"numpy version: {numpy.__version__}")
    except ImportError:
        st.write("numpy: Not available")
    
    try:
        import requests
        st.write(f"requests version: {requests.__version__}")
    except ImportError:
        st.write("requests: Not available")

# The application will be automatically run by Streamlit Cloud
