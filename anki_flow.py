import argparse
import re
import os

parser = argparse.ArgumentParser()
parser.add_argument('file_in', type=str,
                    help='The input file')
parser.add_argument('file_out', type=str, nargs='?',
                    help='The (optional) output file')

args = parser.parse_args()

with open(args.file_in) as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

if args.file_out == None:
    args.file_out = os.path.splitext(args.file_in)[0] + "_out.txt"

# Get indices to add unique identifiers
uid_indices = []
for i, line in enumerate(lines):
    if line == '----- Type':
        if i == 0:
            uid_indices.append(i)
        elif i == 1:
            print("This shouldn't happen.")
        else:
            if lines[i-2] != '----- Unique Id':
                uid_indices.append(i)

# Add unique identifiers
for i, uid_index in enumerate(uid_indices):
    lines.insert(uid_index + 2*i, "RANDOM_GIBBERISH")
    lines.insert(uid_index + 2*i, "----- Unique Id")

# print(lines)
# print('\n'.join(lines))

cards = []
fields = []
components = []
for line in lines:
    if not line.startswith('-----'):
        if line != '':
            components.append(line)
    else:
        fields.append(' '.join(components))
        components = []
        if line.startswith('----- Unique Id'):
            cards.append('	'.join(fields))
            fields = []

fields.append(' '.join(components))
cards.append('	'.join(fields))

with open(args.file_in, "w") as file:
    file.write('\n'.join(lines))

with open(args.file_out, "w") as file:
    file.write('\n'.join(cards[1:]))
