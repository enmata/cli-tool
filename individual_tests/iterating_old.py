import os
import json

# with open('input_multiple.json', 'r') as json_input_file:
#     input_data = json_input_file.read()
# input = json.load(input_data)

# json_input_file = open('input_multiple.json', 'r')
# input = json.load(json_input_file)

with open('input_multiple.json', 'r') as json_input_file:
    input = json.load(json_input_file)

for resource in input:
    print("--NewItem--")
    print(resource["type"])
    print(resource["name"])
    print(resource["properties"])
