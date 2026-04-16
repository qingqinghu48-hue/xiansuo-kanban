with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    content = f.read()
start = content.find('const ALL = ')
end = content.find('const PLAT_COLORS')
print('ALL段前60:', repr(content[start:start+60]))
print('ALL段末60:', repr(content[end-60:end]))
print('含3引号:', '"""' in content)
sep = ']' + chr(59)  # ]
print('含分号闭合:', sep in content)
