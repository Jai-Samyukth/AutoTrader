#!/usr/bin/bash
echo "Printing out the requirements.txt and storing it in files."

uv export --no-hashes > requirements.txt
uv export --no-hashes --no-group dev > requirements.dev.txt

