"""
Product Analyzer for TariffDoc AI

This module handles the analysis of product descriptions and coordinates
between the LLM service and the USITC API client.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from .api_client import USITCApiClient
from .llm_service import LLMService

class ProductAnalyzer:
    """Analyzer for product descriptions and tariff information."""
    
    def __init__(self, api_client: USITCApiClient, llm_service: Optional[LLMService] = None):
        """
        Initialize the product analyzer.
        
        Args:
            api_client: USITC API client
            llm_service: Optional LLM service for enhanced analysis
        """
        self.api_client = api_client
        self.llm_service = llm_service
    
    def analyze_product(self, 
                       product_description: str, 
                       origin_country: str, 
                       destination_country: str) -> Dict[str, Any]:
        """
        Analyze a product description and retrieve tariff information.
        
        Args:
            product_description: Description of the product
            origin_country: Country of origin code
            destination_country: Destination country code
            
        Returns:
            Dictionary with analysis results
        """
        # Step 1: Enhance the search query using LLM if available
        search_terms = self._get_search_terms(product_description)
        
        # Get the product analysis if available
        product_analysis = None
        if self.llm_service and self.llm_service.is_enabled():
            analysis_key = f"analysis_{product_description}"
            if analysis_key in self.llm_service.cache:
                product_analysis = self.llm_service.cache[analysis_key]
        
        # Step 2: Search for HTS codes using the enhanced terms
        all_results = []
        for term in search_terms:
            results = self.api_client.search(term)
            # Tag results with the search term that found them
            for result in results:
                if "search_terms" not in result:
                    result["search_terms"] = []
                result["search_terms"].append(term)
            all_results.extend(results)
        
        # Remove duplicates based on HTS code
        unique_results = self._deduplicate_results(all_results)
        
        # Filter results for relevance
        filtered_results = self._filter_results_for_relevance(unique_results, product_description, search_terms)
        
        # Step 3: Analyze confidence levels using LLM if available
        if self.llm_service and self.llm_service.is_enabled():
            filtered_results = self.llm_service.analyze_hs_code_confidence(
                product_description, filtered_results
            )
            
            # Enhance the confidence reasoning with material and function analysis
            if product_analysis:
                for result in filtered_results:
                    self._enhance_confidence_reasoning(result, product_analysis, product_description)
        
        # Step 4: Sort results by confidence (if available) or HTS code
        sorted_results = self._sort_results(filtered_results)
        
        # Return the analysis results
        return {
            "product_description": product_description,
            "search_terms": search_terms,
            "origin_country": origin_country,
            "destination_country": destination_country,
            "hts_results": sorted_results,
            "product_analysis": product_analysis
        }
    
    def _enhance_confidence_reasoning(self, 
                                     result: Dict[str, Any], 
                                     product_analysis: Dict[str, Any],
                                     product_description: str) -> None:
        """
        Enhance the confidence reasoning with material and function analysis.
        
        Args:
            result: HTS result to enhance
            product_analysis: Product analysis from LLM
            product_description: Original product description
        """
        # Extract information from product analysis
        materials = product_analysis.get("MATERIALS", [])
        function = product_analysis.get("FUNCTION", "")
        industry_terms = product_analysis.get("INDUSTRY_TERMS", [])
        
        # Convert to strings if they're lists
        materials_str = ", ".join(materials) if isinstance(materials, list) else str(materials)
        industry_terms_str = ", ".join(industry_terms) if isinstance(industry_terms, list) else str(industry_terms)
        
        # Create enhanced reasoning
        hts_description = result.get("description", "")
        confidence = result.get("confidence", "Medium")
        
        # Check for material matches
        material_matches = []
        for material in materials if isinstance(materials, list) else [materials]:
            if material.lower() in hts_description.lower():
                material_matches.append(material)
        
        # Check for function matches
        function_match = function.lower() in hts_description.lower() if function else False
        
        # Create detailed reasoning
        detailed_reasoning = []
        
        if material_matches:
            detailed_reasoning.append(f"Material match: {', '.join(material_matches)}")
        
        if function_match:
            detailed_reasoning.append(f"Function match: {function}")
        
        if "search_terms" in result:
            search_term = result["search_terms"][0] if result["search_terms"] else ""
            if search_term != product_description:
                detailed_reasoning.append(f"Found via search term: '{search_term}'")
        
        # Add original confidence reason if available
        original_reason = result.get("confidence_reason", "")
        if original_reason and original_reason not in detailed_reasoning:
            detailed_reasoning.append(original_reason)
        
        # Update the confidence reason
        if detailed_reasoning:
            result["confidence_reason"] = " | ".join(detailed_reasoning)
            result["detailed_analysis"] = {
                "materials": materials,
                "function": function,
                "industry_terms": industry_terms,
                "material_matches": material_matches,
                "function_match": function_match
            }
    
    def get_tariff_document_data(self, 
                               product_description: str,
                               hts_code: str,
                               origin_country: str,
                               destination_country: str) -> Dict[str, Any]:
        """
        Get comprehensive tariff information for document generation.
        
        Args:
            product_description: Description of the product
            hts_code: Selected HTS code
            origin_country: Country of origin code
            destination_country: Destination country code
            
        Returns:
            Dictionary with all tariff information needed for document generation
        """
        # Get HTS details
        hts_details = self.api_client.get_hts_details(hts_code)
        if not hts_details:
            # If no details found, create a minimal structure
            hts_details = {
                "hts_code": hts_code,
                "description": "No description available",
                "rates": {
                    "general": "N/A",
                    "special": {},
                    "column2": "N/A"
                }
            }
        
        # Get trade agreement eligibility
        trade_agreements = self.api_client.get_trade_agreement_eligibility(
            hts_code, origin_country, destination_country
        )
        
        # Generate explanation using LLM if available
        explanation = ""
        if self.llm_service and self.llm_service.is_enabled():
            explanation = self.llm_service.generate_tariff_explanation(
                hts_code,
                hts_details.get("description", ""),
                hts_details.get("rates", {}),
                {"origin": origin_country, "destination": destination_country},
                trade_agreements
            )
        
        # Get product analysis if available
        classification_analysis = None
        if self.llm_service and self.llm_service.is_enabled():
            analysis_key = f"analysis_{product_description}"
            if analysis_key in self.llm_service.cache:
                product_analysis = self.llm_service.cache[analysis_key]
                
                # Extract relevant information for the document
                classification_analysis = {
                    "materials": product_analysis.get("MATERIALS", []),
                    "function": product_analysis.get("FUNCTION", ""),
                    "industry_terms": product_analysis.get("INDUSTRY_TERMS", []),
                    "hts_terminology": product_analysis.get("HTS_TERMINOLOGY", "")
                }
                
                # Add confidence reasoning if available in the HTS details
                if "confidence_reason" in hts_details:
                    classification_analysis["confidence_reason"] = hts_details["confidence_reason"]
                
                # Add detailed analysis if available
                if "detailed_analysis" in hts_details:
                    classification_analysis.update(hts_details["detailed_analysis"])
        
        # Compile all data for document generation
        document_data = {
            "product_description": product_description,
            "hts_code": hts_code,
            "hts_description": hts_details.get("description", ""),
            "rates": hts_details.get("rates", {}),
            "unit_of_quantity": hts_details.get("unit_of_quantity", ""),
            "additional_info": hts_details.get("additional_info", ""),
            "origin_country": origin_country,
            "destination_country": destination_country,
            "trade_agreements": trade_agreements,
            "explanation": explanation
        }
        
        # Add classification analysis if available
        if classification_analysis:
            document_data["classification_analysis"] = classification_analysis
        
        return document_data
    
    def _get_search_terms(self, product_description: str) -> List[str]:
        """
        Get search terms for the product description.
        
        Args:
            product_description: Original product description
            
        Returns:
            List of search terms
        """
        if self.llm_service and self.llm_service.is_enabled():
            # Use LLM to enhance the search query and identify appropriate HTS codes
            terms = self.llm_service.enhance_search_query(product_description)
            
            # Always include the original description
            if product_description not in terms:
                terms.append(product_description)
            
            return terms
        else:
            # Without LLM, just use the original description
            return [product_description]
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate HTS code results.
        
        Args:
            results: List of HTS code results
            
        Returns:
            Deduplicated list of results
        """
        unique_results = {}
        for result in results:
            hts_code = result.get("hts_code", "")
            if hts_code and hts_code not in unique_results:
                unique_results[hts_code] = result
        
        return list(unique_results.values())
    
    def _filter_results_for_relevance(self, results: List[Dict[str, Any]], product_description: str, search_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Filter results for relevance based on product description and search terms.
        Enhanced version with better scoring and filtering.
        
        Args:
            results: List of HTS code results
            product_description: Original product description
            search_terms: List of search terms used
            
        Returns:
            Filtered list of results
        """
        if not results:
            return []
        
        # Convert product description and search terms to lowercase for case-insensitive matching
        product_description_lower = product_description.lower()
        search_terms_lower = [term.lower() for term in search_terms]
        
        # Extract key words from product description (excluding common words)
        common_words = {"a", "an", "the", "and", "or", "for", "with", "without", "of", "in", "on", "at", "to", "from", 
                        "by", "as", "is", "are", "was", "were", "be", "been", "being"}
        product_words = set()
        for word in product_description_lower.split():
            word = word.strip(",.;:()[]{}\"'")
            if word and word not in common_words and len(word) > 1:
                product_words.add(word)
        
        # Filter results
        filtered_results = []
        for result in results:
            description = result.get("description", "").lower()
            hts_code = result.get("hts_code", "").lower()
            
            # Skip results with HTS codes that start with "0102" (livestock)
            if hts_code.startswith("0102"):
                continue
            
            # Calculate relevance score
            relevance_score = 0
            
            # Check if any search term is in the description
            for term in search_terms_lower:
                if term in description:
                    relevance_score += 3
                    # Give extra points for exact HTS code matches
                    if term.replace('.', '').isdigit() and term in hts_code:
                        relevance_score += 5
                    break
            
            # Check if any key word from product description is in the description
            for word in product_words:
                if word in description:
                    relevance_score += 1
            
            # Check if the result has search terms that match the product description
            if "search_terms" in result:
                for term in result["search_terms"]:
                    if term.lower() == product_description_lower:
                        relevance_score += 2
                        break
            
            # Bonus points for specific product categories based on the product description
            if "bumper" in product_description_lower and ("bumper" in description or "8708.10" in hts_code):
                relevance_score += 5
            elif "fastener" in product_description_lower and ("fastener" in description or "screw" in description or "bolt" in description):
                relevance_score += 4
            elif "plastic" in product_description_lower and "plastic" in description:
                relevance_score += 3
            
            # Include result if it has a minimum relevance score
            if relevance_score >= 1:
                # Add relevance score to result for debugging
                result["relevance_score"] = relevance_score
                filtered_results.append(result)
        
        # If no results pass the filter, return the original results
        if not filtered_results and results:
            print(f"WARNING: No results passed the relevance filter. Returning original results.")
            return results
        
        return filtered_results
    
    def _sort_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort results by confidence (if available) or HTS code.
        
        Args:
            results: List of HTS code results
            
        Returns:
            Sorted list of results
        """
        # Check if confidence scores are available
        has_confidence = any("confidence" in result for result in results)
        
        # Check if relevance scores are available
        has_relevance = any("relevance_score" in result for result in results)
        
        if has_confidence and has_relevance:
            # Define a confidence score mapping
            confidence_map = {"High": 3, "Medium": 2, "Low": 1}
            
            # Sort by relevance score (high to low), then confidence (high to low), then HTS code
            return sorted(
                results,
                key=lambda x: (
                    -x.get("relevance_score", 0),
                    -confidence_map.get(x.get("confidence", "Medium"), 0),
                    x.get("hts_code", "")
                )
            )
        elif has_confidence:
            # Define a confidence score mapping
            confidence_map = {"High": 3, "Medium": 2, "Low": 1}
            
            # Sort by confidence (high to low) and then by HTS code
            return sorted(
                results,
                key=lambda x: (
                    -confidence_map.get(x.get("confidence", "Medium"), 0),
                    x.get("hts_code", "")
                )
            )
        elif has_relevance:
            # Sort by relevance score (high to low) and then by HTS code
            return sorted(
                results,
                key=lambda x: (
                    -x.get("relevance_score", 0),
                    x.get("hts_code", "")
                )
            )
        else:
            # Sort by HTS code only
            return sorted(results, key=lambda x: x.get("hts_code", ""))
