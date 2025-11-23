import pandas as pd
from bs4 import BeautifulSoup

def scrapeFunc(html: str):
    """
    Parses an HTML table and converts it into a Pandas DataFrame.

    Args:
        html (str): HTML content containing the table.

    Returns:
        pd.DataFrame: DataFrame containing the table data.
    """

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find the first table
    table = soup.find("table")
    if table is None:
        raise ValueError("No table found in the provided HTML.")

    # Extract header rows
    header_rows = table.find("thead").find_all("tr")
    headers = []

    # Process first header row (handle colspan)
    for th in header_rows[0].find_all(["th", "td"]):
        colspan = int(th.get("colspan", 1))
        text = th.get_text(strip=True)
        headers.extend([text] * colspan)

    # If there's a second header row, refine headers
    if len(header_rows) > 1:
        sub_headers = [th.get_text(strip=True) for th in header_rows[1].find_all(["th", "td"])]
        idx = 0
        for i, h in enumerate(headers):
            if headers.count(h) > 1 and idx < len(sub_headers):
                headers[i] = f"{h}_{sub_headers[idx]}"
                idx += 1

    # Extract table body rows
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all("td")]
        rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Save to CSV
    df.to_csv("output.csv", index=False)
    print("Scraping completed. Sample data:")
    print(df.head())

    return df