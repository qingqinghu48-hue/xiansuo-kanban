# Test f-string nested braces
x = 1
# Test 1: simple nested (should fail)
try:
    s1 = f"{{{{color:'#2563eb'}}}}"
    print("Test1 OK:", s1)
except Exception as e:
    print("Test1 FAIL:", e)

# Test 2: what we need
try:
    s2 = f"itemStyle:{{{{color:'#2563eb'}}}}"
    print("Test2 OK:", s2)
except Exception as e:
    print("Test2 FAIL:", e)

# Test 3: full line
try:
    s3 = f"{{name:'test',type:'bar',itemStyle:{{{{color:'#2563eb'}}}}}}"
    print("Test3 OK:", s3)
except Exception as e:
    print("Test3 FAIL:", e)
