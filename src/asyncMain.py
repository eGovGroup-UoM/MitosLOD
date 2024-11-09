import asyncio
import httpx
import csv
import os
import json
from datetime import datetime
from processorMain import extract_data_for_csv, save_to_csv

BASE_URL = "https://api.digigov.grnet.gr/v1/services"


async def fetch_services_list():
    params = {'page': 1}
    services = []
    async with httpx.AsyncClient() as client:
        while True:
            temp_result = await client.get(BASE_URL, params=params)
            json_result = temp_result.json()
            services += json_result['data']
            if len(services) < json_result['total']:
                params['page'] += 1
            else:
                break
        return services

service_path = "/app/data/services/"
async def fetch_updated(services_list):
    for service in services_list:
        filepath = f"{service_path}{service['id']}.json"
        if not os.path.exists(filepath):
            print(f"Downloading service #{service['id']}")
            url = f"{BASE_URL}/{service['id']}"
            data = await fetch_data_from_url_async(url)
            with open(filepath, 'a') as outfile:
                json.dump(data, outfile, ensure_ascii=False)
        else:
            local_time = os.path.getmtime(filepath)
            mitos_time = datetime.fromisoformat(service['last_updated']).timestamp()
            if mitos_time > local_time:
                print(f"Updating service #{service['id']}")
                url = f"{BASE_URL}/{service['id']}"
                data = await fetch_data_from_url_async(url)
                with open(filepath, 'w') as outfile:
                    json.dump(data, outfile, ensure_ascii=False)


def delete_deprecated_services(services_list):
    local_ids = [f.replace('.json','') for f in os.listdir(service_path)]
    mitos_ids = [service['id'] for service in services_list]

    for id in local_ids:
        if id not in mitos_ids:
            print(f"Removing #{id} service file")
            os.remove(f"{service_path}/{id}.json")

async def fetch_data_from_url_async(url):
    """Fetches data from the given URL using httpx asynchronously."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

async def main_exec_async(services_list, keys, output_filename):
    base_url = "https://api.digigov.grnet.gr/v1/services/"

    all_extracted_data = []

    for service in services_list:
        filepath = f"{service_path}{service['id']}.json"
        with open(filepath, 'r') as infile:
                data = json.load(infile)

        extracted_rows = extract_data_for_csv(data, keys, output_filename)

        all_extracted_data.extend(extracted_rows)

    print(f"Saving {len(all_extracted_data)} rows to {output_filename}")
    save_to_csv(output_filename, keys, all_extracted_data)

async def process_csvs_async(services_list):
    #print("Processing CSV1...")  # Debug statement
    properties = ["id","uuid","status","estimated_implementation_time","provided_language","org_owner","provision_org","output_type","cost_min","cost_max","life_events","alternative_titles","official_title","description","last_updated"]
    await main_exec_async(services_list, properties, '/app/data/ProcessGeneral.csv')

    #print("Processing CSV2...")  # Debug statement
    properties2 = ["id","conditions_name","conditions_num_id","conditions_type"]
    await main_exec_async(services_list, properties2, '/app/data/ProcessConditions.csv')

    #print("Processing CSV3...")  # Debug statement
    properties3 = ["id","evidence_description","evidence_num_id","evidence_owner","evidence_related_url","evidence_type"]
    await main_exec_async(services_list, properties3, '/app/data/ProcessEvidence.csv')

    #print("Processing CSV4...")  # Debug statement
    properties4 = ["id","rule_decision_number","rule_ada","rule_description"]
    await main_exec_async(services_list, properties4, '/app/data/ProcessRules.csv')

async def main_async():
    services_list = await fetch_services_list()
    print(f"Found {len(services_list)} services")
    await fetch_updated(services_list)
    delete_deprecated_services(services_list)
    await process_csvs_async(services_list)

if __name__ == "__main__":
    asyncio.run(main_async())
