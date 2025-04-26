"""
Test script to verify the API search for specific HTS codes.
"""

from utils.api_client import USITCApiClient

def test_hts_code_search():
    """Test the API search for specific HTS codes."""
    
    # Initialize the API client
    api_client = USITCApiClient()
    
    # Test HTS code
    hts_code = "8708.99.8180"
    
    print(f"Testing search for HTS code: '{hts_code}'")
    
    # Search for the HTS code
    results = api_client.search(hts_code)
    
    # Print the results
    print("\nSearch Results:")
    if results:
        for i, result in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"HTS Code: {result['hts_code']}")
            print(f"Description: {result['description']}")
            print(f"Rates: {result['rates']}")
    else:
        print("No results found")
    
    # Test getting details for the HTS code
    print(f"\nTesting get_hts_details for HTS code: '{hts_code}'")
    details = api_client.get_hts_details(hts_code)
    
    # Print the details
    print("\nHTS Details:")
    if details:
        print(f"HTS Code: {details['hts_code']}")
        print(f"Description: {details['description']}")
        print(f"Rates: {details['rates']}")
    else:
        print("No details found")

if __name__ == "__main__":
    test_hts_code_search()
