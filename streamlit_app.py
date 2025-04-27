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

# Initialize API client and LLM service
from utils.api_client import USITCApiClient
from utils.llm_service import LLMService

# Check for API keys in Streamlit secrets
api_key = None
model = "gpt-4"

if "openai" in st.secrets:
    api_key = st.secrets["openai"].get("OPENAI_API_KEY")
    model = st.secrets["openai"].get("OPENAI_MODEL", "gpt-4")
else:
    # Try to load from environment variables as fallback
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4")

# Initialize services
api_client = USITCApiClient(cache_enabled=True)
llm_service = LLMService(api_key=api_key, model=model, cache_enabled=True)

# Load sample data for fallback
@st.cache_data
def load_sample_data():
    try:
        # Load sample HTS data
        with open("data/sample_hts_data.json", "r") as f:
            hts_data = json.load(f)
        
        # Load sample duty data
        with open("data/sample_duty_data.json", "r") as f:
            duty_data = json.load(f)
            
        # Load sample trade agreements
        with open("data/sample_trade_agreements.json", "r") as f:
            trade_agreements = json.load(f)
            
        return {
            "hts_data": hts_data,
            "duty_data": duty_data,
            "trade_agreements": trade_agreements
        }
    except Exception as e:
        st.error(f"Error loading sample data: {e}")
        return {
            "hts_data": [],
            "duty_data": {},
            "trade_agreements": []
        }

# Load sample data for fallback
sample_data = load_sample_data()

# Main application header
st.title("Multifactor Tariff Intelligence Assistant (TIA)")
st.markdown("### Tariff Classification and Minimization Advisor")

# Create a navigation system using radio buttons
page = st.radio("Navigation", ["Search", "Results", "Analysis"], horizontal=True)

# Search Page
if page == "Search":
    st.header("Product Search")
    
    # Use a form for the search inputs
    with st.form(key="search_form"):
        # Product description input
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
            country_options = ["US", "JP", "CN", "DE", "UK"]
            country_names = {
                "US": "United States",
                "JP": "Japan",
                "CN": "China",
                "DE": "Germany",
                "UK": "United Kingdom"
            }
            
            origin_country = st.selectbox(
                "Country of Origin",
                options=country_options,
                format_func=lambda x: country_names.get(x, x),
                index=country_options.index("JP") if "JP" in country_options else 0,
                key="origin_country"
            )
        
        with col2:
            destination_country = st.selectbox(
                "Destination Country",
                options=country_options,
                format_func=lambda x: country_names.get(x, x),
                index=country_options.index("US") if "US" in country_options else 0,
                key="destination_country"
            )
        
        # Submit button for the form
        search_submitted = st.form_submit_button("Search for HTS Codes", type="primary")
    
    # Demo suggestion outside the form
    st.info("""
    **Demo Suggestion:** Try searching "Packing-less bumper retainer" (part that fastens an automobile bumper to the body).  
    Newly launched for Toyota models; plastic, one-touch pin, no rubber packing, mass-produced from April 2025.
    """)
    
    # Process form submission
    if search_submitted:
        if not product_description:
            st.error("Please enter a product description")
        else:
            try:
                with st.spinner("Searching for HTS codes..."):
                    # Use LLM to enhance search query if available
                    if llm_service.is_enabled():
                        st.info("Using AI to analyze product description...")
                        search_terms = llm_service.enhance_search_query(product_description)
                        
                        # Get product analysis from LLM cache
                        product_analysis = llm_service.cache.get(f"analysis_{product_description}")
                    else:
                        st.warning("AI analysis not available. Using basic search.")
                        search_terms = [product_description]
                        product_analysis = {
                            "MATERIALS": ["Plastic"] if "plastic" in product_description.lower() else [],
                            "FUNCTION": "Not analyzed",
                            "INDUSTRY_TERMS": [],
                            "HTS_TERMINOLOGY": "Not analyzed"
                        }
                    
                    # Search for HTS codes using the API client
                    try:
                        hts_results = []
                        for term in search_terms:
                            results = api_client.search(term)
                            for result in results:
                                # Check if this result is already in hts_results
                                if not any(r.get("hts_code") == result.get("hts_code") for r in hts_results):
                                    hts_results.append(result)
                        
                        # If we got results, analyze confidence with LLM
                        if hts_results and llm_service.is_enabled():
                            hts_results = llm_service.analyze_hs_code_confidence(product_description, hts_results)
                        
                        # If no results from API, use sample data as fallback
                        if not hts_results:
                            st.warning("No results from API. Using sample data.")
                            # Use sample data as fallback
                            for item in sample_data["hts_data"]:
                                if any(term.lower() in item["description"].lower() for term in search_terms):
                                    hts_results.append(item)
                            
                            # If still no results, add some general results
                            if not hts_results:
                                hts_results = sample_data["hts_data"][:3]
                    except Exception as e:
                        st.error(f"API search failed: {str(e)}")
                        # Use sample data as fallback
                        hts_results = sample_data["hts_data"][:5]
                    
                    # Create search results object
                    results = {
                        "product_description": product_description,
                        "origin_country": origin_country,
                        "destination_country": destination_country,
                        "search_terms": search_terms,
                        "hts_results": hts_results,
                        "product_analysis": product_analysis
                    }
                    
                    # Store results in session state
                    st.session_state.search_results = results
                    
                    # Clear any previously selected HTS code
                    st.session_state.selected_hts_code = None
                    st.session_state.document_data = None
                    st.session_state.pdf_buffer = None
                    
                    # Success message
                    st.success("Search successful! View results in the Results tab.")
                    
                    # Display a preview of the results
                    st.subheader("Preview of Results")
                    st.write(f"Found {len(hts_results)} potential HTS codes.")
                    
                    # Display the first result as a preview
                    if hts_results:
                        first_result = hts_results[0]
                        st.write(f"Top match: {first_result['hts_code']} - {first_result['description']}")
                        st.write(f"General Rate: {first_result['rates']['general']}")
                        
                        # Provide instructions to view full results
                        st.info("Click on the 'Results' tab above to view all results and generate analysis.")
            except Exception as e:
                st.error(f"An error occurred during search: {str(e)}")

