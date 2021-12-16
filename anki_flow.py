import argparse
import os

from anki_preprocess import *
from anki_parser import *
from anki_l2t import *

# create argparser
parser = argparse.ArgumentParser()

parser.add_argument('file_in', type=str,
                    help='The input file')
parser.add_argument('file_out', type=str, nargs='?',
                    help='The (optional) output file')

args = parser.parse_args()

if args.file_out == None:
    args.file_out = os.path.splitext(args.file_in)[0] + ".txt"

# read in file
with open(args.file_in) as file:
    latex_lines = file.readlines()

# preprocess
latex_lines = equip_with_uid(latex_lines)

with open(args.file_in, "w") as file:
    file.write(''.join(latex_lines))

latex_str = '\n'.join([line.strip() for line in latex_lines])

# print(latex_str)
# print('\n' * 1)

# parse data
parser = latexwalker.LatexWalker(latex_str, latex_context=get_anki_context_db())
nodes,_,_ = parser.get_latex_nodes(pos=0)

# convert ankiCard nodes to anki lines
l2t = get_anki_l2t()

out_lines = []
for node in nodes:
    if node.isNodeType(latexwalker.LatexCommentNode):
        print("\n" + node.latex_verbatim().strip())
    if node.isNodeType(latexwalker.LatexMacroNode) and node.macroname == 'ankiCard':
        line = l2t.nodelist_to_text([node])
        print(line)
        out_lines.append(line)

with open(args.file_out, "w") as file:
    file.write('\n'.join(out_lines))
