import json
import os
import subprocess
import argparse
import jsonschema

#Needed for formating some aws cli commands, avoiding
os.environ['AWS_DEFAULT_OUTPUT'] = "json"

def exist_stack(stackName):
    # Description: this function check if stack/resource-group "stackName" name
    # Called by: create action
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: boolean, meaning "true" the stack/resource-group "stackName" name exist, false if does not

    #Getting the list of all stacks
    stack_list = list_stack()
    #Returning boolean True if the stack "stackName" exist on the previous list
    return stackName in stack_list

def create_stack(stackName):
    # Description: this function creates a resource-group, tag based, with stack "stackName" name
    # Called by: create action
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: None

    #Composing command to run
    create_cmd = 'aws resource-groups create-group --name ' + stackName + ' --resource-query \'{ "Type": "TAG_FILTERS_1_0", "Query": "{\\"ResourceTypeFilters\\":[\\"AWS::AllSupported\\"],\\"TagFilters\\":[{\\"Key\\":\\"StackName\\",\\"Values\\":[\\"' + stackName + '\\"]}]}" }\''

    #Creating Stack
    #subprocess.call used instead of due the beckets {} on the command
    subprocess.call(create_cmd, shell=True, stdout=open(os.devnull, 'wb'))

def list_stack():
    # Description: this function gets a list of all stacks/resource-groups
    # Called by: create_stack
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: a list containing all stack/resource-group "stackName"

    #Composing command to run
    cmd = 'aws resource-groups list-groups --output json'

    #Locating stacks
    output = os.popen(cmd)

    stacks = []
    #Formating
    if output:
        output_json = json.load(output)
        for item in output_json["GroupIdentifiers"]:
            stacks.append(item["GroupName"])

    #Returning stacks/resource-groups names
    return stacks

def delete_stack(stackName):
    # Description: this function deletes resources related with stack "stackName"
    # Called by: delete action
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: None

    #Composing command to run
    delete_cmd = 'aws resource-groups delete-group --group "' + stackName + '"'

    #Deleting Linked Resources
    clean_ec2(stackName)
    clean_sqs(stackName)
    clean_s3(stackName)

    #Deleting Stack
    subprocess.call(delete_cmd, shell=True, stdout=open(os.devnull, 'wb'))

def exist_ec2(instanceName,stackName):
    # Description: this function checks if ec2 instance "instanceName" exist on stack/resource-group "stackName"
    # Called by: create action and before create_ec2
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: boolean, meaning "true" the ec2 instance "instanceName" exist on stack/resource-group "stackName, false if does not

    #Composing command to run
    cmd = 'aws ec2 describe-instances --filters "Name=tag:StackName,Values=' + stackName + '" "Name=tag:Name,Values=' + instanceName + '" --output text'

    # Checking if the ec2 instance with the name tag "instanceName" exist
    output = os.popen(cmd).read()
    return bool(output.strip())

def create_ec2(stackName,properties):
    # Description: this function creates a ec2 instance with the name "properties["name"] and linked to stack/resource-group "stackName"
    # Called by: update and create action
    # Output: None
    # Exceptions: None, due the InstanceID is dynamically assigned
    # Returns: None

    #Composing command to run
    instanceType=properties["type"]
    instanceName=properties["name"]

    cmd = "aws ec2 run-instances --image-id ami-0de9f803fcac87f46 --count 1 --instance-type " +  instanceType + " --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=" + instanceName + "},{Key=StackName,Value=" + stackName + "}]'"

    output = os.popen(cmd).read()
    return output

def list_ec2(stackName):
    # Description: this function gets a list of all ec2 instances related with stack/resource-group "stackName"
    # Called by: inventory and exist_ec2
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: a list containing all sc2 InstanceIds related with stack/resource-group "stackName"

    #Composing command to run
    cmd = 'aws ec2 describe-instances --filters "Name=tag:StackName,Values=' + stackName + '" --query "Reservations[].Instances[].[InstanceId]" --output text'

    #Getting the list of all related stack InstanceIds
    output = os.popen(cmd)

    #Formating
    instances = []
    for line in output.readlines():
        if line != "":
            instance_name = line.replace('\n', '')
            instances.append(instance_name)

    #Returning InstanceIds
    return instances

