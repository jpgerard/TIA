"""
Test script to verify the improved search functionality with live USITC API and LLM disambiguation.
"""

from utils.api_client import USITCApiClient
from utils.llm_service import LLMService
from utils.product_analyzer import ProductAnalyzer

def test_improved_search():
    """Test the improved search functionality."""
    
    # Initialize the API client, LLM service, and product analyzer
    api_client = USITCApiClient()
    llm_service = LLMService()
    product_analyzer = ProductAnalyzer(api_client=api_client, llm_service=llm_service)
    
    # Test the search
    product_description = "Packing-less bumper retainer"
    origin_country = "JP"
    destination_country = "US"
    
    print(f"Testing search for: '{product_description}'")
    
    # Analyze the product
    results = product_analyzer.analyze_product(
        product_description=product_description,
        origin_country=origin_country,
        destination_country=destination_country
    )
    
    # Print the search terms used
    print("\nSearch Terms Used:")
    for term in results['search_terms']:
        print(f"- {term}")
    
    # Print the results
    print("\nSearch Results:")
    if results['hts_results']:
        for i, result in enumerate(results['hts_results'][:5]):  # Show top 5 results
            print(f"\nResult {i+1}:")
            print(f"HTS Code: {result['hts_code']}")
            print(f"Description: {result['description'][:100]}...")  # Truncate long descriptions
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Confidence Reason: {result.get('confidence_reason', 'N/A')}")
            print(f"Relevance Score: {result.get('relevance_score', 'N/A')}")
            
            # Check if this is a bumper part
            is_bumper_part = False
            if "8708.10" in result['hts_code'] or "bumper" in result['description'].lower():
                is_bumper_part = True
                print("✅ This is a bumper part")
            else:
                print("❌ This is NOT a bumper part")
    else:
        print("No results found")

if __name__ == "__main__":
    test_improved_search()
