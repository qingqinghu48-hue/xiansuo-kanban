with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    content = f.read()

# Check key markers
print('id="cards":', 'id="cards"' in content)
print('id="chartTrend":', 'id="chartTrend"' in content)
print('id="tableBody":', 'id="tableBody"' in content)
print('renderAll():', 'renderAll()' in content)
print('renderCards():', 'renderCards()' in content)
print('let filtered:', 'let filtered' in content)
print('ALL.length:', 'ALL.length' in content)

# Check ALL assignment
idx = content.find('const ALL = ')
end = content.find(';', idx)
print('\nALL赋值行:', content[idx:end+1][:100])

# Check last line before </script>
last_lines = content.rfind('<script>')
last_script = content[last_lines:]
print('\n最后script段前200:', last_script[:200])

# Count key divs
print('\nchartTrend出现次数:', content.count('chartTrend'))
print('chart-box出现次数:', content.count('chart-box'))
