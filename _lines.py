with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    lines = f.readlines()
print('总行数:', len(lines))
print('最后30行:')
for i,l in enumerate(lines[-30:], len(lines)-29):
    print(i, repr(l[:120]))
