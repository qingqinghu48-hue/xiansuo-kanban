import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\Administrator\Desktop\线索\线索看板.html', encoding='utf-8') as f:
    content = f.read()

# Extract ALL array - look for pattern
idx = content.find('const ALL = ')
if idx < 0:
    print('const ALL not found!')
else:
    print(f'const ALL at pos {idx}')
    # Find the start of the array
    arr_start = content.find('[', idx)
    if arr_start < 0:
        print('Array bracket not found')
    else:
        # Find matching close bracket - count brackets
        depth = 0
        end = arr_start
        in_str = False
        str_char = None
        escape = False
        for i in range(arr_start, len(content)):
            c = content[i]
            if escape:
                escape = False
                continue
            if c == '\\' and in_str:
                escape = True
                continue
            if c in ('"', "'") and not in_str:
                in_str = True
                str_char = c
            elif in_str and c == str_char:
                in_str = False
                str_char = None
            elif not in_str:
                if c == '[':
                    depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break

        raw = content[arr_start:end]
        print(f'Array length: {len(raw)} chars')
        try:
            data = json.loads(raw)
            print(f'JSON OK, items: {len(data)}')
            if data:
                print(f'Keys: {list(data[0].keys())}')
        except Exception as ex:
            print(f'JSON error: {ex}')
            err = str(ex)
            pos_m = re.search(r'position (\d+)', err)
            if pos_m:
                pos = int(pos_m.group(1))
                snippet = raw[max(0,pos-80):pos+80]
                print(f'Error context: ...{snippet}...')
