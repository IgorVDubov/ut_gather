def run_middle_5():
    v1 = 0
    v2 = 0
    v3 = 0
    v4 = 0
    v5 = 0
    def inner(v):
        nonlocal v1, v2, v3, v4, v5
        v_middle = (v + v1 + v2 + v3 + v4) / 5 
        v4 = v3
        v3 = v2
        v2 = v1
        v1 = v
        return v_middle
    return inner

c = run_middle_5()
b = run_middle_5()

print(f'C:{c(1)}')
print(f'C:{c(1)}')
print(f'C:{c(1)}')
print(f'C:{c(1)}')
print(f'C:{c(1)}')
print(f'b:{b(2)}')
print(f'C:{c(1)}')
print(f'b:{b(2)}')