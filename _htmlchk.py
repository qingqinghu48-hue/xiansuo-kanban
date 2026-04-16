import sys; sys.stdout.reconfigure(encoding='utf-8')
with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    c = f.read()

import re
patterns = [
    r'DOMContentLoaded',
    r'echarts\.init',
    r'var ALL',
    r'window\.__ALL__',
    r'loading\.style\.display\s*=\s*["\']none["\']',
    r'loading\.style',
]
for pat in patterns:
    m = re.search(pat, c)
    if m:
        print(f'Found [{pat}]:')
        print(repr(c[max(0,m.start()-50):m.end()+100]))
        print()
    else:
        print(f'NOT FOUND: {pat}')