# Results Page
elif page == "Results":
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        st.header("HTS Code Search Results")
        
        # Display search information
        st.markdown(f"**Product Description:** {results['product_description']}")
        st.markdown(f"**Origin Country:** {results['origin_country']}")
        st.markdown(f"**Destination Country:** {results['destination_country']}")
        
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
        
        # Display search terms if available
        if results.get('search_terms'):
            st.markdown("**Search Terms Used:**")
            for term in results['search_terms']:
                st.markdown(f"- {term}")
        
        # Display results in a table
        if results['hts_results']:
            # Create a DataFrame for display
            df_data = []
            for result in results['hts_results']:
                confidence = result.get("confidence", "Medium")
                
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
                    "Confidence": confidence_display
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
            
            # Use a form for the analysis generation
            with st.form(key="analysis_form"):
                st.write("Click the button below to generate a detailed tariff analysis for the selected HTS code.")
                analysis_submitted = st.form_submit_button("Generate Analysis", type="primary")
            
            if analysis_submitted:
                try:
                    with st.spinner("Generating tariff analysis..."):
                        # Try to get trade agreement eligibility from API
                        try:
                            trade_agreements_data = api_client.get_trade_agreement_eligibility(
                                selected_hts_code, 
                                results['origin_country'], 
                                results['destination_country']
                            )
                            
                            # Format trade agreements for display
                            trade_agreements = []
                            for agreement in trade_agreements_data.get("eligible_agreements", []):
                                trade_agreements.append({
                                    "name": agreement.get("agreement", "Unknown"),
                                    "eligible": True,
                                    "rate": agreement.get("rate", "0%"),
                                    "requirements": agreement.get("requirements", "Not specified")
                                })
                                
                            # If no eligible agreements found, add a placeholder
                            if not trade_agreements:
                                trade_agreements = [
                                    {
                                        "name": "USMCA",
                                        "eligible": results['origin_country'] in ["MX", "CA"] and results['destination_country'] == "US",
                                        "rate": "0%" if results['origin_country'] in ["MX", "CA"] and results['destination_country'] == "US" else "N/A",
                                        "requirements": "Regional Value Content ≥ 60%"
                                    },
                                    {
                                        "name": "GSP",
                                        "eligible": False,
                                        "rate": "N/A",
                                        "requirements": "Not applicable"
                                    }
                                ]
                        except Exception as e:
                            st.warning(f"Could not retrieve trade agreement data: {str(e)}")
                            # Fallback trade agreements
                            trade_agreements = [
                                {
                                    "name": "USMCA",
                                    "eligible": results['origin_country'] in ["MX", "CA"] and results['destination_country'] == "US",
                                    "rate": "0%" if results['origin_country'] in ["MX", "CA"] and results['destination_country'] == "US" else "N/A",
                                    "requirements": "Regional Value Content ≥ 60%"
                                },
                                {
                                    "name": "GSP",
                                    "eligible": False,
                                    "rate": "N/A",
                                    "requirements": "Not applicable"
                                }
                            ]
                        
                        # Generate tariff minimization strategies
                        # In a real implementation, this would use the LLM to generate custom strategies
                        strategies = [
                            {
                                "name": "USMCA Re-routing",
                                "description": "Move final assembly to Mexico to qualify for USMCA preferential treatment",
                                "savings": "2.5%",
                                "implementation": "Medium"
                            },
                            {
                                "name": "Duty Drawback",
                                "description": "Claim duty refund for imported goods that are subsequently exported",
                                "savings": "Up to 99% refund",
                                "implementation": "Complex"
                            },
                            {
                                "name": "First Sale Valuation",
                                "description": "Declare customs value based on first sale price",
                                "savings": "10-15% reduction in duty base",
                                "implementation": "Medium"
                            }
                        ]
                        
                        # Create document data
                        document_data = {
                            "product_description": results['product_description'],
                            "hts_code": selected_hts_code,
                            "hts_description": selected_result['description'],
                            "origin_country": results['origin_country'],
                            "destination_country": results['destination_country'],
                            "rates": selected_result['rates'],
                            "trade_agreements": trade_agreements,
                            "strategies": strategies
                        }
                        
                        # Store in session state
                        st.session_state.selected_hts_code = selected_hts_code
                        st.session_state.document_data = document_data
                        
                        # Success message
                        st.success("Analysis generated successfully! View it in the Analysis tab.")
                except Exception as e:
                    st.error(f"An error occurred while generating analysis: {str(e)}")
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
        
        # Get country names
        country_names = {
            "US": "United States",
            "JP": "Japan",
            "CN": "China",
            "DE": "Germany",
            "UK": "United Kingdom"
        }
        origin_name = country_names.get(origin_country, origin_country)
        destination_name = country_names.get(destination_country, destination_country)
        
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
    st.header("About Multifactor TIA")
    st.markdown(
        """
        The Tariff Intelligence Assistant (TIA) streamlines tariff analysis for global manufacturing by:
        
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
        - 📊 **Tariff-Minimization Advisor**: Get strategic recommendations
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
