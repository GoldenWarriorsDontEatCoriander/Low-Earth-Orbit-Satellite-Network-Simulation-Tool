import timeit

setup = """
def handle_a():
    pass

def handle_b():
    pass

def handle_default():
    pass

input = 'condition_b'
handlers = {
    'condition_a': handle_a,
    'condition_b': handle_b
}

def process_input(input_condition):
    handler = handlers.get(input_condition, handle_default)
    handler()

def process_input_if(input_condition):
    if input_condition == 'condition_a':
        handle_a()
    elif input_condition == 'condition_b':
        handle_b()
    else:
        handle_default()
"""

# 测试字典方法
dict_time = timeit.timeit('process_input(input)', setup=setup, number=1000000)

# 测试if方法
if_time = timeit.timeit('process_input_if(input)', setup=setup, number=1000000)

print(f"Dictionary method: {dict_time} seconds")
print(f"If method: {if_time} seconds")
