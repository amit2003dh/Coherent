import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8007")

st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Market Intelligence Dashboard")
st.markdown("---")

# Refresh and New Data buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.success("Cache cleared! Fetching latest data...")
        st.rerun()

with col2:
    if st.button("Get New Data"):
        with st.spinner("Running pipeline to fetch new data..."):
            try:
                # Run the pipeline to get fresh data
                import subprocess
                import sys
                
                result = subprocess.run(
                    [sys.executable, "run_pipeline.py", "--enrich"],
                    capture_output=True,
                    text=True,
                    cwd="c:/Users/dell/Documents/Projects/Coherent"
                )
                
                if result.returncode == 0:
                    st.success("✅ New data fetched successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Pipeline failed: {result.stderr}")
                    
            except Exception as e:
                st.error(f"❌ Error running pipeline: {e}")

# Sidebar filters
st.sidebar.header("Filters")

company_filter = st.sidebar.text_input("Company", "", key="company_filter")
location_filter = st.sidebar.text_input("Location", "", key="location_filter")
min_salary = st.sidebar.number_input("Min Salary", min_value=0, value=0, step=100000, key="min_salary")
max_salary = st.sidebar.number_input("Max Salary", min_value=0, value=10000000, step=100000, key="max_salary")
skill_filter = st.sidebar.text_input("Skill", "", key="skill_filter")
limit = st.sidebar.slider("Results Limit", 10, 500, 100, key="limit")

