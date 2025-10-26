# README

## MGNREGA Webscraping tool

The project scrapes the tabular data from the MGNREGA MIS website: https://nreganarep.nic.in/
and stores the data in a PostgreSQL database for further analysis and visualization.

## Project Structure (Update as you add files!)

```
cs699_project/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── images/
│       └── mgnrega.png
├── backend/
│   ├── web_scraping/
│   │   └── webscraping.ipynb
│   └── database/
│       └── db.py
└── README.md
```

## Steps to test webscraping script

1. Create a virtual environment using: `python3 -m venv venv`
2. Activate the virtual environment using: `source venv/bin/activate`
3. Install the requirements using: `pip install -r requirements.txt`
4. Run the python script `python src/backend/web_scraping/automate.py`
5. Create a .env file for supabase db, refer the `.env.example`
