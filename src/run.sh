#!/bin/bash

echo "Running asyncMain.py..."
/usr/local/bin/python3 /app/asyncMain.py
if [ $? -ne 0 ]; then
  echo "asyncMain.py failed. Exiting."
  exit 1
fi

echo "Running TTLGeneralOutput.py..."
/usr/local/bin/python3 /app/TTLGeneralOutput.py
if [ $? -ne 0 ]; then
  echo "TTLGeneralOutput.py failed. Exiting."
  exit 1
fi

# Run the third script
echo "Running upload.py..."
/usr/local/bin/python3 /app/upload.py
if [ $? -ne 0 ]; then
  echo "upload.py failed. Exiting."
  exit 1
fi

echo "All scripts executed successfully."