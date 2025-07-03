#!/usr/bin/env python3
import sqlite3
import sys
import os

# Change to backend directory
os.chdir('backend')

conn = sqlite3.connect('data/outlets.db')
cursor = conn.cursor()

print("=== EXACT OUTLET COUNTS FROM DATABASE ===\n")

# Test all KL patterns that should be included
kl_patterns = [
    ('kuala lumpur', '%kuala lumpur%'),
    ('wilayah persekutuan kuala lumpur', '%wilayah persekutuan kuala lumpur%'),
    ('wp kuala lumpur', '%wp kuala lumpur%'),
    ('kl (with spaces)', '% kl %'),
    ('klcc', '%klcc%'),
    ('kl eco city', '%kl eco city%'),
    ('kl gateway', '%kl gateway%'),
    ('kl sentral', '%kl sentral%')
]

total_kl = 0
kl_ids = set()

print("KL Pattern Breakdown:")
for name, pattern in kl_patterns:
    cursor.execute(f"SELECT COUNT(*), GROUP_CONCAT(id) FROM outlets WHERE LOWER(address) LIKE LOWER('{pattern}')")
    count, ids = cursor.fetchone()
    if ids:
        id_list = [int(x) for x in ids.split(',')]
        kl_ids.update(id_list)
    print(f"  {name}: {count} outlets")
    total_kl += count

print(f"\nTotal KL outlets (with overlaps): {total_kl}")
print(f"Unique KL outlets: {len(kl_ids)}")

# Get exact unique KL count using OR conditions
kl_query = """
SELECT COUNT(*) FROM outlets 
WHERE LOWER(address) LIKE LOWER('%kuala lumpur%')
   OR LOWER(address) LIKE LOWER('%wilayah persekutuan kuala lumpur%')
   OR LOWER(address) LIKE LOWER('%wp kuala lumpur%')
   OR LOWER(address) LIKE LOWER('% kl %')
   OR LOWER(address) LIKE LOWER('%klcc%')
   OR LOWER(address) LIKE LOWER('%kl eco city%')
   OR LOWER(address) LIKE LOWER('%kl gateway%')
   OR LOWER(address) LIKE LOWER('%kl sentral%')
"""
cursor.execute(kl_query)
exact_kl_count = cursor.fetchone()[0]
print(f"Exact KL count (OR query): {exact_kl_count}")

# Selangor count
cursor.execute("SELECT COUNT(*) FROM outlets WHERE LOWER(address) LIKE LOWER('%selangor%')")
selangor_count = cursor.fetchone()[0]
print(f"\nSelangor outlets: {selangor_count}")

# Test current agent query for KL
current_kl_query = """
SELECT COUNT(*) FROM outlets WHERE 1=1 AND (
    LOWER(address) LIKE LOWER('%kuala lumpur%') OR 
    LOWER(address) LIKE LOWER('%wilayah persekutuan kuala lumpur%') OR 
    LOWER(address) LIKE LOWER('%wp kuala lumpur%') OR 
    LOWER(address) LIKE LOWER('% kl %') OR 
    LOWER(address) LIKE LOWER('%klcc%') OR 
    LOWER(address) LIKE LOWER('%kl eco city%') OR 
    LOWER(address) LIKE LOWER('%kl gateway%') OR 
    LOWER(address) LIKE LOWER('%kl sentral%')
)
"""
cursor.execute(current_kl_query)
current_agent_kl = cursor.fetchone()[0]
print(f"\nCurrent agent KL query result: {current_agent_kl}")

conn.close()
