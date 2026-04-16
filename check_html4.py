import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    content = f.read()

# Find all CSS rules for .cards and .hdr
import re
cards_css = re.findall(r'.cards\s*\{[^}]*\}', content)
hdr_css = re.findall(r'.hdr\s*\{[^}]*\}', content)
body_css = re.findall(r'body\s*\{[^}]*\}', content)
all(content.find('.cards') > 0, 'cards CSS found')
print('cards CSS:', cards_css)
print('hdr CSS:', hdr_css[:2])
print('body CSS:', body_css[:2])

# Check if there are any </style> before </head>
style_count = content.count('</style>')
print('\n</style>出现次数:', style_count)

# Check ECharts CDN
ec_idx = content.find('echarts')
print('\nECharts引用:', repr(content[ec_idx-20:ec_idx+80]))

# Find where the problem might be - check if renderAll has any issue
ra_idx = content.find('function renderAll')
print('\nrenderAll函数:', repr(content[ra_idx:ra_idx+80]))
