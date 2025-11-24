# README

## MGNREGA Webscraping tool

The project scrapes the tabular data from the MGNREGA MIS website: https://nreganarep.nic.in/
and stores the data in a PostgreSQL database for further analysis and visualization.

## Project Structure

```
cs699_project/
├── frontend/
│   ├── app.py
│   ├── static
│       └── images/
│       └── templates/
├── backend/
│   ├── web_scraping/
│   │   └── scrape.py
│   │   └── automate.py
│   └── database/
│       └── db_dump.py
└── README.md
```

## Details about Webscraping
1. `backend` module contains the scripts for scraping the website and uploading the data to the Postgres database.
2. `scrape.py` handles the scraping of required tabular data from the mgnrega website and `automate.py` runs this scraping module for all the districts considered.
3. This data is then uploaded to an online Postgres database [[supabase.com](https://supabase.com/)] using psycopg and supabase python packages.
4. The data from this Postgres DB is used in the flask application for genereating report and visualization plots.

## Steps to run the project

1. Create a virtual environment using: `python3 -m venv venv`
2. Activate the virtual env using: `source venv/bin/activate`
3. Install the requirements using: `pip install -r requirements.txt`
4. Run the flask application `python src/frontend/app.py`
