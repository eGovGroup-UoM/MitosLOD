import requests
from requests.auth import HTTPDigestAuth

def upload_ttl_to_virtuoso(ttl_file, virtuoso_url, graph_uri, username, password):
  with open(ttl_file, 'rb') as f:
      data = f.read()

  response = requests.post(
      f"{virtuoso_url}/sparql-graph-crud-auth?graph={graph_uri}",
      data=data,
      auth=HTTPDigestAuth(username, password),
  )