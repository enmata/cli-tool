## cli-tool

### Abstract
This document tries to explain the workflow and usage of the cli-tool.
cli-tool is a python script that manages custom AWS stacks. That custom stacks are using "Tag based" group-resources, avoiding "CloudFormation" stacks and "CloudFormation stack based" group-resources.
The script is able to create, update and delete custom stacks, identifying which resources belong to the stack based on tags custom "StackName" tags.
Supports ec2 instances, sqs queues and s3 buckets, based on an entering json array.

### Tools and libraries
The following tools has been used:
- python 3.7.3
- aws-cli/1.19.26 (AWS personal account)
- awscli-local/0.13 (localstack)
- python pip modules (and it's dependencies)
        - json         # input/output formatting for aws cli and user inputs
        - os           # reading files and aws cli system calls process managing
        - subprocess   # aws cli system calls process managing
        - argparse     # user input parameters parsing, management and restrictions
        - jsonschema   # user input json validation

### cli-tool usage
cli-tool is accepting the following actions/parameters:

- **create <json_input_file.json> --stack-name <stack_name>**
    creates a new custom stack, based on json input parameter, setting <stack_name> as a resource-group name and as a stackName
    example:
        *python cli-tool.py create input_ec2_multiple.json --stack-name ec2_only_stack*

- **update <json_input_file.json> --stack-name <stack_name>**
    creates an existing stack, based on json input parameters, using <stack_name> for locating the resource-group/stackName
    example:
        *python cli-tool.py update input_sqs_alone.json --stack-name sqs_queues_stack*

- **delete --stack-name <stack_name>**
    deletes all resources linked to the custom stack <stack_name> and the resource-group
    example:
        *python cli-tool.py delete --stack-name stack_to_delete*

- **inventory --stack-name <stack_name>**
    lists all the existing resources linked to the custom stack <stack_name>
    example:
        *python cli-tool.py inventory --stack-name stack_for_listing*

- **-h**
    basic usage help
    example:
        *python cli-tool.py -h*

**Additional notes:**  detailed information about each individual defined function is explained on different comments of each individual function on the python file.

### Suported resources
The following resources are supported on custom stack
- ec2 instances     https://docs.aws.amazon.com/cli/latest/reference/ec2/
- sqs queues        https://docs.aws.amazon.com/cli/latest/reference/sqs/
- s3 buckets        https://docs.aws.amazon.com/cli/latest/reference/s3/

### Folder structure
Files and scripts has been distributed as follows:
```
├── cli-tool.py     # Python-based cli-tool
├── Readme.rd       # cli-tool documentation
├── input_tests     # Folder containing tiffernt json array test files used during application testing
```

### Assumptions, requirements and considerations
- cli-tool is assuming:
--- python 3 is installed on the environment
--- aws cli SDK is installed on the environment
--- AWS credentials account is set up for amazon web services, with rights to create resource groups, ec2 instances, sqs queues and s3 buckets
--- any operating system with python, the listed pip requirements and aws sdk installed should be able to run the cli
- Whats makes a resource (an ec2 instance, an sqs queue or an s3 buckets) is making he proper "StackName" tag.
--- If one resource has these tag, is considered part of the custom stack.
--- If a resource containing these tag is deleted, is only recreated if "create" of "update" operations are running again
-Update operation is not a destructive action. If a previously created resource does not exist on the new json, this resource is not deleted.
- cli-tool does not have support for direct editing existing resources. A "delete" and "create" is needed, destroying previous resources.
- Time delay between executions: recreation (delete and create) of some specific resources with the same name needs some time between executions. I avoided introducing unnecessary "sleeps" between runs, introducing raise conditions.
--- deleting resources like EC2 instances (*aws ec2 terminate-instances*) is not immediate action. Some minutes are needed to be able to completely delete the instance. If we try before some minutes, we could get wrong results listing ghost existing instances.
--- sqs queues need 60 seconds between creation a delete and re-creation if the same name is used. aws cli raises an exception if we try to do it before that time.

### Technical desisions
- Discarted usage of cli skeleton
  Most of aws cli commands accepts json input/output files
  Example:
    _aws ec2 run-instances --cli-input-json file://ec2runinst.json_
    _aws ec2 run-instances --generate-cli-skeleton_
    https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-skeleton.html
    User input json strucure is quite different from cli skeleton specification, so I used the regular entering parameter method.

- Resource-group usage based on tags
    Some resources (like sqs queues and s3 buckets) are not easy to locate only using aws cli and tags.
    Tag based resource-groupss ("Type": "TAG_FILTERS_1_0") helps for tag managing, grouping and locating that resources.
    Using tags is also an easy option to manage and identify the resources belonging to that stack than for instance adding a prefix/suffix on the resource name.

- python eval dynamic function calling and the same funcion name for all resources
  Every kind of resource has _"exist"_, _"create_"_, "list_" and "clean_" functions to manage it, with the same parameters.
  In order to make a make a better code,  avoiding cloning if/else cases, dynamic function calls using the python "eval" functionality has been used.

- System calls using "subprocess.call(cmd)" vs using "os.popen(cmd)"
    Some commands containing brackets ({}) are not properly executed using the regular "os.popen(cmd)". For these specific calls (on "create_stack" and "delete_stack") has been done by using the "subprocess.call(cmd)" function.

- Setting "AWS_DEFAULT_OUTPUT" value to "json" to avoid "Unknown output type: yaml" errors when using old "aws cli" version (<v2).

- Creating additional action "inventory"
        - Created for debuging propouses, reusing all "list_" already defined functions

### Parsing parameters
- For **command line parameters** -> using argparse python standard library
        - parameters needs to follow the order *<action_name> <file_name> (if needed) --stack-name <stack_name>*
        - all actions (create/update/delete/inventory) needs "- -stack-name" parameter
        - jsonfile path is needed for running "create" and "update" actions
- For **json file** -> using python jsonschema validation
        - A json schema validation is done before any creation or update. If the json entered by the used is not compliance with the embedded schema in "json_validation" funcion, an exception error is raised.
            Example: _jsonschema.exceptions.ValidationError: 's3WRONG' is not one of ['s3', 'ec2', 'sqs']_
        - 3 child items on each resource are needed to be specified: "name", "type" and "properties"
        - json file is loaded as an array, so claudators are needed for json file content

### Known errors and exceptions

- **Custom raise exception: ValueError("---Action---Creating and updating: ERROR: json_validation input json not properly set---")**
        - **From:** json_validation function
        - Exception raised from inside json_validation function if the user input json is not compliance with the schema

- **Custom raise exception: ValueError("---Action---reating and updating: ERROR: json_validation unknown error---")**
        - **From:** json_validation function
        - Exception raised from inside json_validation function for unknown error during json schema validation

- **Custom raise exception: ValueError("---Action---Creating and updating: ERROR: Resource not supported after json_validation---")**
        - **From:** Main
        - Exception raised if the user is trying to create a resource different than ec2, sqs or s3
        This case should never happens, json_validation should avoid arriving here

- **QueueDeletedRecently: Creating SQS queue before 60 seconds**
        - From: create_sqs function
        - Example: _An error occurred (AWS.SimpleQueueService.QueueDeletedRecently) when calling the CreateQueue operation: You must wait 60 seconds after deleting a queue before you can create another with the same name._

- **Invalid bucket name**: bucket name needs to be unique and name cannot contain underscore "_" simbols
        https://docs.aws.amazon.com/AmazonS3/latest/userguide/BucketRestrictions.html
        - **From:** create_s3
        - Example: _make_bucket failed: s3://my-bucket-name_new921 An error occurred (InvalidBucketName) when calling the CreateBucket operation: The specified bucket is not valid._

- **EC2 instance appears after deletion**
    Deleting EC2 instances (aws ec2 terminate-instances) is not immediate action. AWS cli is returning an existing instance after some minutes after termination.
    https://docs.aws.amazon.com/AWSEC2/latest/WindowsGuide/terminating-instances.html

### Testing

- All mentioned actions has been tested:
        - using official awscli/1.19.26 with a AWS personal account
        - using localstack and awscli-local/0.13 against a local docker container
        - cases listed on input_tests folder (solo/combined resources, alone/multiple instances, etc...)

- Specific corner cases tested:
        - Checked not interfering the value of system variable "AWS_DEFAULT_OUTPUT", due " - - output" set on all needed commands
        - empties array json file ([])
        - "delete" action executed multiple times
        - inventorying non-existing stacks
        - no resource changes after running "update" the same json specification
        - mentioned exceptions on "Known errors and exceptions" section
        - non supported resource types on json (schema validation)

### Possible upgrades and alternatives
- Add support more resource types (APIGateway, VPC, DynamoDB, etc...)
    https://docs.aws.amazon.com/ARG/latest/userguide/supported-resources.html
- manage system call exit codes
- verbose switch for debugging purposes
- Interactive version with user interaction
- parameter for switching between amazon "aws cli" and localstack "awslocal" environments/command
- Deeper json schema validation, depending of the resource (["properties"]["name"] vs ["properties"]["bucket-name"])
- avoid group-resource usage using REST API/request pip module api calls for resources management
    https://docs.aws.amazon.com/index.html
- boto3 usage for a native aws python management
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/examples.html
- add support for updating live individual resources
    https://docs.aws.amazon.com/cli/latest/reference/s3api/index.html#cli-aws-s3api
