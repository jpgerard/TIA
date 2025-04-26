"""
Simplified Streamlit Application for TariffDoc AI

This is a minimal version of the application that focuses only on the search functionality.
"""

import os
import json
import streamlit as st
from utils.api_client import USITCApiClient
from utils.product_analyzer import ProductAnalyzer

# Set page configuration
st.set_page_config(
    page_title="TariffDoc AI - Simplified",
    page_icon="📄",
    layout="wide"
)

# Load country data
def load_country_data():
    try:
        with open("data/country_codes.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading country data: {e}")
        return {}

# Initialize API client and services
def initialize_services():
    api_client = USITCApiClient(cache_enabled=True)
    
    # Initialize product analyzer without LLM service
    product_analyzer = ProductAnalyzer(
        api_client=api_client,
        llm_service=None
    )
    
    return {
        "api_client": api_client,
        "product_analyzer": product_analyzer
    }

# Load data and initialize services
country_data = load_country_data()
services = initialize_services()

# Main application header
st.title("TariffDoc AI - Simplified Version")
st.markdown("### HTS Code Search")

# Product description input
product_description = st.text_area(
    "Enter Product Description",
    placeholder="e.g., Aluminum bicycle frame, Carbon fiber fishing rod, Plastic toy parts",
    help="Provide a detailed description of your product including materials and function"
)

# Country selection
col1, col2 = st.columns(2)

with col1:
    # Create a list of country options
    country_options = [(code, data["name"]) for code, data in country_data.items()]
    country_options.sort(key=lambda x: x[1])  # Sort by country name
    
    origin_country = st.selectbox(
        "Country of Origin",
        options=[code for code, _ in country_options],
        format_func=lambda x: next((name for code, name in country_options if code == x), x),
        index=country_options.index(("JP", "Japan")) if ("JP", "Japan") in country_options else 0
    )

with col2:
    destination_country = st.selectbox(
        "Destination Country",
        options=[code for code, _ in country_options],
        format_func=lambda x: next((name for code, name in country_options if code == x), x),
        index=country_options.index(("US", "United States")) if ("US", "United States") in country_options else 0
    )

# Demo suggestion
st.info("""
**Demo Suggestion:** Try searching "Packing-less bumper retainer" (part that fastens an automobile bumper to the body).
""")

# Search button
if st.button("Search for HTS Codes", type="primary"):
    if not product_description:
        st.error("Please enter a product description")
    else:
        try:
            with st.spinner("Searching for HTS codes..."):
                # Add debug message
                st.info("Starting search process...")
                
                # Analyze the product
                results = services["product_analyzer"].analyze_product(
                    product_description=product_description,
                    origin_country=origin_country,
                    destination_country=destination_country
                )
                
                # Add debug message
                st.info(f"Search completed. Found {len(results.get('hts_results', []))} results.")
                
                # Display results directly
                st.success("Search successful! Results are below:")
                
                # Display results in a simple format
                if results.get('hts_results'):
                    st.write(f"Found {len(results['hts_results'])} results.")
                    
                    # Display all results in a simple list
                    for i, result in enumerate(results['hts_results']):
                        st.markdown(f"**Result {i+1}:** {result['hts_code']} - {result['description']}")
                        st.markdown(f"**General Rate:** {result['rates']['general']}")
                        st.markdown("---")
                else:
                    st.warning("No results found. Try a different search term.")
        except Exception as e:
            st.error(f"An error occurred during search: {str(e)}")
            
            # Display detailed error information
            with st.expander("Detailed Error Information"):
                import traceback
                st.code(traceback.format_exc())
                
                # Display the state of the services
                st.subheader("Service Status")
                st.write(f"API Client initialized: {services['api_client'] is not None}")
                st.write(f"Product Analyzer initialized: {services['product_analyzer'] is not None}")
