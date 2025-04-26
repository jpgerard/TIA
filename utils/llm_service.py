"""
LLM Service for TariffDoc AI

This module handles integration with OpenAI's API for enhancing product descriptions
and generating explanations of tariff information.
"""

import os
import openai
import json
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMService:
    """Service for interacting with OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", cache_enabled: bool = True):
        """
        Initialize the LLM service.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model: OpenAI model to use
            cache_enabled: Whether to cache LLM responses
        """
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: No OpenAI API key provided. LLM features will be disabled.")
            
        self.model = model
        self.cache_enabled = cache_enabled
        self.cache = {}
        
        # Set the API key for the openai module
        if self.api_key:
            openai.api_key = self.api_key
    
    def is_enabled(self) -> bool:
        """Check if the LLM service is enabled (has API key)."""
        return bool(self.api_key)
    
    def enhance_search_query(self, product_description: str) -> List[str]:
        """
        Use LLM to enhance the product description for better HTS matching.
        This improved version focuses on identifying specific HTS codes.
        
        Args:
            product_description: Original product description
            
        Returns:
            List of enhanced search terms including specific HTS codes
        """
        if not self.is_enabled():
            # Fallback when LLM is not available
            return [product_description]
            
        # Check cache first if enabled
        cache_key = f"enhance_{product_description}"
        if self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            prompt = f"""
            You are a tariff classification expert with deep knowledge of the Harmonized Tariff Schedule (HTS).
            
            IMPORTANT CONTEXT ABOUT HTS:
            - The HTS is not a list of specific products but a hierarchical classification system
            - Products are categorized based primarily on material composition and function
            - The HTS uses formal terminology that often differs from common commercial terms
            - For example, "phone chargers" are listed as "static converters for telecommunication devices"
            
            TASK:
            Analyze this product description and identify the appropriate HTS codes and search terms:
            
            Product: {product_description}
            
            Provide the following:
            1. MATERIALS: List the primary materials (e.g., plastic, steel, textile)
            2. FUNCTION: Describe the primary function in formal terms
            3. INDUSTRY_TERMS: Provide industry-specific terminology
            4. HTS_TERMINOLOGY: Convert to formal HTS terminology
            5. HTS_CODES: Provide 3-5 specific HTS codes that would be appropriate for this product. Be as specific as possible, including subheadings (e.g., 8708.10.60 rather than just 8708.10). For automotive parts, consider codes like 8708.10.60 for bumper parts, 8708.29 for body parts, etc.
            6. SEARCH_TERMS: Generate 5-7 specific search terms that would yield accurate HTS codes
            
            Format your response as a structured list with clear headings for each section.
            
            IMPORTANT: For HTS_CODES, provide the most specific codes possible, including all available digits and subheadings. For example, use "8708.10.6030" instead of just "8708.10" for automotive bumper parts. The more specific the code, the better the search results will be.
            """
            
            # Check if the model supports JSON response format
            supports_json_format = self.model in ["gpt-4-turbo", "gpt-4-1106-preview", "gpt-4-0125-preview", "gpt-3.5-turbo-1106"]
            
            if supports_json_format:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,  # Lower temperature for more focused responses
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content.strip())
            else:
                # For models that don't support JSON response format
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt + "\n\nEven though I asked for JSON, please format your response as a structured list with clear headings."}],
                    temperature=0.3,  # Lower temperature for more focused responses
                    max_tokens=500
                )
                
                # Parse the text response into a structured format
                content = response.choices[0].message.content.strip()
                result = self._parse_structured_response(content, product_description)
            
            # Extract search terms and HTS codes from the response
            search_terms = result.get("SEARCH_TERMS", [])
            hts_codes = result.get("HTS_CODES", [])
            
            # If no search terms were provided, fall back to the original description
            if not search_terms:
                search_terms = [product_description]
            
            # Always include the original description as one of the search terms
            if product_description not in search_terms:
                search_terms.append(product_description)
            
            # Add HTS codes to the search terms
            for code in hts_codes:
                # Clean up the code (remove any text after the code and any trailing punctuation)
                code_parts = code.split(' ', 1)
                clean_code = code_parts[0].strip().rstrip(':;,.')
                
                # Only add valid HTS codes (should contain numbers and dots)
                if any(c.isdigit() for c in clean_code) and '.' in clean_code:
                    if clean_code not in search_terms:
                        search_terms.append(clean_code)
                        print(f"DEBUG: Adding HTS code '{clean_code}' to search terms")
            
            # Store the full analysis for later use
            self.cache[f"analysis_{product_description}"] = result
            
            # Cache the results if enabled
            if self.cache_enabled:
                self.cache[cache_key] = search_terms
                
            return search_terms
            
        except Exception as e:
            print(f"LLM query failed: {e}")
            # Fallback to original description
            return [product_description]
    
    def _parse_structured_response(self, content: str, product_description: str) -> Dict[str, Any]:
        """
        Parse a structured text response into a dictionary.
        
        Args:
            content: The structured text response from the LLM
            product_description: The original product description
            
        Returns:
            A dictionary with the parsed information
        """
        result = {
            "MATERIALS": [],
            "FUNCTION": "",
            "INDUSTRY_TERMS": [],
            "HTS_TERMINOLOGY": "",
            "HTS_CODES": [],
            "SEARCH_TERMS": []
        }
        
        # Simple parsing logic for structured text
        current_section = None
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if "MATERIALS:" in line.upper() or "1. MATERIALS" in line:
                current_section = "MATERIALS"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "FUNCTION:" in line.upper() or "2. FUNCTION" in line:
                current_section = "FUNCTION"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "INDUSTRY" in line.upper() or "3. INDUSTRY" in line:
                current_section = "INDUSTRY_TERMS"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "HTS_TERMINOLOGY" in line.upper() or "4. HTS_TERMINOLOGY" in line:
                current_section = "HTS_TERMINOLOGY"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "HTS_CODES" in line.upper() or "5. HTS_CODES" in line:
                current_section = "HTS_CODES"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
            elif "SEARCH" in line.upper() or "6. SEARCH" in line:
                current_section = "SEARCH_TERMS"
                line = line.split(":", 1)[1].strip() if ":" in line else ""
                
            # Process content based on current section
            if current_section and line and not line.startswith(str(current_section)):
                if current_section == "MATERIALS":
                    if line.startswith("- "):
                        result["MATERIALS"].append(line[2:])
                    elif line.startswith("* "):
                        result["MATERIALS"].append(line[2:])
                    elif "," in line:
                        result["MATERIALS"].extend([m.strip() for m in line.split(",")])
                    else:
                        result["MATERIALS"].append(line)
                elif current_section == "FUNCTION":
                    result["FUNCTION"] += line + " "
                elif current_section == "INDUSTRY_TERMS":
                    if line.startswith("- "):
                        result["INDUSTRY_TERMS"].append(line[2:])
                    elif line.startswith("* "):
                        result["INDUSTRY_TERMS"].append(line[2:])
                    elif "," in line:
                        result["INDUSTRY_TERMS"].extend([t.strip() for t in line.split(",")])
                    else:
                        result["INDUSTRY_TERMS"].append(line)
                elif current_section == "HTS_TERMINOLOGY":
                    result["HTS_TERMINOLOGY"] += line + " "
                elif current_section == "HTS_CODES":
                    if line.startswith("- "):
                        result["HTS_CODES"].append(line[2:])
                    elif line.startswith("* "):
                        result["HTS_CODES"].append(line[2:])
                    elif "," in line:
                        result["HTS_CODES"].extend([c.strip() for c in line.split(",")])
                    else:
                        result["HTS_CODES"].append(line)
                elif current_section == "SEARCH_TERMS":
                    if line.startswith("- "):
                        result["SEARCH_TERMS"].append(line[2:])
                    elif line.startswith("* "):
                        result["SEARCH_TERMS"].append(line[2:])
                    elif line.startswith('"') and line.endswith('"'):
                        result["SEARCH_TERMS"].append(line.strip('"'))
                    elif "," in line:
                        result["SEARCH_TERMS"].extend([t.strip() for t in line.split(",")])
                    else:
                        result["SEARCH_TERMS"].append(line)
        
        # Clean up the results
        result["FUNCTION"] = result["FUNCTION"].strip()
        result["HTS_TERMINOLOGY"] = result["HTS_TERMINOLOGY"].strip()
        
        # If we couldn't parse any search terms, use the original description
        if not result["SEARCH_TERMS"]:
            result["SEARCH_TERMS"] = [product_description]
            
        return result
    
    def generate_tariff_explanation(self, 
                                   hts_code: str, 
                                   description: str, 
                                   rates: Dict[str, Any], 
                                   countries: Dict[str, str],
                                   trade_agreements: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate plain-language explanation of tariff information.
        
        Args:
            hts_code: The HTS code
            description: Product description
            rates: Dictionary of duty rates
            countries: Dictionary with origin and destination countries
            trade_agreements: Optional trade agreement eligibility information
            
        Returns:
            Plain-language explanation of the tariff information
        """
        if not self.is_enabled():
            # Fallback when LLM is not available
            return f"Tariff information for {description} (HTS: {hts_code})"
            
        # Check cache first if enabled
        cache_key = f"explain_{hts_code}_{countries['origin']}_{countries['destination']}"
        if self.cache_enabled and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Format rates for the prompt
            rates_str = json.dumps(rates, indent=2)
            
            # Format trade agreements for the prompt
            if trade_agreements:
                agreements_str = json.dumps(trade_agreements, indent=2)
            else:
                agreements_str = "No trade agreement information available"
            
            prompt = f"""
            You are a tariff expert. Explain the following tariff information in plain language:
            
            HTS Code: {hts_code}
            Description: {description}
            Rates: {rates_str}
            Countries: Origin - {countries['origin']}, Destination - {countries['destination']}
            Trade Agreements: {agreements_str}
            
            Provide:
            1. A simple explanation of what this product category includes
            2. An interpretation of the applicable duty rates
            3. Potential trade agreement benefits
            4. Key considerations for importers
            
            Keep your response under 250 words and focus on practical implications.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=350
            )
            
            explanation = response.choices[0].message.content.strip()
            
            # Cache the results if enabled
            if self.cache_enabled:
                self.cache[cache_key] = explanation
                
            return explanation
            
        except Exception as e:
            print(f"LLM explanation failed: {e}")
            # Fallback explanation
            return f"This product ({description}) is classified under HTS code {hts_code}. The general duty rate is {rates.get('general', 'unknown')}. Check with a customs broker for specific details."
    
    def analyze_hs_code_confidence(self, product_description: str, hts_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze the confidence level for HTS code matches based on product description.
        
        Args:
            product_description: Original product description
            hts_results: List of HTS code results from the API
            
        Returns:
            Enhanced list of HTS results with confidence scores
        """
        if not self.is_enabled() or not hts_results:
            # Fallback when LLM is not available or no results
            for result in hts_results:
                result["confidence"] = "Medium"
            return hts_results
            
        try:
            # Format the HTS results for the prompt
            hts_items = []
            for i, result in enumerate(hts_results[:10]):  # Limit to top 10 for prompt size
                hts_items.append(f"{i+1}. {result['hts_code']} - {result['description']}")
            
            hts_list = "\n".join(hts_items)
            
            prompt = f"""
            You are a tariff classification expert. Analyze the following product description 
            and potential HTS code matches. Assign a confidence score (High, Medium, or Low) 
            to each match based on how well it describes the product.
            
            Product Description: {product_description}
            
            Potential HTS Codes:
            {hts_list}
            
            For each numbered item, provide only the confidence level (High, Medium, or Low) 
            and a very brief explanation (10 words or less). Format as:
            1. [Confidence]: [Brief reason]
            2. [Confidence]: [Brief reason]
            ...
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=250
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Parse the analysis and update the results
            lines = analysis.split('\n')
            for line in lines:
                if ':' not in line:
                    continue
                    
                try:
                    # Extract the index and confidence
                    parts = line.split(':', 1)
                    index_part = parts[0].strip()
                    if not index_part[0].isdigit():
                        continue
                        
                    index = int(index_part.split('.')[0]) - 1
                    confidence_part = parts[1].strip()
                    
                    # Extract confidence level
                    if "high" in confidence_part.lower():
                        confidence = "High"
                    elif "medium" in confidence_part.lower():
                        confidence = "Medium"
                    elif "low" in confidence_part.lower():
                        confidence = "Low"
                    else:
                        confidence = "Medium"  # Default
                    
                    # Update the result if index is valid
                    if 0 <= index < len(hts_results):
                        hts_results[index]["confidence"] = confidence
                        hts_results[index]["confidence_reason"] = confidence_part
                        
                except Exception as e:
                    print(f"Error parsing confidence line: {e}")
                    continue
            
            # Set default confidence for any results without a score
            for result in hts_results:
                if "confidence" not in result:
                    result["confidence"] = "Medium"
                    result["confidence_reason"] = "Default assessment"
            
            return hts_results
            
        except Exception as e:
            print(f"LLM confidence analysis failed: {e}")
            # Fallback confidence assignment
            for result in hts_results:
                result["confidence"] = "Medium"
            return hts_results
