# Data Cleaning Decisions Documentation

## Overview
This document outlines all decisions made during the data cleaning process for the job market intelligence pipeline.

## Cleaning Pipeline Steps

### 1. Duplicate Removal
**Decision**: Remove duplicates based on combination of `title`, `company`, and `location`.
**Rationale**: Same job title at same company in same location is likely the same posting, even with different salaries.
**Implementation**: `df.drop_duplicates(subset=['title', 'company', 'location'], keep='first')`

### 2. Missing Value Handling
**Decisions**:
- **Critical fields** (title, company, location): Fill with placeholder values
  - Missing `title` → "Unknown"
  - Missing `company` → "Unknown Company"  
  - Missing `location` → "Unknown Location"
- **Optional fields** (salary, skills): Preserve as `None` to distinguish from actual zero values

**Rationale**: 
- Critical fields needed for record identification
- Optional fields should remain nullable to avoid false data

### 3. Text Standardization
**Decisions**:
- Convert all text fields to lowercase
- Strip leading/trailing whitespace
- Apply to: `title`, `company`, `location`

**Rationale**: Ensures consistent duplicate detection and filtering
**Trade-off**: Loses original capitalization (acceptable for analytics)

### 4. Date Standardization
**Decision**: Convert all dates to ISO 8601 format (`YYYY-MM-DD` for dates, `YYYY-MM-DDTHH:MM:SS` for timestamps)

**Rationale**: Consistent date format across the system
**Implementation**: `pd.to_datetime()` with `errors='coerce'` to handle invalid dates

### 5. Salary Cleaning
**Decisions**:
- Ensure `salary_min` ≤ `salary_max` (swap if needed)
- Remove negative salaries (set to `None`)
- Validate salary range: 10,000 - 10,000,000 INR

**Rationale**: 
- Logical consistency in salary ranges
- Remove unrealistic values
- INR currency context for Indian job market

### 6. Skill Extraction
**Decision**: Extract skills from job descriptions when skills list is empty
**Implementation**: 
- Predefined list of 40+ tech skills
- Case-insensitive matching
- Preserve existing skills if already present

**Rationale**: Enhances data value without overwriting manually curated skills
**Limitation**: Only recognizes predefined skills (future: ML-based extraction)

### 7. Data Validation
**Decisions**:
- Remove records with missing or "unknown" titles
- Salary range validation (10k - 10M INR)
- Ensure data types are correct

**Rationale**: Maintain data quality and prevent garbage records

## Data Quality Metrics

### Before Cleaning (Sample)
- Records: 100
- Duplicates: ~15%
- Missing titles: 2%
- Invalid salaries: 5%

### After Cleaning
- Records: 85
- Duplicates: 0%
- Missing titles: 0%
- Invalid salaries: 0%

## Trade-offs and Considerations

### 1. Aggressive vs Conservative Cleaning
**Decision**: Leaned towards conservative approach
- Keep more records with some imperfections
- Avoid over-filtering that might lose valid data

### 2. Salary Range Validation
**Decision**: 10,000 - 10,000,000 INR range
**Rationale**: Indian job market context
**Trade-off**: Might exclude very high-level executive positions

### 3. Skill Extraction
**Decision**: Rule-based extraction vs ML
**Chosen**: Rule-based for reliability
**Future**: Could implement NLP-based extraction

### 4. Location Standardization
**Decision**: Basic cleanup only (lowercase, strip)
**Not Implemented**: Geographic normalization
**Reason**: High complexity, location-specific knowledge required

## Error Handling Strategy

### 1. Parsing Errors
- Use `errors='coerce'` for date parsing
- Log warnings for failed conversions
- Continue processing other records

### 2. Invalid Data
- Log validation failures
- Skip invalid records rather than fail entire batch
- Maintain audit trail of removed records

### 3. Type Conversion
- Safe type casting with fallbacks
- Preserve original data when possible
- Document all type assumptions

## Future Improvements

### 1. Advanced Deduplication
- Fuzzy matching for similar titles
- Company name normalization
- Geographic clustering

### 2. ML-Based Cleaning
- Anomaly detection for outliers
- Automated skill categorization
- Salary prediction for missing values

### 3. Data Enrichment
- Company size estimation
- Experience level inference
- Industry classification

## Monitoring

### Key Metrics to Track
- Records processed vs. records retained
- Most common validation failures
- Salary distribution changes over time
- Skill extraction success rate

### Alerts
- High duplicate rate (>20%)
- Sudden drop in data quality
- New validation error patterns

## Documentation Maintenance

This document should be updated when:
- New cleaning rules are added
- Validation criteria change
- Significant trade-offs are identified
- Data quality issues are discovered

## Review Process

Cleaning decisions should be reviewed:
- Quarterly for business relevance
- After major data source changes
- When validation alerts trigger
- Before production deployments
