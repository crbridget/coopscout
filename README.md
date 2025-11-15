# CoopScout

Automated web scraper for Northeastern University's NUworks co-op job portal. Saves you time by automatically collecting job postings, filtering by your criteria, and exporting clean data for analysis.

## Description

CoopScout streamlines the co-op search process by:
- Automating login through Northeastern SSO and Duo 2FA
- Searching and filtering jobs by keyword, location, and position type
- Scraping comprehensive details: title, company, compensation, deadlines, requirements, and descriptions
- Exporting structured data to JSON for easy review and comparison

Built by a Northeastern Data Science student to make co-op hunting less tedious.

## Installation

**Prerequisites:**
- Python 3.x
- Chrome browser
- Valid Northeastern credentials with NUworks access
- Duo Mobile app

**Steps:**

1. Clone this repository
```bash
git clone https://github.com/yourusername/coopscout.git
cd coopscout
```

2. Install required packages
```bash
pip install selenium python-dotenv pandas
```

3. Create a `.env` file in the project root:
```
USERNAME=your_northeastern_username
PASSWORD=your_northeastern_password
```

4. (Optional) Update search parameters in `main.py`:
```python
SEARCH = "software engineering"  # Change to your target role
LOCATION = "Boston, MA, USA"     # Change to your preferred location
```

## Usage

Run the scraper:
```bash
python main.py
```

**What happens:**
1. Browser opens and navigates to NUworks
2. Logs in with your credentials
3. **Sends Duo push - approve on your phone within 60 seconds**
4. Searches for jobs matching your criteria
5. Filters for co-op positions at your location
6. Scrapes all qualified job postings
7. Saves results to `coopsearch.json`

**Example output** (`coopsearch.json`):
```json
[
  {
    "title": "Software Engineer Co-op",
    "company": "Geotab",
    "location": "Boston, MA",
    "deadline": "November 30, 2025",
    "compensation": "$25-30/hour",
    "targeted major": "Computer Science, Data Science",
    "minimum GPA": "3.0",
    "description": "Full job description text..."
  }
]
```

## Support

**Common Issues:**

- **Duo timeout:** Approve the push within 60 seconds. If you miss it, restart the script.
- **Login fails:** Double-check credentials in `.env` file
- **Element not found:** NUworks may have updated their UI. Check CSS selectors in the code or wait for updates.
- **Slow loading:** Increase `time.sleep()` values if your internet connection is slow

For bugs or questions, open an issue on GitHub.

## Roadmap

Future improvements:
- Headless mode for background execution
- Email notifications for new job matches
- Support for multiple search queries in one run
- Filtering by work authorization requirements

## Contributing

This is a personal project for Northeastern students. If you have suggestions or want to contribute:
1. Fork the repo
2. Create a feature branch
3. Submit a pull request

## Authors

Built by Bridget Crampton, Northeastern Data Science '27

## License

MIT License

## Project Status

Active development - works with current NUworks interface as of November 2025. If NUworks updates their website, selectors may need adjustment.

---

⚠️ **Important:** This tool is for personal use only. Respect Northeastern's terms of service. Never share your `.env` file or commit it to version control.
