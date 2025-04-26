# TariffDoc AI - System Patterns

## System Architecture

TariffDoc AI follows a modular architecture with clear separation of concerns:

1. **Frontend Layer**: Streamlit-based user interface
2. **Service Layer**: Core business logic components
3. **Integration Layer**: External API interactions
4. **Utility Layer**: Helper functions and tools

## Key Technical Decisions

### 1. Streamlit as UI Framework

Streamlit was chosen for its simplicity and rapid development capabilities. It provides:
- Easy-to-create interactive web interfaces
- Built-in state management
- Simple deployment options
- Native support for data visualization

### 2. Modular Component Design

The application is structured with modular components that have specific responsibilities:
- **API Client**: Handles all communication with the USITC API
- **LLM Service**: Manages interactions with OpenAI's API
- **Product Analyzer**: Coordinates between services to analyze products
- **PDF Generator**: Creates standardized PDF documents

### 3. Fallback Mechanisms

The system implements fallback mechanisms to ensure functionality even when external services are unavailable:
- Mock data for USITC API when the actual API fails
- Graceful degradation when LLM features are not available
- Default values for missing information

### 4. Caching Strategy

Performance optimization through strategic caching:
- API responses are cached to reduce redundant calls
- LLM responses are cached to minimize API usage
- Streamlit's built-in caching for data loading functions

### 5. Environment-Based Configuration

Configuration management through environment variables:
- OpenAI API key and model selection
- Optional features can be enabled/disabled
- Easy configuration through .env file

## Architecture Patterns

### Service Pattern

Each major component is implemented as a service class with:
- Clear initialization parameters
- Well-defined public methods
- Internal helper methods
- Consistent error handling

### Adapter Pattern

The API client acts as an adapter between the USITC API and the application:
- Translates between different data formats
- Handles various response structures
- Provides a consistent interface to the rest of the application

### Strategy Pattern

The product analyzer implements a strategy pattern for search enhancement:
- Uses LLM-enhanced search when available
- Falls back to basic search when LLM is not available
- Allows for future alternative search strategies

### Factory Pattern

The PDF generator acts as a factory for creating document elements:
- Standardized document structure
- Consistent styling
- Reusable components

## Data Flow

1. User inputs product description and country information
2. System enhances search terms (with LLM if available)
3. API client retrieves matching HTS codes
4. Product analyzer processes and ranks results
5. User selects an HTS code
6. System retrieves detailed information and trade agreement eligibility
7. PDF generator creates a downloadable document

This architecture provides a solid foundation while allowing for future enhancements and scalability.
