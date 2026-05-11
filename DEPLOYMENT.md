# Deployment Guide

This document provides detailed instructions for deploying the Job Market Intelligence Pipeline.

## Option 1: Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup
```bash
# Clone repository
git clone <repo-url>
cd Coherent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Create data directories
mkdir -p data/raw data/processed

# Run the full pipeline
python run_pipeline.py

# Start API server
uvicorn src.api:app --reload

# In another terminal, start dashboard
streamlit run frontend/app.py
```

## Option 2: Docker (Recommended for Production)

### Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Services
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432

### Manual Docker Build

```bash
# Build image
docker build -t job-market-intel .

# Run API
docker run -p 8000:8000 --env-file .env job-market-intel

# Run Dashboard
docker run -p 8501:8501 --env API_BASE_URL=http://localhost:8000 job-market-intel streamlit run frontend/app.py --server.port=8501
```

## Option 3: Render.com (Free Tier)

### Prerequisites
- Render account (free)
- GitHub repository

### Steps

1. **Prepare Repository**
   - Push code to GitHub
   - Ensure `.env` is NOT committed (use `.env.example`)
   - Add `DATABASE_URL` to Render environment variables

2. **Create PostgreSQL Database**
   - Go to Render dashboard
   - Create new "PostgreSQL" database
   - Note the connection string (Internal Database URL)

3. **Deploy API**
   - Create new "Web Service"
   - Connect GitHub repository
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn src.api:app --host 0.0.0.0 --port $PORT`
   - Add environment variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `SCRAPER_DELAY_SECONDS`: 3
     - `MAX_RETRIES`: 3
     - `API_HOST`: 0.0.0.0
     - `API_PORT`: $PORT (Render provides this)

4. **Deploy Dashboard**
   - Create another "Web Service"
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0`
   - Add environment variable:
     - `API_BASE_URL`: Your API service URL (e.g., https://your-api.onrender.com)

5. **Schedule Pipeline (Optional)**
   - Create "Cron Job" service
   - Command: `python run_pipeline.py`
   - Schedule: `0 0 * * *` (daily at midnight)
   - Add same environment variables as API

## Option 4: Railway.app

### Steps

1. **Create Project**
   - Sign up at railway.app
   - Create new project from GitHub

2. **Add Services**
   - Add PostgreSQL service
   - Add Python service (API)
   - Add Python service (Dashboard)

3. **Configure Environment Variables**
   - In each service, add required env vars
   - Link DATABASE_URL to PostgreSQL service

4. **Deploy**
   - Railway auto-deploys on push
   - Access via provided URLs

## Option 5: VPS (DigitalOcean, AWS, etc.)

### Prerequisites
- Ubuntu server (or other Linux)
- Domain name (optional)
- SSL certificate (optional)

### Setup Script

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git nginx -y

# Clone repository
git clone <repo-url>
cd Coherent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Create data directories
mkdir -p data/raw data/processed

# Install Gunicorn for production
pip install gunicorn

# Create systemd service for API
sudo nano /etc/systemd/system/job-api.service
```

**Systemd Service File:**
```ini
[Unit]
Description=Job Market Intelligence API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/Coherent
Environment="PATH=/path/to/Coherent/venv/bin"
ExecStart=/path/to/Coherent/venv/bin/gunicorn src.api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable job-api
sudo systemctl start job-api

# Setup Nginx reverse proxy
sudo nano /etc/nginx/sites-available/job-api
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/job-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot (optional)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

### Required
- `DATABASE_URL`: Database connection string
- `BASE_URL`: Target website for scraping

### Optional (with defaults)
- `SCRAPER_DELAY_SECONDS`: 3
- `MAX_RETRIES`: 3
- `REQUEST_TIMEOUT`: 30
- `USER_AGENT`: Mozilla/5.0...
- `API_HOST`: 0.0.0.0
- `API_PORT`: 8000
- `LOG_LEVEL`: INFO
- `MAX_PAGES`: 10

## Monitoring

### Health Checks

**API Health:**
```bash
curl http://your-api-url/
```

**Database Stats:**
```bash
curl http://your-api-url/api/stats/summary
```

### Logs

**Docker:**
```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

**Systemd:**
```bash
sudo journalctl -u job-api -f
```

**Render/Railway:**
- Check dashboard logs tab

## Scaling

### Horizontal Scaling (API)
- Use load balancer (Nginx, HAProxy)
- Run multiple API instances
- Use shared PostgreSQL database

### Database Scaling
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Enable read replicas for dashboard queries
- Consider connection pooling (PgBouncer)

## Backup

### Database Backup
```bash
# PostgreSQL
pg_dump -U username -h localhost jobdb > backup.sql

# Restore
psql -U username -h localhost jobdb < backup.sql
```

### SQLite Backup
```bash
cp data/jobs.db data/jobs.db.backup
```

### Automated Backup (Cron)
```bash
# Add to crontab
0 2 * * * pg_dump -U username jobdb > /backups/jobdb_$(date +\%Y\%m\%d).sql
```

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Database connection refused:**
- Check DATABASE_URL format
- Verify database is running
- Check firewall rules

**Out of memory:**
- Reduce MAX_PAGES in scraper
- Increase server RAM
- Use database pagination

## Security

### Best Practices
- Never commit `.env` file
- Use strong database passwords
- Enable HTTPS in production
- Implement rate limiting on API
- Use environment-specific configs
- Regular security updates

### API Authentication (Optional)
```python
# Add to src/api.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != os.getenv("API_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials

# Protect endpoints
@app.get("/api/jobs", dependencies=[Depends(verify_token)])
```

## Cost Estimate

### Free Options
- Render: $0 (with limitations)
- Railway: $5 free credit
- Local: $0

### Paid Options
- DigitalOcean: $5-20/month
- AWS: $20-50/month
- Render: $7-25/month

## Support

For deployment issues:
1. Check logs
2. Verify environment variables
3. Test components individually
4. Consult documentation
5. Open GitHub issue
