with open(r'c:\Users\Administrator\Desktop\线索\echarts.min.js','r',encoding='utf-8') as f:
    c = f.read()
# Find the UMD wrapper structure
import re
# Find the IIFE/factory pattern
patterns = [
    r'\(function\(.*?typeof define.*?typeof exports.*?\}\)\)\(',
    r'"use strict";.*?define',
    r'if\s*\(\s*typeof\s+define\s*===\s*["\']function["\']',
]
for pat in patterns:
    m = re.search(pat, c, re.DOTALL)
    if m:
        print(f'模式: {pat[:40]}...')
        print(repr(c[m.start():m.end()+200]))
        print('---')
        break

# Check what the factory returns / sets
# Find "typeof exports" branch
exp_idx = c.find('typeof exports')
if exp_idx > 0:
    print('exports分支附近:')
    print(repr(c[exp_idx:exp_idx+300]))
