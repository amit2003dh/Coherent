# Job Market Intelligence Pipeline

## 🎯 The Challenge

In today's competitive job market, companies struggle with getting timely insights about salary trends, skill demands, and hiring patterns. Manual research takes hours and becomes outdated quickly, making it hard to:

- **Stay competitive** with salary offers
- **Plan hiring strategies** based on real data
- **Identify skill gaps** in the market
- **Make data-driven compensation decisions**

## 💡 Our Solution

We built an intelligent job market intelligence system that automatically gathers, processes, and analyzes job posting data to give you actionable insights. Here's how it works:

**🔄 Automated Data Pipeline**
- Continuously scrapes job postings from Indeed.com
- Handles pagination and respects rate limits
- Cleans and standardizes messy data automatically
- Stores everything in a clean, searchable database

**📊 Smart Analytics**
- Real-time salary trend analysis
- Skill demand tracking across industries
- Company hiring patterns
- Geographic job distribution insights

**🎛 Interactive Dashboard**
- Beautiful, easy-to-use interface
- Filter by company, location, salary range, or skills
- Visual charts and detailed job information
- Export capabilities for deeper analysis

## 🚀 What Makes This Special

**Always Fresh Data**: Our pipeline runs automatically, so you're always looking at the latest market information, not weeks-old data.

**Smart Filtering**: Unlike other tools, our filters work together - combine company, location, salary, and skills to find exactly what you need.

**Actionable Insights**: We don't just show data - we highlight trends, patterns, and opportunities you might miss.

**Developer Friendly**: Clean code, well-documented API, and easy customization for your specific needs.

## Features

- **Automated Scraping**: Collects job postings with pagination handling and error recovery
- **Data Cleaning**: Standardizes formats, handles missing values, extracts skills
- **Database Storage**: Persistent storage with SQLite (default) or PostgreSQL
- **RESTful API**: FastAPI backend with filtering and analytics endpoints
- **Interactive Dashboard**: Streamlit frontend with visualizations
- **Scheduled Updates**: Automated pipeline execution (via GitHub Actions or cron)

## Architecture

```
┌─────────────┐
│   Data      │
│   Source    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Scraper    │ ← requests/BS4, pagination, error handling
│  Module     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Raw Data   │ ← JSON export
│  Storage    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Cleaning   │ ← pandas, standardization, validation
│  Module     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ ← SQLite/PostgreSQL
│  (Clean)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   API       │ ← FastAPI endpoints
│  Layer      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Frontend   │ ← Streamlit dashboard
│  Interface  │
└─────────────┘
```

## Tech Stack

- **Language**: Python 3.9+
- **Scraping**: requests, BeautifulSoup4
- **Data Processing**: pandas, numpy
- **Database**: SQLAlchemy, SQLite/PostgreSQL
- **API**: FastAPI, Uvicorn
- **Frontend**: Streamlit, Plotly
- **Scheduling**: APScheduler / GitHub Actions

## 🛠️ Quick Start

### Prerequisites
- **Python 3.9+** - Modern Python version
- **pip** - Python's package manager
- **Git** - For version control

### Setup in 5 Minutes

1. **Clone & Navigate**
```bash
git clone <repository-url>
cd Coherent
```

2. **Create Virtual Environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Your Environment**
```bash
cp .env.example .env
# Edit .env with your settings (database URL, API keys, etc.)
```

5. **Setup Data Storage**
```bash
mkdir -p data/raw data/processed
```

6. **Initialize Database**
```bash
python -m src.database
```

## 🚀 Getting Started

### One-Command Pipeline Run
```bash
# Run everything end-to-end
python -c "from src.scheduler import run_pipeline; run_pipeline(enrich_with_ai=False)"
```

### Running the Services

#### 🚀 Start API Server
```bash
uvicorn src.api:app --reload
```
**API Available**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs

#### 📊 Start Dashboard
```bash
streamlit run frontend/app.py
```
**Dashboard Available**: http://localhost:8501

### Manual Step-by-Step

1. **Run the scraper** (collects raw data)
```bash
python -m src.scraper
```

