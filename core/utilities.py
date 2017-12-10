import pandas as pd

def summarize_json(raw_json, max_expand=20):
    for key in raw_json:
        value = raw_json[key] 
        if isinstance(value, (int, float, complex, str, tuple)):
            print(f'{key}: {value}')
        elif isinstance(value, list):
            print(f'{key}: {type(value)} with {len(value)} elements')
            if len(value) <  max_expand:
                for item in value:
                    if isinstance(value, (int, float, complex, str, tuple)):
                        print(f'    {item}')
                    else:
                        print(f'    {type(item)} with {len(item)} elements')
        elif isinstance(value, dict):
            print(f'{key}: {type(value)} with {len(value)} elements')
            if len(value.keys()) <  max_expand:
                for item in value.keys():
                    if isinstance(value[item], (int, float, complex, str, tuple)):
                        print(f'    {item}: {value[item]}')
                    else:
                        print(f'    {item}: {type(value[item])} with {len(value[item])} elements')          
        else:
            print(f'{key}: {type(value)}')