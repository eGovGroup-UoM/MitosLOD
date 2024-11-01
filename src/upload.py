import requests
import os
from requests.auth import HTTPDigestAuth

def upload_ttl_to_virtuoso(ttl_file, virtuoso_url, graph_uri, username, password):
  with open(ttl_file, 'rb') as f:
      data = f.read()

  response = requests.post(
      f"{virtuoso_url}/sparql-graph-crud-auth?graph={graph_uri}",
      data=data,
      auth=HTTPDigestAuth(username, password),
  )

  if response.status_code == 200 or response.status_code == 201:
      print("Upload successful")
  else:
      raise Exception(f"Failed to upload. Status code: {response.status_code}, Response: \"{response.text}\"")

def main():
    virtuoso_url = os.getenv('VIRTUOSO_URL')
    graph_uri = os.getenv('GRAPH_URI')
    username = os.getenv('VIRTUOSO_USERNAME')
    password = os.getenv('VIRTUOSO_PASSWORD')

    if None in (virtuoso_url, graph_uri, username, password):
        print("One or more environment variables are missing!")
        return

    upload_ttl_to_virtuoso("/app/data/generated_data.ttl", virtuoso_url, graph_uri, username, password)

if __name__ == "__main__":
    main()