2. **Clean the data** (processes raw data)
```bash
python -m src.cleaner
```

3. **Load into database** (stores cleaned data)
```bash
python -m src.database
```

### Running the API

```bash
uvicorn src.api:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

### Running the Dashboard

```bash

The dashboard will be available at `http://localhost:8501`

## 📡 API Endpoints

### Job Data
- `GET /api/jobs` - List all jobs with smart filters
  - **Filters**: `limit`, `company`, `location`, `min_salary`, `max_salary`, `skill`
  - **Returns**: Paginated job listings with full details
- `GET /api/jobs/{id}` - Get specific job by ID
  - **Returns**: Complete job information including skills and description

### 📊 Analytics & Insights
- `GET /api/stats/salary` - Salary distribution and trends
  - **Returns**: Min/max/average salaries by location and company
- `GET /api/stats/skills` - Most in-demand skills
  - **Returns**: Skill frequency and demand analysis
- `GET /api/stats/companies` - Top hiring companies
  - **Returns**: Company job counts and salary ranges
- `GET /api/stats/locations` - Job hotspots by location
  - **Returns**: Geographic distribution and opportunities
- `GET /api/stats/summary` - Database overview
  - **Returns**: Total jobs, companies, locations, and market health

## ⚙️ Configuration

### Quick Setup
```bash
# Copy the template and edit your settings
cp .env.example .env

# Database (choose one)
DATABASE_URL=sqlite:///./data/jobs.db
# Or for PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/jobdb

# API Server
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Data Source (customize your job search)
BASE_URL=https://indeed.com/jobs?q=software+developer
MAX_PAGES=10
```

### All Available Settings
```bash
# Scraper Controls
SCRAPER_DELAY_SECONDS=3      # Delay between requests
MAX_RETRIES=3              # Retry attempts
REQUEST_TIMEOUT=30             # Request timeout
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Advanced Options
DEBUG_MODE=false              # Enable debug logging
ENABLE_AI_ENRICHMENT=true    # Use AI for skill analysis
EXPORT_FORMAT=json             # Data export format
```

## Data Cleaning Decisions

### Missing Values
- **Title/Company**: Filled with "Unknown" to maintain record count
- **Location**: Set to `None` (not critical for all use cases)
- **Salary**: Set to `None` (cannot impute accurately)
- **Skills**: Empty list if not found in description

### Standardization
- **Dates**: Converted to ISO 8601 format (YYYY-MM-DD)
- **Salary**: Extracted numeric values, separated min/max, detected currency
- **Location**: Trimmed whitespace, normalized spacing
- **Skills**: Extracted from description using keyword matching, lowercase

### Deduplication
- Records with duplicate URLs are removed during cleaning
- Database has unique constraint on URL field

## Customization

### Adding New Data Sources

1. Update `src/scraper.py`:
   - Modify `BASE_URL` in `.env`
   - Update CSS selectors in `_extract_job_from_card()`
   - Adjust pagination logic in `has_next_page()`

2. Update `src/cleaner.py`:
   - Modify field extraction logic if needed
   - Add new skill keywords to `extract_skills()`

### Using PostgreSQL

1. Install PostgreSQL
2. Create database: `createdb jobdb`
3. Update `.env`: `DATABASE_URL=postgresql://user:password@localhost:5432/jobdb`
4. Reinstall with: `pip install psycopg2-binary`

## Deployment

### 🏠 Local Development (Easiest)
```bash
# Start API
uvicorn src.api:app --reload

# Start Dashboard (new terminal)
streamlit run frontend/app.py
```

### 🐳 Docker (Recommended for Production)
```bash
# One command to start everything
docker-compose up
```
**Benefits**: Isolated environment, consistent setup, easy deployment

