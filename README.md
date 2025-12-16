# CoopScout

Automated web scraper and job tracking platform for Northeastern University's NUworks co-op portal. Saves you time by automatically collecting job postings, filtering by your criteria, and providing a modern web interface to browse and manage opportunities.

## Description

CoopScout streamlines the co-op search process by:
- Automating login through Northeastern SSO and Duo 2FA
- Searching and filtering jobs by keyword, location, and position type
- Scraping comprehensive details: title, company, compensation, deadlines, requirements, and descriptions
- Storing data in Supabase for persistent access
- Providing a modern React frontend for browsing jobs

Built by Northeastern students to make co-op hunting less tedious.

## Architecture

```
coopscout/
├── scraper/              # Core scraping logic
│   ├── scraper.py       # Reusable NUworks scraper
│   ├── save_cookies.py  # Cookie management
│   ├── automated_scraper.py
│   └── .env             # Scraper credentials
├── backend/
│   ├── api/
│   │   └── app.py       # Flask REST API
│   ├── .env             # Database credentials
│   ├── seed_database.py # One-time database upload
│   └── cookies.pkl      # Saved login cookies
├── frontend/            # React + Vite web app
│   ├── src/
│   └── package.json
└── .gitignore
```

## Tech Stack

**Backend:**
- Python 3.10+
- Selenium (web scraping)
- Flask (REST API)
- Supabase (database)
- Flask-CORS (API access)

**Frontend:**
- React 18
- Vite
- Axios (API calls)
- Modern CSS

## Installation

### Prerequisites
- Python 3.10+
- Node.js 16+
- Chrome browser
- Valid Northeastern credentials with NUworks access
- Duo Mobile app
- Supabase account (free tier works)

### Backend Setup

1. **Clone this repository**
```bash
git clone https://github.com/yourusername/coopscout.git
cd coopscout
```

2. **Install Python dependencies**
```bash
pip install selenium python-dotenv pandas flask flask-cors supabase
```

3. **Set up environment variables**

Create `backend/.env`:
```
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
```

Create `scraper/.env`:
```
USERNAME=your_northeastern_username
PASSWORD=your_northeastern_password
```

