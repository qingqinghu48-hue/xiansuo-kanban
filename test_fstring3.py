# Test what actually works in f-string
# The problematic line: series:[{...itemStyle:{color:'#2563eb'}...}]

# Test: array with object containing nested object - all braces escaped
try:
    code = f"series:[{{{{name:'入库量',type:'bar',data:[1,2,3],itemStyle:{{{{color:'#2563eb'}}}}}}}}]"
    print("series OK:", code)
except Exception as e:
    print("series FAIL:", e)

# Test: tooltip formatter with params
try:
    code = f"tooltip:{{trigger:'axis',formatter:function(params){{return params[0].name;}}}}"
    print("tooltip OK:", code)
except Exception as e:
    print("tooltip FAIL:", e)

# Test: full cc.setOption with nested tooltip formatter
try:
    code = f"cc.setOption({{tooltip:{{trigger:'axis',formatter:function(params){{return params[0].name;}}}}}})"
    print("setOption OK:", code)
except Exception as e:
    print("setOption FAIL:", e)
