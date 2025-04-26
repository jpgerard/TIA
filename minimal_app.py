"""
Minimal Streamlit Application

This is an extremely minimal Streamlit application with no external dependencies.
"""

import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Minimal Streamlit App",
    page_icon="📄",
    layout="wide"
)

# Main application header
st.title("Minimal Streamlit Application")
st.markdown("### This is a test application to diagnose blank screen issues")

# Add some basic UI elements
st.write("This is a minimal Streamlit application with no external dependencies.")
st.write("If you can see this text, the application is working correctly.")

# Add a text input
user_input = st.text_input("Enter some text")

# Add a button
if st.button("Click Me", type="primary"):
    if user_input:
        st.success(f"You entered: {user_input}")
    else:
        st.error("Please enter some text")

# Add some more UI elements
st.markdown("---")
st.markdown("### Debug Information")

# Display environment information
import sys
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")

# Display current time
import datetime
st.write(f"Current time: {datetime.datetime.now()}")

# Add a simple counter using session state
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment Counter"):
    st.session_state.counter += 1

st.write(f"Counter value: {st.session_state.counter}")
