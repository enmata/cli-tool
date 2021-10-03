import os
import json

# with open('input_multiple.json', 'r') as json_input_file:
#     input_data = json_input_file.read()
# input = json.load(input_data)

# json_input_file = open('input_multiple.json', 'r')
# input = json.load(json_input_file)

with open('input_multiple.json', 'r') as json_input_file:
    input = json.load(json_input_file)

def listingec2():
    return "Hello ec2"

def listingsqs():
    return "Hello sqs"

def listings3():
    return "Hello sqs"


for resource in input:
    resource_type = resource["type"]
    print("--NewItem--{}".format(resource_type))
    switcher = {
        "ec2": listingec2(),
        "sqs": listingsqs(),
        "s3":  listings3()
    }
    result = switcher.get(resource_type, 'default')
    print(result)
