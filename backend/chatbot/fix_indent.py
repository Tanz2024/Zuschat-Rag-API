#!/usr/bin/env python3

# Fix the indentation issue in enhanced_minimal_agent.py
with open('enhanced_minimal_agent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()


del lines[1476:1484]

# Insert the correct conditional structure
correct_lines = [
    '            if any(term in query_lower for term in ["show all", "all products", "show products", "list all"]):\n',
    '                response_parts.append(f"**Here are all {len(products)} products in our ZUS Coffee collection:**\\n")\n',
    '            elif is_price_query:\n',
    '                if "cheap" in query_lower or "cheapest" in query_lower:\n',
    '                    response_parts.append(f"**Here are our most affordable products ({len(products)} item{\'s\' if len(products) != 1 else \'\'}):**\\n")\n',
    '                elif "expensive" in query_lower or "most expensive" in query_lower:\n',
    '                    response_parts.append(f"**Here are our premium products ({len(products)} item{\'s\' if len(products) != 1 else \'\'}):**\\n")\n',
    '                else:\n',
    '                    response_parts.append(f"**Products matching your price criteria ({len(products)} item{\'s\' if len(products) != 1 else \'\'}):**\\n")\n'
]

# Insert the correct lines at position 1476
for i, line in enumerate(correct_lines):
    lines.insert(1476 + i, line)

with open('enhanced_minimal_agent.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed indentation issue in enhanced_minimal_agent.py")
