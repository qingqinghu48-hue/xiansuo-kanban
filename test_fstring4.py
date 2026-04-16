# Test the exact patterns used in generate_html.py

# Trend chart series
try:
    code = f"series:[{{{name:'入库量',type:'bar',data:[1,2],itemStyle:{{{{color:'#2563eb'}}}}},barWidth:'60%'}}}}]"
    print("Trend series OK:", code)
except Exception as e:
    print("Trend series FAIL:", e)

# Pie chart series
try:
    code = f"series:[{{{type:'pie',radius:['38%','68%'],data:[1,2],label:{{formatter:'{{b}}\\n{{d}}%'}}}}}}]"
    print("Pie series OK:", code)
except Exception as e:
    print("Pie series FAIL:", e)

# Cost chart series (two items)
try:
    code = f"series:[{{{name:'营销消耗',type:'bar',data:[1,2],itemStyle:{{{{color:'#2563eb'}}}}}}}}},{{{name:'单条成本',type:'line',yAxisIndex:1,data:[1,2],itemStyle:{{{{color:'#f43f5e'}}}}},smooth:true}}}}}}]"
    print("Cost series OK:", code)
except Exception as e:
    print("Cost series FAIL:", e)

# Full cost setOption
try:
    code = f"cc.setOption({{tooltip:{{trigger:'axis',formatter:function(params){{return params[0].name;}}}},legend:{{data:['x'],right:10,top:0}},grid:{{top:35,right:55,bottom:25,left:60}},xAxis:{{type:'category',data:['a'],axisLabel:{{rotate:30,fontSize:11}}}},yAxis:[{{type:'value',name:'y',position:'left'}}],series:[{{{name:'消耗',type:'bar',data:[1],itemStyle:{{{{color:'#2563eb'}}}}}}}}},{{{name:'单条',type:'line',yAxisIndex:1,data:[1],itemStyle:{{{{color:'#f43f5e'}}}}},smooth:true}}}}}}]}})"
    print("Full cost OK:", code)
except Exception as e:
    print("Full cost FAIL:", e)
