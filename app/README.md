# Bank Rates App — [Live App](https://aurore-bank-rates.streamlit.app/)

A Streamlit-powered dashboard for exploring and analyzing key U.S. banking and market rates. Fetches data directly from the U.S. Treasury, FRED (Federal Reserve Economic Data), and other sources. Supports custom rate calculations and PDF export.

---

## Features
- 📊 **Interactive dashboard** for visualizing FRED and Treasury rates
- 🏗️ **Custom Rate Builder**: Combine and adjust base rates for custom analytics
- 📄 **PDF export** of data tables
- 🔒 **User authentication** (with visit tracking)
- 🗂️ **Session log viewing**
- 🕵️ **Scraping support** for sources without APIs (e.g., FHLB)

---

## Tech Stack & Libraries Used
- [Streamlit](https://streamlit.io/) – UI and app framework
- [pandas](https://pandas.pydata.org/) – Data analysis
- [matplotlib](https://matplotlib.org/) – Plotting
- [reportlab](https://www.reportlab.com/) – PDF generation
- [Requests](https://requests.readthedocs.io/) – HTTP requests
- [urllib3](https://urllib3.readthedocs.io/) – HTTP connection pooling
- [python-dotenv](https://pypi.org/project/python-dotenv/) – Environment variable management
- [streamlit_authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) – Authentication
- [selenium](https://selenium.dev/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) (for scraping, see `poc/scraping_test.py`)

---

## APIs & Data Sources
- **FRED API** ([stlouisfed.org](https://fred.stlouisfed.org/))  
  Used for fetching official rates (e.g., Fed Funds, Treasury CMT, SOFR, Prime Rate, etc.). Requires a FRED API key.
- **CME Group API** ([dataservices.cmegroup.com](https://dataservices.cmegroup.com/pages/CME-Data-Via-API))  
  Some CME rates require a paid license (see To-Do section).
- **FHLB**  
  No public API; rates are scraped or exported from Excel.

---

## Folder Structure
```
├── app.py                # Main Streamlit app
├── auth-app.py           # Authentication and logging
├── api/                  # (Future) API endpoints
├── utils/
│   ├── fetch_rates.py    # Fetching and caching rate data
│   └── pdf_generator.py  # PDF export utilities
├── poc/                  # Proof-of-concept scripts (e.g., scraping)
├── public/               # Static assets (e.g., logo)
├── config.yaml           # Authentication and app config
├── requirements.txt      # Python dependencies
├── TODO                  # Pending features and notes
└── usage.log             # User/session log
```

---

## Configuration
- **Environment Variables**:  
  Create a `.env` file with your FRED API key:
  ```env
  FRED_API_KEY=your_fred_api_key_here
  ```
- **Authentication**:  
  Update credentials and cookie settings in `config.yaml`.

---

## How to Run
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Set up environment variables**
   - Copy `.env.example` to `.env` and add your FRED API key
3. **Run the app**
   ```bash
   streamlit run app.py
   ```
4. **(Optional) Authentication app**
   ```bash
   streamlit run auth-app.py
   ```

---

## To-Do / Pending
- [ ] User handling - In Progress
- [ ] User Logs - In progress
- [ ] Set Up API to track usage per user (Might not be necessary yet)
- [ ] Update with Loan Rates
- [ ] Evaluate other frameworks for creating a full on web app.
- [ ] FHLB Support: Scrape or import from Excel (no API - POC was done with selenium)
    - We’ll need a different setup for deployment since headless browsers aren’t supported in most cloud environments.
- [ ] Add CME rates (license required for some endpoints)
- [ ] Handle CME Group API subscription ($25/month)
- [ ] Add more robust error handling for missing/invalid data
- [ ] Extend API endpoints (see `api/`)
- [ ] UI/UX improvements and more visualizations

See the `TODO` file for more details.

---

## License
Proprietary / Internal (update as appropriate)

---

## Contact
Aurore Labs — [aurorelabs.ai](https://aurorelabs.ai)