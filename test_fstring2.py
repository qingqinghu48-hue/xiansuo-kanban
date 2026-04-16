# Test complex nested f-string with JS objects
# Simulate the actual series line

# Test A: object with nested {}
test_a = f"{{name:'test',itemStyle:{{color:'red'}}}}"
print("A:", test_a)

# Test B: array line (outer { NOT escaped - starts Python expr)
try:
    test_b = f"        {{name:'test',itemStyle:{{color:'red'}}}}"
    print("B:", test_b)
except Exception as e:
    print("B FAIL:", type(e).__name__, e)

# Test C: array line (outer { IS escaped)
try:
    test_c = f"        {{{{'name':\"test\",'itemStyle':{{'color':\"red\"}}}}}}"
    print("C:", test_c)
except Exception as e:
    print("C FAIL:", type(e).__name__, e)
