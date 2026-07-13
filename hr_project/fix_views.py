#!/usr/bin/env python
import re

# Read the file
with open('./hr_portal/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific syntax error at the end of the file
# The issue is with the unterminated string and improper formatting
content = re.sub(r'\"\s*# If not POST, redirect to dashboard\s*\n\s*return redirect\(\'dashboard\'\)\s*\"', 
                 '# If not POST, redirect to dashboard\n    return redirect(\'dashboard\')', content)

# Also fix other lines that have the quote issue
content = re.sub(r'^(\s*)\"(.+)\"$', r'\1\2', content, flags=re.MULTILINE)

# Write the fixed content back
with open('./hr_portal/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed the views.py file")