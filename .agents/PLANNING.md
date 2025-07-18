# 🗺️ Planning

This document outlines the architecture, goals, and conventions for the Show Up Crawler project.

## 🚀 Project Goals

The primary goal of this project is to create a web crawler that extracts information about crypto-related events happening in Buenos Aires from various event websites. The initial focus will be on `lu.ma`.

The extracted data should include:
- Event title
- Date and time (start/end with timezone)
- Location (full address, city, country, coordinates)
- Description
- Organizer
- Event URL
- Event metadata (type, visibility, API ID)
- Cover image and additional details

## 🏗️ Architecture

The project will be built using Python and the Scrapy framework with Playwright for JavaScript-heavy pages.

- **Crawler**: A Scrapy spider will be developed to crawl `lu.ma` and other target websites.
- **Data Extraction**: Multi-layer extraction approach:
  - **Primary**: JSON data extraction from embedded structured data
  - **Fallback**: HTML parsing using CSS selectors
  - **Components**: Modular extractors for different data sources
- **Data Storage**: Initially, the scraped data will be stored in a JSON file. In the future, we might consider a database like PostgreSQL or MongoDB.
- **Configuration**: Project settings and configurations will be managed in `scrapy.cfg` and the Scrapy settings file.

### Data Flow Architecture:
```
Scrapy Spider → Playwright → JsonExtractor → Enhanced EventItem → Enhanced JSON Pipeline → Complete Events JSON
```

### Component Structure:
```
show_up/
├── extractors/          # Data extraction components
│   ├── base.py         # Base extractor interface
│   └── json_extractor.py # JSON extraction logic
├── utils/              # Utility functions
│   └── validation.py   # Data validation helpers
├── spiders/            # Scrapy spiders
├── items.py            # Enhanced data models
├── pipelines.py        # Enhanced data processing
└── settings.py         # Configuration
```

## 🎨 Code Style & Conventions

- **Language**: Python 3.13+ with modern type hints.
- **Package Manager**: `uv` will be used for managing Python dependencies.
- **Testing**: `pytest` will be used for testing.
- **Linting & Formatting**: `ruff` will be used for linting and formatting to ensure code quality.
- **Modularity**: Code will be organized into spiders, items, and pipelines as per Scrapy's conventions.

## ⛓️ Constraints

- Adhere to the rules in `.agents/RULES.md`.
- Do not add any new dependencies without prior discussion and approval.
- All code must be tested.
- Maintain backward compatibility with existing functionality.
- Follow modular design principles for extensibility.

---

## 🚀 Enhanced JSON Data Extraction Feature

### 📋 Feature Overview

**Problem**: Current spider extracts incomplete event data (null values for dates, locations)  
**Solution**: Implement JSON data extraction from embedded structured data within HTML responses  
**Status**: Planned for implementation

### 🔬 Current State Analysis

#### Problems Identified:
1. **Incomplete Data Extraction**: `crypto_events.json` shows null values for critical fields
2. **Ineffective Selectors**: Current CSS selectors don't match Luma's actual HTML structure
3. **Missed Rich Data**: HTML files contain complete JSON structures that are ignored
4. **Poor Data Quality**: Only extracting titles and URLs, missing dates, locations, organizers

#### Available Data in HTML:
From analysis of `output/html/21MeetUp__JULIO.html`:
- **Complete Event Details**: Names, dates, locations, coordinates
- **Structured JSON**: Embedded in script tags with full event metadata
- **Rich Location Data**: Full addresses, coordinates, place IDs
- **Event Metadata**: Types, visibility, organizer info, timezones

### 🎯 Technical Specifications

#### Enhanced Data Model:
```python
class EventItem(scrapy.Item):
    # Basic fields
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    
    # Temporal fields
    date = scrapy.Field()          # Start date
    end_date = scrapy.Field()      # End date
    timezone = scrapy.Field()      # Event timezone
    
    # Location fields
    location = scrapy.Field()      # Simple location string
    full_address = scrapy.Field()  # Complete address
    city = scrapy.Field()          # City
    country = scrapy.Field()       # Country
    coordinates = scrapy.Field()   # Lat/lng coordinates
    place_id = scrapy.Field()      # Google Place ID
    
    # Metadata fields
    event_type = scrapy.Field()    # Event type
    visibility = scrapy.Field()    # Public/private
    api_id = scrapy.Field()        # Luma API ID
    cover_url = scrapy.Field()     # Cover image URL
    organizer = scrapy.Field()     # Event organizer
    guest_count = scrapy.Field()   # Number of guests
    
    # Technical fields
    html_content = scrapy.Field()  # Processed HTML
    raw_html = scrapy.Field()      # Raw HTML
    extraction_method = scrapy.Field()  # How data was extracted
```

#### JSON Extraction Patterns:
```python
JSON_EXTRACTION_PATTERNS = [
    r'"event":\s*\{[^}]+(?:\{[^}]*\}[^}]*)*\}',
    r'window\.__INITIAL_DATA__\s*=\s*({.+?});',
    r'<script[^>]*>.*?({.*?"event".*?}.*?)</script>'
]
```

### 🏗️ Implementation Architecture

#### Phase 1: Data Model Enhancement
- **Extend EventItem**: Add comprehensive fields for complete event data
- **Maintain Compatibility**: Ensure existing pipelines continue working
- **Add Validation**: Type hints and field validation helpers

#### Phase 2: JSON Extraction Logic
- **Create JsonExtractor**: Reusable class for JSON data extraction
- **Multiple Patterns**: Support various JSON embedding patterns
- **Error Handling**: Graceful degradation to HTML parsing
- **Logging**: Comprehensive extraction status logging

#### Phase 3: Spider Enhancement
- **Integrate JsonExtractor**: Update LumaSpider to use new extraction logic
- **Maintain Playwright**: Keep existing browser automation
- **Enhanced Parsing**: Improve event page parsing
- **Debug Support**: Better debugging and error reporting

#### Phase 4: Pipeline Updates
- **Enhanced Output**: Richer JSON output with complete metadata
- **Backward Compatibility**: Support existing JSON structure
- **Performance**: Optimize data processing and storage
- **Configuration**: Allow customization of extraction behavior

#### Phase 5: Testing & Documentation
- **Unit Tests**: Comprehensive test coverage for all components
- **Integration Tests**: End-to-end testing with sample HTML
- **Documentation**: Update README and inline documentation
- **Validation**: Test against all existing HTML files

### 🎯 Success Criteria

#### Functional Requirements:
1. **Complete Data Extraction**: Extract all available event data fields
2. **High Success Rate**: >95% successful extraction from HTML files
3. **Backward Compatibility**: Existing functionality remains intact
4. **Error Resilience**: Graceful handling of malformed data
5. **Performance**: No significant performance degradation

#### Quality Requirements:
1. **Code Coverage**: >90% test coverage for new code
2. **Documentation**: Complete inline documentation and README updates
3. **Logging**: Comprehensive logging for debugging and monitoring
4. **Configuration**: Flexible configuration options
5. **Maintainability**: Clean, modular, and extensible code

### 📊 Expected Outcomes

#### Before Implementation:
- **Data Completeness**: ~25% (only titles and URLs)
- **Event Details**: Missing dates, locations, organizers
- **Data Quality**: Poor, with many null values

#### After Implementation:
- **Data Completeness**: ~95% (all available fields)
- **Event Details**: Complete temporal, location, and metadata
- **Data Quality**: High, with comprehensive validation
