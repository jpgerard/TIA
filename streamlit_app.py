"""
Minimal Streamlit App for Deployment Testing

This is a minimal version of the app that should work on Streamlit Cloud.
"""

import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="Multifactor Tariff Intelligence Assistant (TIA)",
    page_icon="📄",
    layout="wide"
)

# Main application header
st.title("Multifactor Tariff Intelligence Assistant (TIA)")
st.markdown("### Tariff Classification and Minimization Advisor")

# Add a simple message
st.success("✅ Application is running successfully!")

# Create a simple form
with st.form(key="demo_form"):
    st.write("This is a simplified version of the TIA application for deployment testing.")
    product_description = st.text_area(
        "Enter Product Description",
        placeholder="e.g., Aluminum bicycle frame, Carbon fiber fishing rod, Plastic toy parts",
        key="product_description"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        origin_country = st.selectbox(
            "Country of Origin",
            options=["US", "JP", "CN", "DE", "UK"],
            index=1,
            key="origin_country"
        )
    
    with col2:
        destination_country = st.selectbox(
            "Destination Country",
            options=["US", "JP", "CN", "DE", "UK"],
            index=0,
            key="destination_country"
        )
    
    submit_button = st.form_submit_button("Search for HTS Codes", type="primary")

if submit_button:
    st.info(f"Search requested for: {product_description}")
    st.info(f"Origin: {origin_country}, Destination: {destination_country}")
    
    # Display a sample result
    st.subheader("Sample Results")
    df = pd.DataFrame({
        "HTS Code": ["8708.10.60", "8708.29.50", "3926.30.10"],
        "Description": [
            "Parts and accessories of bodies for motor vehicles: Bumpers",
            "Parts and accessories of bodies for motor vehicles: Other",
            "Other articles of plastics: Fittings for furniture, coachwork or the like"
        ],
        "General Rate": ["2.5%", "2.5%", "5.3%"]
    })
    st.dataframe(df)

# Sidebar with information
with st.sidebar:
    st.header("About Multifactor TIA")
    st.markdown(
        """
        This is a simplified version of the Tariff Intelligence Assistant for deployment testing.
        
        The full version provides:
        
        - 🔍 **Intelligent Search**: Find the right HTS codes for your products
        - 🌐 **Trade Agreement Analysis**: Identify potential duty savings
        - 📊 **Tariff-Minimization Advisor**: Get strategic recommendations
        - 📈 **Savings Analysis**: Quantify potential duty savings opportunities
        """
    )
    
    # Add Multifactor AI branding
    st.markdown("---")
    st.markdown("Powered by Multifactor AI")
