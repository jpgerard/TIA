"""
USITC API Client for TariffDoc AI

This module handles communication with the USITC HTS RESTful API for tariff data retrieval.
"""

import requests
import json
import time
import os
import re
import urllib.parse
from typing import Dict, List, Any, Optional, Union
from bs4 import BeautifulSoup

class USITCApiClient:
    """Client for interacting with the USITC HTS RESTful API."""
    
    # Base URL for the USITC RESTful API
    BASE_URL = "https://hts.usitc.gov/reststop"
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize the USITC API client.
        
        Args:
            cache_enabled: Whether to cache API responses
        """
        self.session = requests.Session()
        self.cache_enabled = cache_enabled
        self.cache = {}
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for HTS codes matching the query.
        
        Args:
            query: Search term (product description or HTS code)
            
        Returns:
            List of matching HTS codes with details
        """
        # Check cache first if enabled
        if self.cache_enabled and query in self.cache:
            return self.cache[query]
        
        # Try to search using the USITC RESTful API
        results = self._search_usitc_api(query)
        
        # If we couldn't find results, use fallback data for demo purposes
        if not results:
            print("API search failed, using fallback data")
            results = self._get_fallback_results(query)
        
        # Cache the results if enabled
        if self.cache_enabled:
            self.cache[query] = results
            
        return results
    
    def _search_usitc_api(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for HTS codes using the USITC RESTful API.
        
        Args:
            query: Search term (product description or HTS code)
            
        Returns:
            List of search results or empty list if the search fails
        """
        try:
            # Check if the query looks like an HTS code (e.g., 8708.10)
            is_hts_code = bool(re.match(r'^\d{4}(\.\d{2})?', query))
            
            if is_hts_code:
                # If it's an HTS code, use the export endpoint for more precise results
                return self._search_by_hts_code(query)
            else:
                # If it's a product description, use the search endpoint
                return self._search_by_description(query)
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return []
        except Exception as e:
            print(f"Error processing API response: {e}")
            return []
    
    def _search_by_description(self, description: str) -> List[Dict[str, Any]]:
        """
        Search for HTS codes by product description.
        
        Args:
            description: Product description
            
        Returns:
            List of search results
        """
        # Preprocess the query to improve search results
        # Remove hyphens and replace with spaces for better matching
        # Also remove any trailing punctuation
        preprocessed_query = description.replace('-', ' ').rstrip(':;,.')
        
        # Encode the query for URL
        encoded_query = urllib.parse.quote(preprocessed_query)
        
        # Use the search endpoint
        url = f"{self.BASE_URL}/search?keyword={encoded_query}"
        print(f"DEBUG: Searching USITC API by description: {url}")
        print(f"DEBUG: Original query: '{description}'")
        print(f"DEBUG: Preprocessed query: '{preprocessed_query}'")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://hts.usitc.gov/',
            'Origin': 'https://hts.usitc.gov'
        }
        
        response = self.session.get(url, headers=headers, timeout=10)
        
        # Print response status for debugging
        print(f"DEBUG: API response status: {response.status_code}")
        
        # If the response is successful, try to parse it
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API response: {data[:200]}...")  # Print first 200 chars for debugging
                
                # Parse the response
                results = self._parse_search_results(data)
                
                if results:
                    print(f"Successfully got {len(results)} results from description search")
                    return results
                else:
                    print("No results found in description search response")
                    return []
            except json.JSONDecodeError as e:
                print(f"Failed to parse API response as JSON: {e}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
                return []
        else:
            print(f"Description search API request failed with status code: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
            return []
    
    def _search_by_hts_code(self, hts_code: str) -> List[Dict[str, Any]]:
        """
        Search for HTS codes by HTS code.
        
        Args:
            hts_code: HTS code to search for
            
        Returns:
            List of search results
        """
        # Clean up the HTS code
        hts_code = hts_code.strip().rstrip(':;,.')
        
        # Extract the first 4 digits of the HTS code
        hts_prefix = hts_code[:4]
        
        # Calculate the range for the export endpoint
        hts_from = hts_prefix
        hts_to = hts_prefix + "99"
        
        # Use the export endpoint
        url = f"{self.BASE_URL}/exportList?from={hts_from}&to={hts_to}&format=JSON&styles=true"
        print(f"DEBUG: Searching USITC API by HTS code: {url}")
        print(f"DEBUG: HTS code: '{hts_code}'")
        print(f"DEBUG: HTS prefix: '{hts_prefix}'")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://hts.usitc.gov/',
            'Origin': 'https://hts.usitc.gov'
        }
        
        response = self.session.get(url, headers=headers, timeout=10)
        
        # Print response status for debugging
        print(f"DEBUG: API response status: {response.status_code}")
        
        # If the response is successful, try to parse it
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API response: {data[:200]}...")  # Print first 200 chars for debugging
                
                # Parse the response
                results = self._parse_export_results(data, hts_code)
                
                if results:
                    print(f"Successfully got {len(results)} results from HTS code search")
                    return results
                else:
                    print("No results found in HTS code search response")
                    return []
            except json.JSONDecodeError as e:
                print(f"Failed to parse API response as JSON: {e}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
                return []
        else:
            print(f"HTS code search API request failed with status code: {response.status_code}")
            print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
            return []
    
    def get_hts_details(self, hts_code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific HTS code.
        
        Args:
            hts_code: The HTS code to look up
            
        Returns:
            Detailed information about the HTS code or None if not found
        """
        # Try to get details using the export endpoint
        try:
            # Extract the first 4 digits of the HTS code
            hts_prefix = hts_code[:4]
            
            # Calculate the range for the export endpoint
            hts_from = hts_prefix
            hts_to = hts_prefix + "99"
            
            # Use the export endpoint
            url = f"{self.BASE_URL}/exportList?from={hts_from}&to={hts_to}&format=JSON&styles=true"
            print(f"Getting HTS details from: {url}")
            
            response = self.session.get(url, timeout=10)
            
            # Print response status and headers for debugging
            print(f"API response status: {response.status_code}")
            
            # If the response is successful, try to parse it
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"API response: {data[:200]}...")  # Print first 200 chars for debugging
                    
                    # Parse the response
                    results = self._parse_export_results(data, hts_code)
                    
                    # Find the exact HTS code
                    for result in results:
                        if result.get("hts_code") == hts_code:
                            return result
                    
                    # If we couldn't find the exact HTS code, return the first result
                    if results:
                        return results[0]
                except json.JSONDecodeError as e:
                    print(f"Failed to parse export API response as JSON: {e}")
                    print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
            else:
                print(f"Export API request failed with status code: {response.status_code}")
                print(f"Response content: {response.text[:200]}...")  # Print first 200 chars for debugging
        except requests.exceptions.RequestException as e:
            print(f"Failed to get HTS details: {e}")
        except Exception as e:
            print(f"Error processing HTS details: {e}")
        
        # Try to search for the exact code
        results = self.search(hts_code)
        
        for result in results:
            if result.get("hts_code") == hts_code:
                return result
        
        # If we couldn't find details, return a fallback result
        return self._get_fallback_results(hts_code)[0] if self._get_fallback_results(hts_code) else None
    
    def _parse_search_results(self, data: Any) -> List[Dict[str, Any]]:
        """
        Parse the search API response into a structured format.
        
        Args:
            data: Raw API response data
            
        Returns:
            Structured list of HTS code information
        """
        results = []
        
        # Try different response formats
        
        # Format 1: Array of objects
        if isinstance(data, list):
            for item in data:
                result = self._parse_result_item(item)
                if result:
                    results.append(result)
        
        # Format 2: Object with results array
        elif isinstance(data, dict) and "results" in data:
            for item in data["results"]:
                result = self._parse_result_item(item)
                if result:
                    results.append(result)
        
        # Format 3: Object with data.items array
        elif isinstance(data, dict) and "data" in data and "items" in data["data"]:
            for item in data["data"]["items"]:
                result = self._parse_result_item(item)
                if result:
                    results.append(result)
        
        return results
    
    def _parse_export_results(self, data: Any, query: str) -> List[Dict[str, Any]]:
        """
        Parse the export API response into a structured format.
        
        Args:
            data: Raw API response data
            query: The original query to filter results
            
        Returns:
            Structured list of HTS code information
        """
        results = []
        
        # Try different response formats
        
        # Format 1: Array of objects
        if isinstance(data, list):
            for item in data:
                result = self._parse_result_item(item)
                if result and (query in result.get("hts_code", "") or query.lower() in result.get("description", "").lower()):
                    results.append(result)
        
        # Format 2: Object with results array
        elif isinstance(data, dict) and "results" in data:
            for item in data["results"]:
                result = self._parse_result_item(item)
                if result and (query in result.get("hts_code", "") or query.lower() in result.get("description", "").lower()):
                    results.append(result)
        
        # Format 3: Object with data.items array
        elif isinstance(data, dict) and "data" in data and "items" in data["data"]:
            for item in data["data"]["items"]:
                result = self._parse_result_item(item)
                if result and (query in result.get("hts_code", "") or query.lower() in result.get("description", "").lower()):
                    results.append(result)
        
        return results
    
    def _parse_result_item(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a single result item from the API response.
        
        Args:
            item: Result item from the API
            
        Returns:
            Structured result item or None if parsing fails
        """
        # Try different field names for HTS code
        hts_code = None
        for field in ["htsno", "hts_code", "htsCode", "code", "number", "htsNumber"]:
            if field in item:
                hts_code = item[field]
                break
        
        # Try different field names for description
        description = None
        for field in ["description", "desc", "text", "title", "htsDescription"]:
            if field in item:
                description = item[field]
                break
        
        # If we don't have both HTS code and description, skip this item
        if not hts_code or not description:
            return None
        
        # Try different field names for rates
        general_rate = "N/A"
        for field in ["general_rate_of_duty", "generalRate", "general", "rate", "generalDuty"]:
            if field in item:
                general_rate = item[field]
                break
        
        # Try different field names for special rates
        special_rates = {}
        for field in ["special_rate_of_duty", "specialRates", "special", "rates", "specialDuty"]:
            if field in item:
                special_rates = self._parse_special_rates(item[field])
                break
        
        # Try different field names for column 2 rate
        column2_rate = "N/A"
        for field in ["column_2_rate_of_duty", "column2Rate", "column2", "col2", "column2Duty"]:
            if field in item:
                column2_rate = item[field]
                break
        
        # Try different field names for unit of quantity
        unit_of_quantity = ""
        for field in ["unit_of_quantity", "unit", "uom", "unitOfQuantity"]:
            if field in item:
                unit_of_quantity = item[field]
                break
        
        # Try different field names for additional info
        additional_info = ""
        for field in ["additional_info", "notes", "info", "additional", "additionalInfo"]:
            if field in item:
                additional_info = item[field]
                break
        
        return {
            "hts_code": hts_code,
            "description": description,
            "rates": {
                "general": general_rate,
                "special": special_rates,
                "column2": column2_rate
            },
            "unit_of_quantity": unit_of_quantity,
            "additional_info": additional_info
        }
    
    def _parse_special_rates(self, special_rates: Union[Dict[str, str], str, List[Dict[str, str]]]) -> Dict[str, str]:
        """
        Parse special rates from the API response.
        
        Args:
            special_rates: Special rates data from the API
            
        Returns:
            Structured dictionary of special rates by country/agreement
        """
        if isinstance(special_rates, dict):
            return special_rates
        elif isinstance(special_rates, str):
            # If it's a string, try to parse it as a structured format
            parsed = {}
            if special_rates:
                # Try different separators
                for separator in [';', ',', '|']:
                    if separator in special_rates:
                        parts = special_rates.split(separator)
                        for part in parts:
                            # Try different key-value separators
                            for kv_separator in [':', '-', '=']:
                                if kv_separator in part:
                                    key, value = part.split(kv_separator, 1)
                                    parsed[key.strip()] = value.strip()
                                    break
            return parsed
        elif isinstance(special_rates, list):
            # If it's a list, try to parse it as a list of objects
            parsed = {}
            for item in special_rates:
                if isinstance(item, dict):
                    # Try different field names for country/agreement
                    country = None
                    for field in ["country", "agreement", "code", "name"]:
                        if field in item:
                            country = item[field]
                            break
                    
                    # Try different field names for rate
                    rate = None
                    for field in ["rate", "value", "duty"]:
                        if field in item:
                            rate = item[field]
                            break
                    
                    if country and rate:
                        parsed[country] = rate
            return parsed
        else:
            return {}

    def get_trade_agreement_eligibility(self, hts_code: str, origin: str, destination: str) -> Dict[str, Any]:
        """
        Determine trade agreement eligibility for a given HTS code and countries.
        
        Args:
            hts_code: The HTS code
            origin: Country of origin code
            destination: Destination country code
            
        Returns:
            Dictionary with trade agreement eligibility information
        """
        # This is a simplified implementation that would need to be expanded
        # with real trade agreement logic or API calls
        
        # For the POC, we'll focus on US as the destination
        if destination != "US":
            return {"eligible_agreements": [], "details": "Only US destination supported in this POC"}
        
        # Get the HTS details
        hts_details = self.get_hts_details(hts_code)
        if not hts_details:
            return {"eligible_agreements": [], "details": "HTS code not found"}
        
        # Check special rates for the origin country
        special_rates = hts_details.get("rates", {}).get("special", {})
        eligible_agreements = []
        
        # USMCA eligibility
        if origin in ["CA", "MX"] and any(k in special_rates for k in ["CA", "MX", "USMCA"]):
            eligible_agreements.append({
                "agreement": "USMCA",
                "rate": special_rates.get("CA", special_rates.get("MX", special_rates.get("USMCA", "Free"))),
                "requirements": "Must meet USMCA rules of origin"
            })
        
        # US-Korea FTA
        if origin == "KR" and any(k in special_rates for k in ["KR", "US-KR"]):
            eligible_agreements.append({
                "agreement": "US-KR FTA",
                "rate": special_rates.get("KR", special_rates.get("US-KR", "Free")),
                "requirements": "Must meet US-Korea FTA rules of origin"
            })
            
        # US-Japan Trade Agreement
        if origin == "JP" and any(k in special_rates for k in ["JP", "US-JP"]):
            eligible_agreements.append({
                "agreement": "US-Japan Trade Agreement",
                "rate": special_rates.get("JP", special_rates.get("US-JP", "Free")),
                "requirements": "Must meet US-Japan Trade Agreement rules of origin"
            })
        
        return {
            "eligible_agreements": eligible_agreements,
            "details": "Based on country of origin and special rates"
        }
    
    def _get_fallback_results(self, query: str) -> List[Dict[str, Any]]:
        """
        Get minimal fallback results when API search fails.
        This is a simplified version that doesn't rely on hardcoded product types.
        
        Args:
            query: Search term (product description or HTS code)
            
        Returns:
            List of minimal fallback HTS code results
        """
        print(f"WARNING: API search failed for '{query}', using minimal fallback")
        
        # If the query looks like an HTS code, return a minimal result for that code
        if re.search(r'\d{4}(\.\d{2})?', query):
            hts_code = query.strip().lower()
            return [
                {
                    "hts_code": hts_code,
                    "description": "HTS code information not available",
                    "rates": {
                        "general": "N/A",
                        "special": {},
                        "column2": "N/A"
                    },
                    "unit_of_quantity": "",
                    "additional_info": "Please verify this HTS code with official sources"
                }
            ]
        
        # For product descriptions, return a minimal placeholder
        return [
            {
                "hts_code": "0000.00.0000",
                "description": "No matching HTS code found",
                "rates": {
                    "general": "N/A",
                    "special": {},
                    "column2": "N/A"
                },
                "unit_of_quantity": "",
                "additional_info": "Please try a different search term or consult with a customs expert"
            }
        ]
