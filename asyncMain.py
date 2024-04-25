import asyncio
import httpx
import csv
from processorMain import extract_data_for_csv, save_to_csv

BASE_URL = "https://api.digigov.grnet.gr/v1/services"

page_limit = 35

async def fetch_ids(page=1, limit=100):
    all_ids = []
    async with httpx.AsyncClient() as client:
        for current_page in range(1, page_limit):
            print(len(all_ids))
            params = {
                "page": current_page,
                "limit": limit
            }
            resp = await client.get(BASE_URL, params=params)
            resp.raise_for_status()

            # Check if response is JSON
            if resp.headers.get('content-type') == 'application/json':
                json_data = resp.json()
                # Extract IDs from the nested 'data' key
                if 'data' in json_data and isinstance(json_data['data'], list):
                    all_ids.extend( [item['id'] for item in json_data['data']] )
                else:
                    print("Unexpected JSON structure:", json_data)
                    continue
            else:
                print("Received non-JSON response:", resp.text)
                continue
        return all_ids

async def fetch_data_from_url_async(url):
    """Fetches data from the given URL using httpx asynchronously."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

async def main_exec_async(ids, keys, output_filename):
    base_url = "https://api.digigov.grnet.gr/v1/services/"

    all_extracted_data = []

    for id_ in ids:
        full_url = base_url + id_
        print(f"Fetching data from URL: {full_url}")  # Debug statement
        data = await fetch_data_from_url_async(full_url)

        extracted_rows = extract_data_for_csv(data, keys, output_filename)

        all_extracted_data.extend(extracted_rows)

    print(f"Saving {len(all_extracted_data)} rows to {output_filename}")
    save_to_csv(output_filename, keys, all_extracted_data)

async def process_csvs_async(ids):
    #print("Processing CSV1...")  # Debug statement
    properties = ["id","uuid","status","estimated_implementation_time","provided_language","org_owner","provision_org","output_type","cost_min","cost_max","life_events","alternative_titles","official_title","description","last_updated"]
    await main_exec_async(ids, properties, 'dags/data/ProcessGeneral.csv')

    #print("Processing CSV2...")  # Debug statement
    properties2 = ["id","conditions_name","conditions_num_id","conditions_type"]
    await main_exec_async(ids, properties2, 'dags/data/ProcessConditions.csv')

    #print("Processing CSV3...")  # Debug statement
    properties3 = ["id","evidence_description","evidence_num_id","evidence_owner","evidence_related_url","evidence_type"]
    await main_exec_async(ids, properties3, 'dags/data/ProcessEvidence.csv')

    print("Processing CSV4...")  # Debug statement
    properties4 = ["id","rule_decision_number","rule_ada","rule_description"]
    await main_exec_async(ids, properties4, 'dags/data/ProcessRules.csv')

async def main_async():
    ids = await fetch_ids()
    print("Fetched IDs:", ids);
    await process_csvs_async(ids)

if __name__ == "__main__":
    asyncio.run(main_async())