4. **Set up Supabase database**
   
   a. Create a project at [supabase.com](https://supabase.com)
   
   b. Run this SQL in the SQL Editor:
```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    deadline TEXT,
    compensation TEXT,
    targeted_major TEXT,
    minimum_gpa TEXT,
    description TEXT,
    scraped_at TEXT,
    search_keywords TEXT,
    search_location TEXT,
    user_id TEXT
);
```

   c. Disable Row Level Security (for development):
   - Go to Table Editor → jobs table → Settings → Disable RLS

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Create environment file**

Create `frontend/.env`:
```
VITE_API_URL=http://localhost:5000
```

### .gitignore Setup

Make sure your `.gitignore` includes:
```
# Environment and secrets
.env
*.pkl

# Python
__pycache__/
venv/
*.pyc

# Data files
*.json
errors.txt
scrape_history.json

# Frontend
node_modules/
dist/
.vite/

# OS
.DS_Store
```

## Usage

### Web Application

**Step 1: Scrape initial data**
```bash
cd scraper
python scraper.py
```
- Browser opens → log in → approve Duo push
- Jobs are scraped and uploaded to Supabase automatically
- This populates your database with jobs

**Step 2: Start the backend API**
```bash
cd backend/api
python app.py
```
API runs at `http://localhost:5000`

**Step 3: Start the frontend**
```bash
cd frontend
npm run dev
```
Frontend runs at `http://localhost:5173`

**Step 4: Browse jobs**
- Open `http://localhost:5173` in your browser
- Search, filter, and view job listings

### Automated Scraping with Cookies

To avoid repeated Duo prompts, save your cookies once:

**Step 1: Save cookies**
```bash
cd scraper
python save_cookies.py
```
- Browser opens → log in → approve Duo → press Enter
- Cookies saved to `cookies_admin.pkl`

**Step 2: Use cookies for scraping**

Modify `automated_scraper.py` to use cookies:
```python
from scraper import scrape_with_cookies
import pickle

# Load saved cookies
cookies = pickle.load(open("cookies_admin.pkl", "rb"))

# Scrape without Duo
jobs = scrape_with_cookies(
    cookies,
    search_term="software engineering",
    location="Boston, MA, USA"
)
```

**Step 3: Schedule with cron (optional)**

For daily automated scraping on Mac/Linux:
```bash
crontab -e
```

Add this line to run daily at 2 AM:
```
0 2 * * * cd /path/to/coopscout/scraper && python automated_scraper.py
```

### Command Line Scraper

For one-time manual scraping:

```bash
cd scraper
python automated_scraper.py
```

Or use the scraper directly in Python:
```python
from scraper import scrape_with_login
import os
from dotenv import load_dotenv

load_dotenv()
jobs = scrape_with_login(
    os.getenv("USERNAME"),
    os.getenv("PASSWORD"),
    search_term="data science",
    location="Boston, MA, USA",
    max_jobs=10
)
```

## API Endpoints

**Get all jobs:**
```
GET http://localhost:5000/api/v1/jobs/all
```

**Filter jobs:**
```
GET http://localhost:5000/api/v1/jobs?title=software&location=boston&company=google
```

Query parameters:
- `title` - Filter by job title
- `location` - Filter by location
- `company` - Filter by company name

**Example response:**
```json
[
  {
    "id": 1,
    "title": "Software Engineer Co-op",
    "company": "Geotab",
    "location": "Boston, MA",
    "deadline": "November 30, 2025",
    "compensation": "$25-30/hour",
    "targeted_major": "Computer Science, Data Science",
    "minimum_gpa": "3.0",
    "description": "Full job description...",
    "scraped_at": "2024-12-15T14:30:00",
    "search_keywords": "software engineering",
    "search_location": "Boston, MA, USA"
  }
]
```

## Project Structure Details

### Scraper Module
- **scraper.py** - Core scraping class with methods for login, search, and data extraction
- **save_cookies.py** - Interactive script to save authentication cookies
- **automated_scraper.py** - Script for scheduled/automated scraping
- **profiler.py** - Performance profiling tools
- **retry.py** - Retry logic for failed operations

### Backend API
- **app.py** - Flask REST API with CORS support
- **seed_database.py** - One-time script to upload JSON data to Supabase

### Frontend
- React single-page application
- Job listing and filtering interface
- API integration for real-time data

## Features

### Current Features
✅ Automated NUworks login with Duo 2FA  
✅ Job scraping with customizable search filters  
✅ REST API for job data access  
✅ Modern web interface for browsing jobs  
✅ Cookie-based authentication (no repeated Duo prompts)  
✅ Supabase cloud database storage  
✅ Multi-page scraping support  
✅ Comprehensive job data extraction  

### Planned Features
- [ ] User authentication and personal job lists
- [ ] Job application tracking and notes
- [ ] Email notifications for new job matches
- [ ] Advanced filtering (work authorization, remote options)
- [ ] Saved search queries and alerts
- [ ] Job comparison tool
- [ ] Mobile responsive design improvements
- [ ] Export to PDF/CSV
- [ ] GitHub Actions for cloud-based automated scraping

## Development

**Running in development mode:**

Backend with debug mode:
```bash
cd backend/api
python app.py
```

Frontend with hot reload:
```bash
cd frontend
npm run dev
```

**Testing the scraper:**
```bash
cd scraper
python scraper.py  # Run with max_jobs=5 for testing
```

**Building for production:**
```bash
cd frontend
npm run build
```

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Make sure you're in the right directory
cd scraper  # for scraper scripts
cd backend/api  # for API
cd frontend  # for frontend

# Reinstall dependencies
pip install -r requirements.txt  # Python
npm install  # Frontend
```

**Duo timeout:**
- Approve the push within 60 seconds
- If you miss it, restart the script
- Consider saving cookies to avoid repeated Duo prompts

**Login fails:**
- Double-check credentials in `.env` file
- Make sure you're using your Northeastern username (not email)
- Verify Duo is set up on your account

**Element not found errors:**
- NUworks may have updated their UI
- Check if you can log in manually first
- Wait for updates to CSS selectors

**CORS errors in frontend:**
- Make sure Flask-CORS is installed: `pip install flask-cors`
- Verify backend is running on port 5000
- Check `VITE_API_URL` in frontend `.env`

**Supabase connection errors:**
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in backend `.env`
- Check if RLS is disabled on the jobs table
- Make sure your Supabase project is active

**Frontend won't start:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Cookies expired:**
- Run `python save_cookies.py` again
- Cookies typically last 30 days
- You'll know they expired when scraping fails at login

## Authors

Built by:
- **Bridget Crampton** - Data Science '28, Northeastern University
- **Olivia Hill** - Computer Science '28, Northeastern University

## License

This project is for educational and personal use only. Not affiliated with or endorsed by Northeastern University.

## Acknowledgments

- Built for the Northeastern co-op community
- Thanks to all students who provided feedback and testing
- Inspired by the need to make co-op searching less tedious

## Project Status

🟢 **Active Development** - Works with current NUworks interface as of December 2025.

If NUworks updates their website structure, CSS selectors may need adjustment. We aim to maintain compatibility and will update as needed.

---

## Important Notes

⚠️ **Please read before using:**

1. **Personal Use Only** - This tool is for individual job searching. Do not use for commercial purposes or mass data collection.

2. **Respect Terms of Service** - Use responsibly and in accordance with Northeastern's acceptable use policies.

3. **Security Best Practices:**
   - Never commit `.env` files to version control
   - Don't share your cookies or credentials
   - Keep your dependencies updated
   - Review code before running scripts from others

4. **Cookie Management:**
   - Cookies expire after ~30 days
   - Re-run `save_cookies.py` when they expire
   - Store cookies securely (they're in `.gitignore`)

5. **Rate Limiting:**
   - Don't scrape too frequently (daily is reasonable)
   - Add delays between requests
   - Be respectful of NUworks servers

6. **Maintenance:**
   - NUworks may update their interface
   - Selectors may need periodic updates
   - Check GitHub for updates if scraping fails
