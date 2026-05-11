# Architecture Documentation

## System Overview

The Job Market Intelligence System is a comprehensive data pipeline that scrapes, cleans, stores, and serves job market data through a dynamic API and dashboard.

## Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   Data Pipeline   │───▶│   Database      │
│ (GitHub Actions)│    │ (Python Modules) │    │ (PostgreSQL)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                          │
                                ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Raw Data       │    │   API Server    │
                       │   (JSON/CSV)     │◀───│   (FastAPI)     │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Dashboard     │
                                               │  (Streamlit)    │
                                               └─────────────────┘
```

## Component Breakdown

### 1. Data Source Layer
- **Source**: LinkedIn Jobs (configurable via BASE_URL)
- **Method**: Web scraping with fallback to realistic sample data
- **Frequency**: Daily automated runs

### 2. Scraper Layer (`src/scraper/`)
- **fetcher.py**: HTTP requests and pagination logic
- **parser.py**: HTML/JSON parsing and data extraction
- **Features**:
  - Rate limiting and respectful scraping
  - Error handling with retries
  - Pagination support
  - Sample data generation for demonstration

### 3. Cleaning Layer (`src/cleaning/`)
- **transform.py**: Data cleaning and standardization using pandas
- **Features**:
  - Duplicate removal
  - Missing value handling
  - Text standardization
  - Salary validation
  - Skill extraction
  - Data validation rules

### 4. Database Layer (`src/database/`)
- **models.py**: SQLAlchemy ORM models and schema
- **loader.py**: Database operations and upsert logic
- **Features**:
  - PostgreSQL with SQLAlchemy ORM
  - Upsert operations to prevent duplicates
  - Timestamp tracking (scraped_at, last_updated_at)
  - Indexes for performance

### 5. API Layer (`src/api/`)
- **main.py**: FastAPI application with endpoints
- **Features**:
  - RESTful API design
  - Query parameters and filtering
  - Analytics endpoints
  - Auto-generated documentation
  - CORS support

### 6. AI/ML Layer (`src/ai/`)
- **enrich.py**: Data enrichment and insights
- **Features**:
  - Job level classification
  - Experience extraction
  - Urgency assessment
  - Market insights generation

### 7. Scheduler (`src/scheduler.py`)
- **Pipeline orchestration**
- **Error handling and logging**
- **AI/ML enrichment toggle**

## Data Flow

1. **Scraping**: Fetcher retrieves raw HTML/JSON data
2. **Parsing**: Parser extracts structured job information
3. **Cleaning**: Transformer standardizes and validates data
4. **Enrichment** (optional): AI layer adds insights
5. **Storage**: Loader upserts data to PostgreSQL
6. **Serving**: API provides filtered access
7. **Visualization**: Dashboard displays analytics

## Technology Stack

- **Runtime**: Python 3.10+
- **Web Scraping**: requests, BeautifulSoup4
- **Data Processing**: pandas, numpy
- **Database**: PostgreSQL with SQLAlchemy
- **API**: FastAPI
- **Frontend**: Streamlit
- **Testing**: pytest
- **Automation**: GitHub Actions
- **Deployment**: Docker, Render/Railway

## Configuration

All configuration is managed through environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `BASE_URL`: Source website URL
- `SEARCH_QUERY`: Job search terms
- `LOCATION`: Geographic filter
- `MAX_PAGES`: Pagination limit

## Error Handling Strategy

- **Network Errors**: Exponential backoff retries
- **Parsing Errors**: Graceful fallbacks, logging
- **Database Errors**: Transaction rollback, retry logic
- **Data Validation**: Skip invalid records, log warnings

## Performance Considerations

- **Database Indexes**: On title, company, location
- **Pagination**: Limit/offset for large datasets
- **Caching**: API response caching (5-minute TTL)
- **Rate Limiting**: Respectful scraping delays

## Security Measures

- **Environment Variables**: No hardcoded secrets
- **SQL Injection**: SQLAlchemy ORM protection
- **CORS**: Configurable origins
- **Input Validation**: Pydantic models in FastAPI

## Monitoring & Logging

- **Structured Logging**: JSON format with timestamps
- **Pipeline Metrics**: Jobs collected, cleaned, stored
- **Error Tracking**: Detailed error messages
- **Health Checks**: API and database connectivity

## Scalability Design

- **Horizontal Scaling**: Stateless API design
- **Database Scaling**: Connection pooling
- **Async Processing**: Future support for async scraping
- **Microservices**: Modular component design
