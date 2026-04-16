content = open(r'c:\Users\Administrator\Desktop\线索\线索看板.html', 'r', encoding='utf-8').read()
old = "var pc = {};\n    filtered.forEach(function(r){ pc[r['平台']||'其他']=(pc[r['平台']||'其他']||0)+1; });"
new = "var pc = {};\n    filtered.forEach(function(r){ var src = r['线索来源'] || r['平台'] || '未知'; pc[src]=(pc[src]||0)+1; });"
print('Found:', old in content)
content2 = content.replace(old, new, 1)
print('Changed:', content != content2)
open(r'c:\Users\Administrator\Desktop\线索\线索看板.html', 'w', encoding='utf-8').write(content2)
print('Done')
