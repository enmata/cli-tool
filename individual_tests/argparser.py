import argparse

# Construct the argument parser
parser = argparse.ArgumentParser()
sp = parser.add_subparsers(dest='action')

#Creating "create" arg rules
create_parser = sp.add_parser("create", help="create operand")
create_parser.add_argument("json_file", help="create filename")
create_parser.add_argument("--stack-name", required=True,   help="stack-name to create")

#Creating "update" arg rules
update_parser = sp.add_parser("update", help="update operand")
update_parser.add_argument("json_file", help="update filename")
update_parser.add_argument("--stack-name", required=True,   help="stack-name to update")

#Creating "delete" arg rules
delete_parser = sp.add_parser("delete", help="delete operand")
delete_parser.add_argument("--stack-name", required=True,   help="stack-name to delete")

#Creating "delete" arg rules
inventory_parser = sp.add_parser("inventory", help="delete operand")
inventory_parser.add_argument("--stack-name", required=True,   help="stack-name to inventory")


args = vars(parser.parse_args())

print(args)

if args["action"] == "delete":
    print("deleting")
    print(args["stack_name"])
elif args["action"] == "inventory":
    print("inventory")
    print(args["stack_name"])
else:
    print("creating and updating")
    print(args["json_file"])
    print(args["stack_name"])
