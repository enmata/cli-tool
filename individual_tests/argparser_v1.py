import argparse

# Construct the argument parser
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)

# Add the arguments to the parser
group.add_argument("-c", "--create", help="create operand")
group.add_argument("-u", "--update", help="update operand")
#group.add_argument("-d", "--delete", help="delete operand")
parser.add_argument("-sn", "--stack-name", required=True,   help="stack-name operand")
#args = vars(parser.parse_args())
args = parser.parse_args()

print(args.__class__)
print(args)

# Calculate the sum
#print("create is ".format(int(args['create'])))
#print(args['update'])
#print("delete is ".format(int(args['delete'])))
#print("stack-name is ".format(int(args['stack-name'])))
