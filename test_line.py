import json
from pathlib import Path

BASE = Path(r'c:\Users\Administrator\Desktop\线索')
with open(BASE / 'dashboard_data.json', encoding='utf-8') as f:
    DATA = json.load(f)

DATA_JSON = json.dumps(DATA, ensure_ascii=False)

# Generate the line as the current script does
line = 'const ALL = """ + DATA_JSON + """;'
result = line.replace('DATA_JSON', repr(DATA_JSON[:200]))
print(result[:300])

# Write to test file
test_out = 'const ALL = """ + DATA_JSON + """;'
with open(BASE / 'test_out.txt', 'w', encoding='utf-8') as f:
    # Simulate what the script actually does - write to HTML
    f.write('<script>\n')
    f.write('const ALL = """ + DATA_JSON + """;\n')
    f.write('const X = 1;\n')
    f.write('</script>\n')
    f.write('<p>ALL=' + DATA_JSON[:300] + '</p>')

# Read back
with open(BASE / 'test_out.txt', 'r', encoding='utf-8') as f:
    content = f.read()

print('Written content (script part):')
idx = content.find('<script>')
print(content[idx:idx+200])
print('---')
print('Triple quotes in file:', '"""' in content)
