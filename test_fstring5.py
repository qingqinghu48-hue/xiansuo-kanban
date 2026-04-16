# Test the exact problematic pattern
# Line: series:[{name:'营销消耗',type:'bar',data:spends,itemStyle:{color:'#2563eb'}}]
# This is inside an f-string with surrounding code

# Full series line (what we need)
template = "series:[{{{name:'营销消耗',type:'bar',data:[1,2],itemStyle:{{{{color:'#2563eb'}}}}}}}}},{{{name:'单条成本',type:'line',yAxisIndex:1,data:[1,2],itemStyle:{{{{color:'#f43f5e'}}}}},smooth:true}}}}}}]"
try:
    result = f"var x = {template}"
    print("OK:", result[:80])
except Exception as e:
    print("FAIL:", type(e).__name__, str(e)[:100])

# Simpler: series with nested object only
template2 = "series:[{{{name:'test',itemStyle:{{{{color:'red'}}}}}}}}}]"
try:
    result2 = f"var x = {template2}"
    print("Simple OK:", result2)
except Exception as e:
    print("Simple FAIL:", type(e).__name__, str(e)[:100])
