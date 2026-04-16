import pathlib
lines = open(pathlib.Path(r'C:\Users\Administrator\Desktop\线索\线索看板.html'), 'r', encoding='utf-8').readlines()
for i, l in enumerate(lines, 1):
    if "getElementById" in l and "loading" in l and "style" in l:
        print(f'Line {i}: {l.rstrip()[:100]}')
        lines[i-1] = "    window.console.error && console.error('JS执行到这里1');\n" + l
        break

with open(pathlib.Path(r'C:\Users\Administrator\Desktop\线索\线索看板.html'), 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("done")