### ☁️ Cloud Deployment (Render.com)
1. **Create Account**: Sign up at [render.com](https://render.com)
2. **Connect Repository**: Link your GitHub repository
3. **Create Web Services**: 
   - API service (FastAPI backend)
   - Dashboard service (Streamlit frontend)
4. **Add Database**: PostgreSQL add-on for persistence
5. **Configure Environment**: Set all variables in Render dashboard

### 🤖 GitHub Actions (Automated)
```yaml
# Automatic daily scraping
name: Daily Job Scraping
name: Scrape Jobs

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m src.scraper
      - run: python -m src.cleaner
      - run: python -m src.database
```

## Project Structure

```
Coherent/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── scraper.py         # Web scraping logic
│   ├── cleaner.py         # Data cleaning pipeline
│   ├── database.py        # Database operations
│   └── api.py             # FastAPI endpoints
├── frontend/
│   └── app.py             # Streamlit dashboard
├── data/
│   ├── raw/               # Raw scraped data (JSON)
│   └── processed/         # Cleaned data (JSON/CSV)
├── tests/                 # Unit tests (optional)
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Actual environment variables (not committed)
├── docker-compose.yml    # Docker configuration (optional)
└── README.md            # This file
```

## 🛠️ Troubleshooting Guide

### 🕷️ Common Issues & Quick Fixes

#### Pipeline Not Running?
```bash
# Check if Python modules are accessible
python -c "from src.scheduler import run_pipeline; print('✅ Pipeline accessible')"

# Run with debug mode
python -c "from src.scheduler import run_pipeline; run_pipeline(enrich_with_ai=False, debug=True)"
```

#### 🕷️ Scraper Problems?
- **Rate Limited**: Increase `SCRAPER_DELAY_SECONDS=5` in `.env`
- **No Jobs Found**: Check `BASE_URL` - try different job search terms
- **Connection Timeout**: Set `REQUEST_TIMEOUT=60` and retry more times

#### 🗄️ Database Issues?
```bash
# Test database connection
python -c "from src.database.models import DatabaseManager; db = DatabaseManager(); print('✅ DB connected')"

# Reset if locked
python -c "from src.database.models import DatabaseManager; db = DatabaseManager(); db.create_tables(); print('✅ Tables created')"
```

#### 🌐 API Not Starting?
```bash
# Check if port is available
netstat -an | findstr :8000

# Test API directly
curl http://localhost:8000/api/stats/summary
```

#### 📊 Dashboard Empty?
```bash
# Verify API is accessible from dashboard
curl http://localhost:8000/api/jobs?limit=1

# Check dashboard configuration
echo "API_BASE_URL=http://localhost:8000" >> .env
```

## 🆘 Need Help?

### 📧 Debug Mode
Enable detailed logging by setting `DEBUG_MODE=true` in `.env`

### 📝 Logs Location
- **Pipeline**: `pipeline_error.log` (if errors occur)
- **API**: Check console output where API is running
- **Dashboard**: Check browser console for JavaScript errors

### 🐛 Report Issues
Found a bug? Please open an issue on GitHub with:
- Error messages or logs
- Steps to reproduce
- Expected vs actual behavior
- Your environment details (OS, Python version, etc.)

## 🚀 What's Next

### 🎯 Immediate Goals
- [ ] **LinkedIn Integration** - Expand to LinkedIn job postings
- [ ] **Skill Trends** - Track skill demand over time
- [ ] **Salary Predictor** - ML model for salary estimation
- [ ] **Email Alerts** - Notify users of matching jobs

### 🌟 Advanced Features
- [ ] **User Profiles** - Save searches and preferences
- [ ] **Mobile App** - Responsive dashboard for phones/tablets
- [ ] **Company Insights** - Deep dive into hiring patterns
- [ ] **Market Reports** - PDF/Excel export functionality

### 💡 Community Contributions
- [ ] **New Data Sources** - Glassdoor, AngelList, Monster integration
- [ ] **AI Enhancements** - Better skill extraction, job matching algorithms
- [ ] **Performance** - Caching, background processing, faster API

## 🎓 License

**MIT License** - Use this project for learning, commercial, or open-source contributions!

## 🤝 Get in Touch

**Questions? Issues? Ideas?** 
- Open an issue on GitHub for bugs and feature requests
- Check our [Wiki](./docs/) for detailed guides
- Join our discussions for community support

---

*Built with ❤️ for the job market community*

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Contact

For questions or issues, please open an issue on GitHub.