# Fetch data
def fetch_jobs(_limit=None, _company_filter=None, _location_filter=None, _min_salary=None, _max_salary=None, _skill_filter=None):
    try:
        # Build query parameters
        params = {
            "limit": limit if _limit is not None else 100,
        }
        if _company_filter:
            params["company"] = _company_filter
        if _location_filter:
            params["location"] = _location_filter
        if _min_salary and _min_salary > 0:
            params["min_salary"] = _min_salary
        if _max_salary and _max_salary > 0:
            params["max_salary"] = _max_salary
        if _skill_filter:
            params["skill"] = _skill_filter

        response = requests.get(f"{API_BASE_URL}/jobs", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            return jobs
        else:
            st.error(f"Error fetching jobs: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

@st.cache_data(ttl=60)  # Reduced to 1 minute
def fetch_salary_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/salary")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@st.cache_data(ttl=300)
def fetch_top_skills(limit=20):
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/skills", params={"limit": limit})
        if response.status_code == 200:
            data = response.json()
            return data.get("top_skills", [])
        return []
    except Exception:
        return []


@st.cache_data(ttl=300)
def fetch_summary():
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# Main content
col1, col2, col3 = st.columns(3)

# Get database statistics for total jobs
summary = fetch_summary()
total_jobs_db = summary.get("total_jobs", 0) if summary else 0

# Get filtered jobs for metrics calculation
jobs = fetch_jobs(limit, company_filter, location_filter, min_salary, max_salary, skill_filter)
jobs_with_salary = 0
jobs_with_skills = 0

if jobs:
    df = pd.DataFrame(jobs)
    total_jobs_filtered = len(df)
    
    # Jobs with salary (has either min or max salary)
    jobs_with_salary = len(df[df['salary_min'].notna() | df['salary_max'].notna()])
    
    # Jobs with skills (has non-empty skills string or valid list)
    def has_skills(skills):
        if pd.isna(skills) or skills == '' or skills == '[]':
            return False
        if isinstance(skills, str):
            cleaned = skills.replace('{', '').replace('}', '').replace('"', '').replace('[', '').replace(']', '')
            return len(cleaned.strip()) > 0 and cleaned.strip() != ','
        elif isinstance(skills, list):
            return len(skills) > 0
        return False
    
    jobs_with_skills = sum(df['skills'].apply(has_skills))
    
    # Debug info (commented out)
    # st.write(f"DEBUG: Filter params - company: {company_filter}, location: {location_filter}, min_salary: {min_salary}, max_salary: {max_salary}, skill: {skill_filter}")
    # st.write(f"DEBUG: Fetched {len(jobs)} jobs")
    # st.write(f"DEBUG: Jobs with salary: {jobs_with_salary}")
    # st.write(f"DEBUG: Jobs with skills: {jobs_with_skills}")
else:
    total_jobs_filtered = 0

# Show database total for Total Jobs, filtered for others
col1.metric("Total Jobs", total_jobs_db)
# col2.metric("Jobs with Salary", jobs_with_salary)
col2.metric("Jobs with Skills", jobs_with_skills)

st.caption(f"Showing {total_jobs_filtered} filtered jobs from {total_jobs_db} total")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Job Listings", "Salary Analytics", "Skills & Companies", "Locations"])

with tab1:
    st.header("Job Listings")
    jobs = fetch_jobs(limit, company_filter, location_filter, min_salary, max_salary, skill_filter)
    
    if jobs:
        df = pd.DataFrame(jobs)
        
        # Display as table
        st.dataframe(
            df[["title", "company", "location", "salary_min", "salary_max", "skills"]],
            use_container_width=True
        )
        
        # Job details expander
        st.subheader("Job Details")
        for job in jobs[:10]:  # Show details for first 10 jobs
            with st.expander(f"{job['title']} at {job['company']}"):
                st.write(f"**Location:** {job.get('location', 'N/A')}")
                st.write(f"**Salary Range:** ${job.get('salary_min', 0):,.0f} - ${job.get('salary_max', 0):,.0f}")
                st.write(f"**Skills:** {', '.join(job.get('skills', []))}")
                st.write(f"**Posted:** {job.get('posted_date', 'N/A')}")
                if job.get('url'):
                    st.write(f"**URL:** {job['url']}")
                if job.get('description'):
                    st.write(f"**Description:** {job['description']}")
    else:
        st.warning("No jobs found. Try adjusting filters or ensure the API is running.")

with tab2:
    st.header("Salary Analytics")
    salary_stats = fetch_salary_stats()
    
    if salary_stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Salary Statistics")
            st.metric("Average Min Salary", f"${salary_stats.get('avg_salary_min', 0):,.0f}")
            st.metric("Average Max Salary", f"${salary_stats.get('avg_salary_max', 0):,.0f}")
            st.metric("Max Salary Offered", f"${salary_stats.get('max_salary_max', 0):,.0f}")
        
        with col2:
            st.subheader("Salary Range Distribution")
            jobs = fetch_jobs()
            if jobs:
                df = pd.DataFrame(jobs)
                df_with_salary = df[df['salary_min'].notna()]
                
                if not df_with_salary.empty:
                    fig = px.histogram(
                        df_with_salary,
                        x='salary_min',
                        nbins=30,
                        title="Distribution of Minimum Salaries",
                        labels={'salary_min': 'Salary ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No salary data available.")

with tab3:
    st.header("Skills & Companies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Skills in Demand")
        top_skills = fetch_top_skills(15)
        if top_skills:
            skills_df = pd.DataFrame(top_skills)
            fig = px.bar(
                skills_df,
                x='count',
                y='skill',
                orientation='h',
                title="Top 15 Skills",
                labels={'count': 'Number of Jobs', 'skill': 'Skill'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No skills data available.")
    
    with col2:
        st.subheader("Top Companies Hiring")
        # Get companies from filtered jobs
        jobs = fetch_jobs(limit, company_filter, location_filter, min_salary, max_salary, skill_filter)
        if jobs:
            df = pd.DataFrame(jobs)
            if 'company' in df.columns:
                company_counts = df['company'].value_counts().head(15)
                companies_df = pd.DataFrame({'company': company_counts.index, 'count': company_counts.values})
                fig = px.bar(
                    companies_df,
                    x='count',
                    y='company',
                    orientation='h',
                    title="Top 15 Companies by Job Postings",
                    labels={'count': 'Number of Jobs', 'company': 'Company'}
                )
                fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No company data available.")
        else:
            st.warning("No jobs data available.")

with tab4:
    st.header("Locations")
    st.subheader("Top Locations by Job Postings")
    # Get locations from filtered jobs
    jobs = fetch_jobs(limit, company_filter, location_filter, min_salary, max_salary, skill_filter)
    
    if jobs:
        df = pd.DataFrame(jobs)
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(15)
            locations_df = pd.DataFrame({'location': location_counts.index, 'count': location_counts.values})
            fig = px.bar(
                locations_df,
                x='count',
                y='location',
                orientation='h',
                title="Top 15 Locations",
                labels={'count': 'Number of Jobs', 'location': 'Location'}
            )
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No location data available.")
    else:
        st.warning("No jobs data available.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Click 'Get New Data' to fetch the latest job market data in real-time!")
