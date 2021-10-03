import argparse

# Construct the argument parser
parser = argparse.ArgumentParser()
sp = parser.add_subparsers()

#Creating "create" arg rules
create_parser = sp.add_parser("create", help="create operand")
create_parser.add_argument("create_json_file", help="create json filename")
create_parser.add_argument("--stack-name", required=True, help="stack-name to create")

#Creating "update" arg rules
update_parser = sp.add_parser("update", help="update operand")
update_parser.add_argument("update_json_file", help="update json filename")
update_parser.add_argument("--stack-name", required=True, help="stack-name to update")

#Creating "delete" arg rules
delete_parser = sp.add_parser("delete", help="delete operand")
delete_parser.add_argument("--stack-name", required=True, help="stack-name to delete")

args = parser.parse_args()

print(args.__class__)
print(args)