def clean_ec2(stackName):
    # Description: this function deletes all ec2 instances related with stack "stackName"
    # Called by: delete_stack function
    # Output: None
    # Exceptions: should not be raised, due list_ec2 dictionary avoids implicitly deleting non-existing ec2 instances
    # Returns: None

    #Getting ec2 instances to delete
    toDelete = list_ec2(stackName)

    #Deleting ec2 instances one by one. Deletion takes some time
    for instance in toDelete:
        cmd = 'aws ec2 terminate-instances --instance-ids ' + instance
        output = os.popen(cmd).read()

def exist_sqs(sqsName,stackName):
    # Description: this function checks if sqs queue "instanceName" exist on stack/resource-group "stackName"
    # Called by: create action and before create_sqs
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: boolean, meaning "true" the sqs queue "sqsName" exist on stack/resource-group "stackName, false if does not

    #Getting the list of all related stack sqs queues
    sqs_list = list_sqs(stackName)
    #Returning sqs queue names
    return sqsName in sqs_list

def create_sqs(stackName,properties):
    # Description: this function creates a sqs queue with the name "properties["name"] and linked to stack/resource-group "stackName"
    # Called by: update and create action
    # Output: None
    # Exceptions: (QueueAlreadyExists) when calling the CreateQueue operation if the queue already exist or existed 60 seconds before
    # Returns: None

    #Composing command to run
    sqsName=properties["name"]
    cmd = "aws sqs create-queue --queue-name " + sqsName + " --tags StackName=" + stackName + ',Name=' + sqsName + " --output text"

    #Creating SQS queue
    output = os.popen(cmd).readline().strip()

def list_sqs(stackName):
    # Description: this function gets a list of all sqs queues related with stack/resource-group "stackName"
    # Called by: inventory and exist_sqs
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: a list containing all sqs queues related with stack/resource-group "stackName"

    #Composing command to run
    cmd = 'aws resource-groups list-group-resources --group-name ' + stackName + ' --filters Name=resource-type,Values="AWS::SQS::Queue" --output json'

    #Locating resourceArns
    output = os.popen(cmd)

    #Formating
    output_json = json.load(output)
    queues = []
    for item in output_json["ResourceIdentifiers"]:
        queues.append(item["ResourceArn"].split(":")[5])

    #Returning sqs queue names
    return queues

def clean_sqs(stackName):
    # Description: this function deletes all sqs queues related with stack "stackName"
    # Called by: delete_stack function
    # Output: None
    # Exceptions: should not be raised, due list_sqs dictionary avoids implicitly deleting non-existing sqs queues
    # Returns: None

    #Getting sqs queues to delete
    toDelete = list_sqs(stackName)

    #Deleting sqs queues one by one. Deletion should be inmediate, but recreation with the same name needs 60 seconds
    for queue in toDelete:
        get_url_cmd = 'aws sqs get-queue-url --queue-name ' + queue + ' --output text'
        queueurl = os.popen(get_url_cmd).readline().strip()
        delete_cmd = "aws sqs delete-queue --queue-url " + queueurl
        output = os.popen(delete_cmd).readline().strip()

def exist_s3(s3Name,stackName):
    # Description: this function checks if s3 buckets "s3Name" exist on stack/resource-group "stackName"
    # Called by: create action and before create_s3
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: boolean, meaning "true" the s3 bucket s3Name exist on stack/resource-group "stackName, false if does not

    #Getting the list of all related stack s3 buckets
    s3_lists = list_s3(stackName)
    return s3Name in s3_lists

