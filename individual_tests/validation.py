import jsonschema
import simplejson as json

# json_schema_file = open('input_schema.json',"r")
# schema_data = json_schema_file.read()
# schema = json.loads(schema_data)
#
# json_input_file = open('input.json',"r")
# input_data = json_input_file.read()
# input = json.load(input_data)

with open('input_schema_last2.json', 'r') as json_schema_file:
    schema_data = json_schema_file.read()
schema = json.loads(schema_data)

with open('input_none.json', 'r') as json_input_file:
    input_data = json_input_file.read()
input = json.loads(input_data)


jsonschema.validate(input, schema)
