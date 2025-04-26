"""
Multifactor Tariff Intelligence Assistant (TIA) - Streamlit Application

This is the main Streamlit application for Multifactor Tariff Intelligence Assistant (TIA), which provides
tariff classification and tariff-minimization advisory capabilities.
"""

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from utils.api_client import USITCApiClient
from utils.llm_service import LLMService
# Removed PDF generator import
from utils.product_analyzer import ProductAnalyzer

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Multifactor Tariff Intelligence Assistant (TIA)",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_hts_code" not in st.session_state:
    st.session_state.selected_hts_code = None
if "document_data" not in st.session_state:
    st.session_state.document_data = None
if "pdf_buffer" not in st.session_state:
    st.session_state.pdf_buffer = None

# Load country data
@st.cache_data
def load_country_data():
    try:
        with open("data/country_codes.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading country data: {e}")
        return {}

# Load trade agreement data
@st.cache_data
def load_trade_agreement_data():
    try:
        with open("data/trade_agreements.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading trade agreement data: {e}")
        return {}

# Initialize API client and services
@st.cache_resource
def initialize_services():
    api_client = USITCApiClient(cache_enabled=True)
    
    # Initialize LLM service if API key is available
    # Try to get API key from Streamlit secrets first (for Streamlit Cloud deployment)
    # Fall back to environment variables (for local development)
    openai_api_key = None
    openai_model = "gpt-4"
    
    # Check if running on Streamlit Cloud with secrets
    try:
        openai_api_key = st.secrets["openai"]["OPENAI_API_KEY"]
        openai_model = st.secrets["openai"].get("OPENAI_MODEL", "gpt-4")
    except (KeyError, AttributeError):
        # Fall back to environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
    
    llm_service = None
    if openai_api_key:
        llm_service = LLMService(
            api_key=openai_api_key,
            model=openai_model,
            cache_enabled=True
        )
    
    # Initialize product analyzer
    product_analyzer = ProductAnalyzer(
        api_client=api_client,
        llm_service=llm_service
    )
    
    return {
        "api_client": api_client,
        "llm_service": llm_service,
        "product_analyzer": product_analyzer
    }

# Load data and initialize services
country_data = load_country_data()
trade_agreement_data = load_trade_agreement_data()
services = initialize_services()

# Check if LLM features are available
llm_available = services["llm_service"] is not None

# Main application header
st.title("Multifactor Tariff Intelligence Assistant (TIA)")
st.markdown("### Tariff Classification and Minimization Advisor")

# Display LLM status
if llm_available:
    st.success("✅ LLM features are enabled")
else:
    st.warning("⚠️ LLM features are disabled. Add your OpenAI API key to enable enhanced functionality.")

# Create a navigation system using radio buttons instead of tabs
page = st.radio("Navigation", ["Search", "Results", "Analysis"], horizontal=True)

# Search Page
if page == "Search":
    st.header("Product Search")
    
    # Use a form for the search inputs to avoid text area focus issues
    with st.form(key="search_form"):
        # Product description input with a key
        product_description = st.text_area(
            "Enter Product Description",
            placeholder="e.g., Aluminum bicycle frame, Carbon fiber fishing rod, Plastic toy parts",
            help="Provide a detailed description of your product including materials and function",
            key="product_description"
        )
        
        # Country selection inside the form
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a list of country options
            country_options = [(code, data["name"]) for code, data in country_data.items()]
            country_options.sort(key=lambda x: x[1])  # Sort by country name
            
            origin_country = st.selectbox(
                "Country of Origin",
                options=[code for code, _ in country_options],
                format_func=lambda x: next((name for code, name in country_options if code == x), x),
                index=country_options.index(("JP", "Japan")) if ("JP", "Japan") in country_options else 0,
                key="origin_country"
            )
        
        with col2:
            destination_country = st.selectbox(
                "Destination Country",
                options=[code for code, _ in country_options],
                format_func=lambda x: next((name for code, name in country_options if code == x), x),
                index=country_options.index(("US", "United States")) if ("US", "United States") in country_options else 0,
                key="destination_country"
            )
        
        # Submit button for the form
        search_submitted = st.form_submit_button("Search for HTS Codes", type="primary")
    
    # Demo suggestion outside the form
    st.info("""
    **Demo Suggestion:** Try searching "Packing-less bumper retainer" (part that fastens an automobile bumper to the body).  Newly launched for Toyota models; plastic, one-touch pin, no rubber packing, mass-produced from April 2025.Origin Country Japan. Destination country United States.
    """)
    
    # Process form submission
    if search_submitted:
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
                    
                    # Store results in session state
                    st.session_state.search_results = results
                    
                    # Clear any previously selected HTS code
                    st.session_state.selected_hts_code = None
                    st.session_state.document_data = None
                    st.session_state.pdf_buffer = None
                    
                    # Add debug message
                    st.info("Search completed. Displaying results directly without tab switch.")
                    
                    # Instead of switching tabs, display results directly
                    st.success("Search successful! Results are below:")
                    
                    # Display results in a simple format
                    if results['hts_results']:
                        st.write(f"Found {len(results['hts_results'])} results.")
                        
                        # Display the first result as an example
                        first_result = results['hts_results'][0]
                        st.write(f"First result: {first_result['hts_code']} - {first_result['description']}")
                        
                        # Store results in session state for the Results tab
                        st.session_state.search_results = results
                        
                        # Provide instructions to view full results
                        st.info("Click on the 'Results' tab above to view all results.")
                    else:
                        st.warning("No results found. Try a different search term.")
            except Exception as e:
                st.error(f"An error occurred during search: {str(e)}")
                st.error("Please check the following:")
                st.error("1. Is the product description valid?")
                st.error("2. Are the origin and destination countries selected?")
                st.error("3. Is the API connection working?")
                
                # Display detailed error information
                with st.expander("Detailed Error Information"):
                    import traceback
                    st.code(traceback.format_exc())
                    
                    # Display the state of the services
                    st.subheader("Service Status")
                    st.write(f"API Client initialized: {services['api_client'] is not None}")
                    st.write(f"LLM Service initialized: {services['llm_service'] is not None}")
                    st.write(f"Product Analyzer initialized: {services['product_analyzer'] is not None}")