def create_s3(stackName,properties):
    # Description: this function creates a s3 bucket with the name "properties["name"] and linked to stack/resource-group "stackName". System cmd call needed to be split due aws s3 mb does not support tagging
    # Called by: update and create action
    # Output: None
    # Exceptions: (InvalidBucketName) when calling the CreateBucket operation: The specified bucket is not valid. if the bucket name is not correct or the bucket already exist
    # Returns: None

    #Getting the s3 bucket name
    s3Name=properties["bucket-name"]

    #Composing the creation and tagging command
    create_cmd = "aws s3 mb s3://" + s3Name + ' --output text'
    tag_cmd = "aws resourcegroupstaggingapi tag-resources --resource-arn-list arn:aws:s3:::" + s3Name + ' --tags StackName=' + stackName + ',Name=' + s3Name + ' --output text'

    #Creating bucket
    output = os.popen(create_cmd).readline()

    #Tagging bucket
    output = os.popen(tag_cmd).readline()

def list_s3(stackName):
    # Description: this function gets a list of all s3 buckets related with stack/resource-group "stackName"
    # Called by: inventory and exist_s3
    # Output: None
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: a list containing all s3 buckets related with stack/resource-group "stackName"

    #Composing command to run
    cmd = 'aws resource-groups list-group-resources --group-name ' + stackName + ' --filters Name=resource-type,Values="AWS::S3::Bucket" --output json'

    #Locating resourceArns
    output = os.popen(cmd)

    #Formating
    output_json = json.load(output)
    buckets = []
    for item in output_json["ResourceIdentifiers"]:
        buckets.append(item["ResourceArn"].split(":")[5])

    #Returning s3 buckets names
    return buckets

def clean_s3(stackName):
    # Description: this function deletes all s3 buckets related with stack "stackName"
    # Called by: delete_stack function
    # Output: None
    # Exceptions: should not be raised, due list_s3 dictionary avoids implicitly deleting non-existing s3 buckets
    # Returns: None

    #Getting s3 buckets to delete
    toDelete = list_s3(stackName)

    #Deleting s3 buckets one by one. Deletion should be inmediate
    for bucket in toDelete:
        deletecmd = "aws s3 rb s3://" + bucket + ' --force'
        output = os.popen(deletecmd).readline().strip()

def inventory(stackName):
    # Description: this function lists of supported resources related with stack/resource-group "stackName"
    # Called by: inventory action
    # Output: listing all found resources (none if there are no resources)
    # Exceptions: should not be raised, due used functions should not raise errors
    # Returns: None

    #Getting ec2 instances list
    ec2_list = list_ec2(stackName)
    #Printing found ec2 instances (none if there are no instances)
    if ec2_list:
        print("---Action---Inventory: Listing ec2 instances--")
        for instance in ec2_list:
            print("Existing instance: ",instance)

    #Getting sqs queues list
    sqs_list = list_sqs(stackName)
    #Printing found sqs queues (none if there are no queues)
    if sqs_list:
        print("---Action---Inventory: Listing sqs queues--")
        for queue in sqs_list:
            print("Existing queue: ",queue)

    #Getting s3 buckets list
    s3_list = list_s3(stackName)
    #Printing found s3 buckets (none if there are no buckets)
    if s3_list:
        print("---Action---Inventory: Listing s3 buckets--")
        for bucket in s3_list:
            print("Existing buckets: ",bucket)

def json_validation(jsonfilename):
    # Description: this function parsers/checks/validates if the user input json file (acessible by jsonfilename parameter) is compliant with the accepted schema (embedded on schema_data variable)
    # Called by: create and update actions
    # Output: in case of exception
    # Exceptions: reaised if the user json does not follows the schema
    # Returns: None

    # Embedding accepted json schema
    # Schma accepts an array of items, so empty json also are accepted
    schema_data = """
    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "InventoryItem",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": [ "s3", "ec2", "sqs" ]
          },
          "name": {
            "type": "string"
          },
          "properties": {
          }
        },
        "required": ["name", "type", "properties"]
      }
    }
    """
    #Loading embedded validation schema as variable
    schema = json.loads(schema_data)

    #Loading user input json
    with open(jsonfilename, 'r') as json_input_file:
        input_data3 = json_input_file.read()
    input = json.loads(input_data3)

    #Validating input json against embedded schema
    try:
      jsonschema.validate(input, schema)
    except Exception as json_error:
      print(json_error)
      raise ValueError("---Action---Creating and updating: ERROR: json_validation input json not properly set---")
    except:
      print(json_error)
      raise ValueError("---Action---Creating and updating: ERROR: json_validation unknown error---")

