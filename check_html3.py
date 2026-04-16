import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    content = f.read()

print('id="tbody":', 'id="tbody"' in content)
print('id="modalBody":', 'id="modalBody"' in content)

idx = content.find('<table>')
end = content.find('</table>', idx)
print('\ntable前200:', repr(content[idx:idx+200]))

idx2 = content.find('class="cards"')
print('\ncards div:', repr(content[idx2-20:idx2+80]))

idx3 = content.find('renderAll()')
print('\nrenderAll()前100:', repr(content[idx3-100:idx3+20]))
