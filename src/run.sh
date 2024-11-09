#!/bin/bash

echo "Starting run at $(date)"
echo "Getting Services from Mitos... (asyncMain.py)"
/usr/local/bin/python3 /app/asyncMain.py
if [ $? -ne 0 ]; then
  echo "asyncMain.py failed. Exiting."
  exit 1
fi

echo "Transforming into RDF... (TTLGeneralOutput.py)"
/usr/local/bin/python3 /app/TTLGeneralOutput.py
if [ $? -ne 0 ]; then
  echo "TTLGeneralOutput.py failed. Exiting."
  exit 1
fi

# Run the third script
echo "Uploading to Virtuoso... (upload.py)"
/usr/local/bin/python3 /app/upload.py
if [ $? -ne 0 ]; then
  echo "upload.py failed. Exiting."
  exit 1
fi

echo "All scripts executed successfully at $(date)."