# Constructing the argument parser
# the user entered switch (create/update/delete/inventory) with be accessible by "action" key on arguments final dictionay
parser = argparse.ArgumentParser()
sp = parser.add_subparsers(dest='action')

#Creating "create" switch rules, forcing "--stack-name" usage
create_parser = sp.add_parser("create", help="create operand")
create_parser.add_argument("json_file", help="create filename")
create_parser.add_argument("--stack-name", required=True,   help="stack-name to create")

#Creating "update" switch rules, forcing "--stack-name" usage
update_parser = sp.add_parser("update", help="update operand")
update_parser.add_argument("json_file", help="update filename")
update_parser.add_argument("--stack-name", required=True,   help="stack-name to update")

#Creating "delete" switch rules, forcing "--stack-name" usage
delete_parser = sp.add_parser("delete", help="delete operand")
delete_parser.add_argument("--stack-name", required=True,   help="stack-name to delete")

#Creating "inventory" switch rules, forcing "--stack-name" usage
inventory_parser = sp.add_parser("inventory", help="inventory operand")
inventory_parser.add_argument("--stack-name", required=True,   help="stack-name to inventory")

#Making arguments accessible as dictionary
args = vars(parser.parse_args())

#Reading stack name from user input
stackNameFromInput = args["stack_name"]

#Switching by "action" key stored by argument parser previously
if args["action"] == "delete":
    #User requested the stack deletion, no json validation needed
    print("---Action---Deleting")
    if exist_stack(stackNameFromInput):
        delete_stack(stackNameFromInput)
    else:
        print("---Action---Deleting: stack",stackNameFromInput, "does not exist")

elif args["action"] == "inventory":
    #User requested listing the actual custom stack resources, no json validation needed
    print("---Action---Inventory")
    if exist_stack(stackNameFromInput):
        inventory(stackNameFromInput)
    else:
        print("---Action---Inventory: stack",stackNameFromInput, "does not exist")

elif (args["action"] == "create") or (args["action"] == "update"):
# else:
    #User requested listing the actual custom stack resources, no json validation needed
    print("---Action---Creating and updating")

    #Checking json schema
    json_validation(args["json_file"])

    #Creating and updating resources
    json_file = open(args["json_file"],"r")
    input = json.load(json_file)

    #Creating resource-group if does not already exist
    if not exist_stack(stackNameFromInput):
        create_stack(stackNameFromInput)

    for resource in input:

        #Depending of the reource type
        resource_type = resource["type"]

        #The name of the resource is saved on one or another resource sub-item
        #json_validation should avoid any resource_type different than the supported ones
        if (resource_type == "ec2") or (resource_type == "sqs" ):
            resource_name = resource["properties"]["name"]
        elif resource_type == "s3":
            resource_name = resource["properties"]["bucket-name"]
        else:
            #json_validation should avoid arriving here, resource_type different than the supported ones
            raise ValueError("---Action---Creating and updating: ERROR: Resource not supported after json_validation---")

        #Creating dynamically the functions will be called
        exist_resource = 'exist_' + resource_type
        create_resource = 'create_' + resource_type
        list_resource = 'list_' + resource_type

        #Applying the same workflow and checks for all resources, using dynamic calls and "eval" python functionality
        if not eval(exist_resource)(resource_name,stackNameFromInput):
            eval(create_resource)(stackNameFromInput,resource["properties"])
            eval(list_resource)(stackNameFromInput)
        else:
            print("---Action---Creating and updating: ",resource_type," name ",resource_name," already exist")

    #Finally listing the actual state of the stack
    inventory(stackNameFromInput)
else:
    print("---ERROR: Action not supported---")
