from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from flask import jsonify, request


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Comma-separated list of district table names in supabase
DISTRICT_TABLES = ["ratnagiridb","punedb","thanedb","nagpurdb","kolhapurdb", "bhandaradb", "gadchirolidb", "raigaddb", "sanglidb", "sindhudurgdb", "wardhadb", "sataradb", "palghardb"]


if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

def get_table_from_state(state_name: str):
    return state_name.lower().replace(" ", "") + "db"


def get_state_from_table(table_name: str):
    name = table_name.replace("db", "")
    return name.upper()


def _distinct_values_across_tables(column_name: str):
    
    seen = set()
    quoted = f'"{column_name}"'
    table = DISTRICT_TABLES[0]
   
        # fetch ONLY the target column
    resp = (
        supabase.table(table)
        .select(quoted)
        .neq(column_name, None)     # ignore NULLs
        .execute()
    )

    rows = resp.data
    

    for row in rows:
        val = row.get(column_name)
        if val is not None:
            seen.add(str(val).strip())

   

    values = list(seen)

    # auto-sort: descending for year columns
    if "year" in column_name.lower():
        values.sort(reverse=True)
    else:
        values.sort()

    return values


@app.route("/")
def home():
    # column names exactly as in your Supabase tables
    years = _distinct_values_across_tables("Work Start Fin Year")
    # use District Name as the selectable location list (there is no 'state' column in the provided schema)
    districts = [get_state_from_table(t) for t in DISTRICT_TABLES]

    print(f"DEBUG: Found {len(years)} years and {len(districts)} districts.")
    return render_template("index.html", years=years, all_states=districts)


@app.route("/report")
def show_report():
    selected_year = request.args.get("financial_year")
    selected_state = request.args.get("state_name")  # this will be matched against "District Name"
    selected_block = request.args.get("block_name", "")
    selected_panchayat = request.args.get("panchayat_name", "")

    page = int(request.args.get("page", 1))
    per_page=500
    results = []
    blocks_set = set()
    
    if selected_year and selected_state:
        
        table = get_table_from_state(selected_state)
        query = supabase.table(table).select("*")
        query = query.eq('"Work Start Fin Year"', selected_year)
        query = query.eq('"District Name"', selected_state)

        resp = query.range(0, 20000).execute()
        if resp.data:
            for row in resp.data:
                blocks_set.add(row.get("Block Name"))
                

                # Apply optional filters
                if selected_block and row.get("Block Name") != selected_block:
                    continue
                if selected_panchayat and row.get("Panchayat Name") != selected_panchayat:
                    continue

                results.append(row)
    

        # sort results by Block Name (fallback to Work Name)
        results = sorted(
            results,
            key=lambda r: (r.get("Block Name") or r.get("Work Name") or "")
        )
    # print(results[0])

    total_items = len(results)
    total_pages = max((total_items + per_page - 1) // per_page, 1)

    # Slice results for the current page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    return render_template(
        "report.html",
        results=paginated_results,
        year=selected_year,
        state=selected_state,
        block_name=selected_block,
        panchayat_name=selected_panchayat,
        all_blocks=sorted(blocks_set),
        all_panchayats=[],
        page=page,
        total_pages=total_pages
    )

@app.route("/get_panchayats")
def get_panchayats():
    year = request.args.get("financial_year")
    state = request.args.get("state_name")
    block = request.args.get("block_name")
    panchayats_set = set()

    if not (year and state and block):
        return jsonify([])

    table = get_table_from_state(state)
    try:
        resp = (
            supabase.table(table)
            .select('"Panchayat Name"')
            .eq('"Work Start Fin Year"', year)
            .eq('"District Name"', state)
            .eq('"Block Name"', block)
            .range(0, 10000)
            .execute()
        )
        if resp.data:
            for row in resp.data:
                p_name = row.get("Panchayat Name")
                if p_name:  # only non-empty panchayats
                    panchayats_set.add(p_name)
    except Exception as e:
        print(f"Error fetching panchayats from {table}: {e}")
           

    return jsonify(sorted(panchayats_set))



@app.route("/get_plots")
def get_plots():
    year = request.args.get("financial_year")
    state = request.args.get("state_name")
    block = request.args.get("block_name", "")
    panchayat = None

    results = []
    if year and state:
        table = get_table_from_state(state)
            
        query = supabase.table(table).select("*")
        query = query.eq('"Work Start Fin Year"', year)
        query = query.eq('"District Name"', state)
        if block:
            query = query.eq('"Block Name"', block)
        if panchayat:
            query = query.eq('"Panchayat Name"', panchayat)

        resp = query.range(0, 20000).execute()
        if resp.data:
            results.extend(resp.data)
    

    # Pass results to plots.html for plotting
    return render_template("plots.html", results=results, year=year, state=state, block=block, panchayat=panchayat)

if __name__ == "__main__":
    app.run(debug=True, port=5001)