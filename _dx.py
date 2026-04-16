import sys; sys.stdout.reconfigure(encoding='utf-8')
with open(r'c:\Users\Administrator\Desktop\线索\线索看板.html','r',encoding='utf-8') as f:
    content = f.read()
print('文件大小:', len(content), '字符')
# 检查三个占位符是否还在
for ph in ['%%DATA_JS%%','%%COST_JS%%','%%ECHARTS_JS%%']:
    if ph in content:
        print('FAIL 占位符未替换:', ph)
    else:
        print('OK 占位符已替换:', ph)
# 检查ECharts
if 'echarts' in content:
    print('OK ECharts内嵌：检测到echarts关键词')
else:
    print('FAIL ECharts未内嵌')
# 检查数据
import re
m = re.search(r'var ALL\s*=\s*(\[.*?\]);', content, re.DOTALL)
if m:
    arr_text = m.group(1)
    count = arr_text.count('{')
    print(f'OK 数据已内嵌：约{count}条记录')
else:
    print('FAIL 未找到 var ALL = [...] 数据块')
# 检查loading
if 'loading.style.display' in content:
    print('OK loading隐藏代码存在')
else:
    print('FAIL loading隐藏代码不存在')
# 检查init函数
if 'function initCharts()' in content or 'function init(' in content:
    print('OK initCharts/init函数存在')
else:
    print('FAIL init函数不存在')
# 检查echarts初始化
ec_init = content.count('echarts.init')
print(f'ECharts.init调用次数: {ec_init}')
# 检查DOMContentLoaded
if 'DOMContentLoaded' in content:
    print('OK DOMContentLoaded事件存在')
else:
    print('FAIL DOMContentLoaded事件不存在')
# 打印前20行
lines = content.split('\n')
print('\n--- 前20行 ---')
for i,l in enumerate(lines[:20],1):
    print(i, repr(l[:120]))