# Results Page
elif page == "Results":
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        st.header("HTS Code Search Results")
        
        # Display search information
        st.markdown(f"**Product Description:** {results['product_description']}")
        
        # Display product analysis if available
        product_analysis = results.get('product_analysis')
        if product_analysis:
            with st.expander("View Product Analysis", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Materials")
                    materials = product_analysis.get("MATERIALS", [])
                    if isinstance(materials, list):
                        for material in materials:
                            st.markdown(f"- {material}")
                    else:
                        st.markdown(f"- {materials}")
                    
                    st.subheader("Function")
                    st.markdown(product_analysis.get("FUNCTION", "Not specified"))
                
                with col2:
                    st.subheader("Industry Terms")
                    industry_terms = product_analysis.get("INDUSTRY_TERMS", [])
                    if isinstance(industry_terms, list):
                        for term in industry_terms:
                            st.markdown(f"- {term}")
                    else:
                        st.markdown(f"- {industry_terms}")
                    
                    st.subheader("HTS Terminology")
                    hts_terms = product_analysis.get("HTS_TERMINOLOGY", "Not specified")
                    st.markdown(hts_terms)
        
        if len(results['search_terms']) > 1:
            st.markdown("**Search Terms Used:**")
            for term in results['search_terms']:
                st.markdown(f"- {term}")
        
        # Display results in a table
        if results['hts_results']:
            # Check if any results are using fallback data
            using_fallback = any(result.get("is_fallback", False) for result in results['hts_results'])
            if using_fallback:
                st.warning("⚠️ Using sample data. Live API connection unavailable.")
            
            # Create a DataFrame for display
            df_data = []
            for result in results['hts_results']:
                confidence = result.get("confidence", "Medium")
                confidence_reason = result.get("confidence_reason", "")
                
                # Format the confidence with color
                if confidence == "High":
                    confidence_display = "🟢 High"
                elif confidence == "Medium":
                    confidence_display = "🟡 Medium"
                else:
                    confidence_display = "🔴 Low"
                
                df_data.append({
                    "HTS Code": result["hts_code"],
                    "Description": result["description"],
                    "General Rate": result["rates"]["general"],
                    "Confidence": confidence_display,
                    "Notes": confidence_reason
                })
            
            df = pd.DataFrame(df_data)
            
            # Display the table
            st.dataframe(df, use_container_width=True)
            
            # Selection for analysis generation
            st.subheader("Generate Tariff Analysis")
            
            selected_index = st.selectbox(
                "Select an HTS Code for tariff analysis",
                options=range(len(results['hts_results'])),
                format_func=lambda i: f"{results['hts_results'][i]['hts_code']} - {results['hts_results'][i]['description']}"
            )
            
            selected_result = results['hts_results'][selected_index]
            selected_hts_code = selected_result['hts_code']
            
            # Display detailed analysis for the selected HTS code
            with st.expander("View Detailed Analysis", expanded=True):
                st.subheader(f"Why this HTS code might be appropriate")
                
                # Display confidence and reasoning
                confidence = selected_result.get("confidence", "Medium")
                confidence_reason = selected_result.get("confidence_reason", "")
                
                # Format the confidence with color
                if confidence == "High":
                    st.markdown("**Confidence:** 🟢 High")
                elif confidence == "Medium":
                    st.markdown("**Confidence:** 🟡 Medium")
                else:
                    st.markdown("**Confidence:** 🔴 Low")
                
                if confidence_reason:
                    st.markdown(f"**Reasoning:** {confidence_reason}")
                
                # Display detailed analysis if available
                detailed_analysis = selected_result.get("detailed_analysis", {})
                if detailed_analysis:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Material Matches:**")
                        material_matches = detailed_analysis.get("material_matches", [])
                        if material_matches:
                            for material in material_matches:
                                st.markdown(f"- {material}")
                        else:
                            st.markdown("- No direct material matches")
                    
                    with col2:
                        st.markdown("**Function Match:**")
                        function_match = detailed_analysis.get("function_match", False)
                        function = detailed_analysis.get("function", "")
                        if function_match:
                            st.markdown(f"- ✅ {function}")
                        else:
                            st.markdown(f"- ❌ No direct function match")
                
                # Display HTS classification path
                st.markdown("**HTS Classification Path:**")
                hts_code = selected_result["hts_code"]
                description = selected_result["description"]
                
                # Split the description by colons to show the hierarchy
                parts = description.split(":")
                if len(parts) > 1:
                    for i, part in enumerate(parts):
                        indent = "&nbsp;" * (i * 4)
                        st.markdown(f"{indent}- {part.strip()}")
                else:
                    st.markdown(f"- {description}")
            
            # Use a form for the analysis generation to avoid button click issues
            with st.form(key="analysis_form"):
                st.write("Click the button below to generate a detailed tariff analysis for the selected HTS code.")
                analysis_submitted = st.form_submit_button("Generate Analysis", type="primary")
            
            if analysis_submitted:
                try:
                    with st.spinner("Generating tariff analysis..."):
                        # Get comprehensive tariff information
                        document_data = services["product_analyzer"].get_tariff_document_data(
                            product_description=results['product_description'],
                            hts_code=selected_hts_code,
                            origin_country=results['origin_country'],
                            destination_country=results['destination_country']
                        )
                        
                        # Store in session state
                        st.session_state.selected_hts_code = selected_hts_code
                        st.session_state.document_data = document_data
                        
                        # Provide instructions to view analysis
                        st.success("Analysis generated successfully!")
                        st.info("Click on the 'Analysis' option in the navigation to view the detailed analysis.")
                except Exception as e:
                    st.error(f"An error occurred while generating analysis: {str(e)}")
                    import traceback
                    st.text(traceback.format_exc())
        else:
            st.warning("No HTS codes found for the given product description. Try a more specific description or different search terms.")
    else:
        st.info("Enter a product description in the Search tab to find HTS codes.")

# Analysis Page
elif page == "Analysis":
    if st.session_state.document_data:
        data = st.session_state.document_data
        
        st.header("Tariff-Minimization Advisor")
        
        # Display product information
        product_description = data['product_description']
        hts_code = data['hts_code']
        hts_description = data['hts_description']
        origin_country = data.get('origin_country', 'Unknown')
        destination_country = data.get('destination_country', 'Unknown')
        
        # Get country names from codes
        origin_name = next((country_data[code]["name"] for code in country_data if code == origin_country), origin_country)
        destination_name = next((country_data[code]["name"] for code in country_data if code == destination_country), destination_country)
        
        # Get duty rate
        general_rate = data['rates'].get('general', 'N/A')
        
        # Calculate annual duty spend (assuming $2,000,000 import value)
        import_value = 2000000
        duty_rate = 0.0
        try:
            # Try to convert rate from string to float (removing % and converting to decimal)
            rate_str = general_rate.strip()
            if rate_str.endswith('%'):
                rate_str = rate_str[:-1]
            duty_rate = float(rate_str) / 100
        except:
            duty_rate = 0.025  # Default to 2.5% if conversion fails
        
        annual_duty = import_value * duty_rate
        
        # Display the header information
        st.markdown(f"""
        **Product:** {product_description}
        
        **Current lane:** {origin_name} → {destination_name}
        
        **HS code:** {hts_code} ({hts_description}) – MFN duty {general_rate}
        
        **Assumed annual import value (FOB):** USD ${import_value:,}
        
        **Baseline duty spend:** ${annual_duty:,.0f} / year
        """)
        
        # Create the strategies table
        strategies_data = [
            {
                "Strategy": "USMCA Re-routing & Origin Shift",
                "Mechanism": "Final injection-moulding or simple assembly in Mexico → qualifies as \"originating\" under USMCA ROO 8708.X (tariff shift + RVC ≥ 60 %).",
                "Implementation": "• Evaluate moving last-step moulding to Nifco Mexico plant.\n• Obtain supplier declarations & keep production records.\n• File USMCA Certificate of Origin.",
                "Impact": "0 % duty (vs 2.5 %).",
                "Savings": f"${annual_duty:,.0f}"
            },
            {
                "Strategy": "Duty Drawback (Substitution)",
                "Mechanism": "Import clips, incorporate into vehicles exported from U.S. → claim 99 % refund of duties paid on identical class/ kind.",
                "Implementation": "• Track imported quantities vs. exported vehicles.\n• File CBP drawback claim within 3 yrs (ACE).",
                "Impact": "Up to 99 % refund on 2.5 % already paid.",
                "Savings": f"Up to ${annual_duty * 0.99:,.0f} (if 100 % re-export)"
            },
            {
                "Strategy": "First-Sale Valuation",
                "Mechanism": "Declare customs value based on first (\"factory\") sale to trading company, typically 10 % lower than current invoice.",
                "Implementation": "• Map multi-tier sales chain.\n• Collect factory invoices & Incoterms evidence.\n• Update entry declarations.",
                "Impact": "Duty base drops 10 %.",
                "Savings": f"${annual_duty * 0.1:,.0f}"
            },
            {
                "Strategy": "Supplier Diversification",
                "Mechanism": "Source from Vietnam (MFN 2.5 % but future Indo-Pacific Economic Framework could cut to 0 ) or from NAFTA zone to leverage USMCA immediately.",
                "Implementation": "• Identify alternate moulders.\n• Run landed-cost comparison incl. tooling, logistics.",
                "Impact": "Potential duty to 0 % long-term.",
                "Savings": f"${annual_duty:,.0f} (future)"
            },
            {
                "Strategy": "Tariff Engineering",
                "Mechanism": "Redesign clip (e.g., combined metal–plastic fastener) so primary material classifies under 7318.29 (fasteners; duty 0 %).",
                "Implementation": "• Prototype hybrid design.\n• Request CBP binding ruling pre-launch.",
                "Impact": f"From {general_rate} → 0 %.",
                "Savings": f"${annual_duty:,.0f} (if feasible)"
            }
        ]
        
        # Create a DataFrame for the strategies
        import pandas as pd
        df = pd.DataFrame(strategies_data)
        
        # Display the strategies table
        st.markdown("### Duty Minimization Strategies")
        st.table(df)
        
        # Display advisor recommendations
        st.markdown("### Advisor Recommendation (ranked):")
        st.markdown("""
        1. **USMCA origin shift** – quickest full elimination; tooling already exists in Nifco Mexico.
        
        2. **Duty drawback** – activate immediately on exported vehicle programs; moderate process overhead.
        
        3. **First-sale valuation** – low effort, modest but guaranteed savings.
        
        4. **Explore supplier diversification** once IPEF tariffs clarify.
        
        5. **Investigate tariff-engineering** only if redesign aligns with OEM specs.
        """)
        
        # Display next steps
        st.markdown("### Next steps auto-generated by TIA:")
        st.markdown("""
        - Draft USMCA Certificate template for bumper retainer (pre-filled HS 8708.10.60, RVC worksheet).
        
        - Create CBP Form 7553 & 7551 packets for drawback program enrollment.
        
        - Produce first-sale valuation checklist and evidence log template.
        
        - Schedule sourcing RFP to Mexican moulding suppliers with duty-free scenario analysis.
        """)
        
        # Display footnote
        st.caption(f"All figures assume constant FOB value and current HTSUS Rev 2 (updated {datetime.now().strftime('%Y-%m-%d')}). Actual savings depend on production mix and export volumes.")
        
    else:
        st.info("Generate an analysis from the Results tab to view tariff minimization strategies.")

# Sidebar with information
with st.sidebar:
    st.header("About Multifactor TIA POC")
    st.markdown(
        """
        This POC demo streamlines tariff analysis for global manufacturing by:
        
        - Providing accurate HTS code classification
        - Calculating applicable duty rates
        - Identifying trade agreement eligibility
        - Recommending tariff minimization strategies
        
        This application uses the USITC Harmonized Tariff Schedule data and 
        leverages AI to enhance search capabilities and provide strategic tariff advice.
        """
    )
    
    st.subheader("Features")
    st.markdown(
        """
        - 🔍 **Intelligent Search**: Find the right HTS codes for your products
        - 🌐 **Trade Agreement Analysis**: Identify potential duty savings
        - 📊 **Tariff-Minimization Advisor**: Get strategic recommendations to reduce duty costs
        - 📈 **Savings Analysis**: Quantify potential duty savings opportunities
        """
    )
    
    # Add Multifactor AI branding
    st.markdown("---")
    st.markdown("Powered by Multifactor AI")
    
    # Display version information
    st.markdown("---")
    st.caption("Multifactor Tariff Intelligence Assistant (TIA) v0.1.0")
    st.caption(f"Generated on: {datetime.now().strftime('%B %d, %Y')}")

# Run the Streamlit app
if __name__ == "__main__":
    # This is handled by Streamlit
    pass
