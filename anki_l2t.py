from pylatexenc import latex2text, macrospec, latexwalker
from pylatexenc.latex2text import _PushEquationContext

import re

class EnumContext:
    def __init__(self, env=None, nest_level=0, item_no=0):
        self.env = env
        self.nest_level = nest_level
        self.item_no = item_no

def enum_environment_to_text(n, l2tobj):
    if n.environmentname not in ("enumerate", "itemize"):
        raise RuntimeError("environment was expected to be enumerate or itemize")
    try:
        old_context = getattr(l2tobj, 'context_enum_environment', EnumContext())
        l2tobj.context_enum_environment = EnumContext(n.environmentname, old_context.nest_level+1, 0)
        s = l2tobj.nodelist_to_text(n.nodelist)
    finally:
        l2tobj.context_enum_environment = old_context
    delims = ('<ul>', '</li></ul>') if n.environmentname == "itemize" else ('<ol>', '</li></ol>')
    return delims[0] + s.strip() + delims[1]

def item_to_text(n, l2tobj):
    enumcontext = getattr(l2tobj, 'context_enum_environment', EnumContext())
    s = '</li><li>' if enumcontext.item_no != 0 else '<li>'
    enumcontext.item_no += 1
    return s
    # if n.nodeoptarg:
    #     itemstr = l2tobj.nodelist_to_text([n.nodeoptarg])
    # if enumcontext.env == 'itemize':
    #     itemstr = '- '
    # elif enumcontext.env == 'enumerate':
    #     enumcontext.item_no += 1
    #     itemstr = str(enumcontext.item_no) + '. '
    # else:
    #     itemstr = '* ' # \item not in \begin{enumerate} or \begin{itemize} environment
    # return '\n' + '  '*enumcontext.nest_level + itemstr

def math_node_to_text(self, node):
    r"""
    Return the textual representation of the given `node` representing a block
    of math mode latex.  The `node` is either a
    :py:class:`~pylatexenc.latexwalker.LatexMathNode` or a
    :py:class:`~pylatexenc.latexwalker.LatexEnvironmentNode`.
    This method is responsible for honoring the `math_mode=...` option
    provided to the constructor.
    """

    if self.math_mode == 'verbatim':
        if node.isNodeType(latexwalker.LatexEnvironmentNode) \
           or node.displaytype == 'display':
            return self._fmt_indented_block(node.latex_verbatim(), indent='')
        else:
            return node.latex_verbatim()

    elif self.math_mode == 'remove':
        return ''

    elif self.math_mode == 'with-delimiters':
        with _PushEquationContext(self):
            delims = node.delimiters if node.isNodeType(latexwalker.LatexMathNode) else (r'\begin{%s}' % (node.environmentname), r'\end{%s}' % (node.environmentname))
            content_lines = node.latex_verbatim()[len(delims[0]):-len(delims[1])].splitlines()
            content = ' '.join([line for line in content_lines if line.strip() != ''])
            # content = self.nodelist_to_text(node.nodelist).strip()
        if node.isNodeType(latexwalker.LatexMathNode):
            delims = ('\(', '\)')
            # delims = node.delimiters
        else: # environment node
            delims = ('\[', '\]')
            # delims = (r'\begin{%s}'%(node.environmentname),
            #           r'\end{%s}'%(node.environmentname),)
        # if node.isNodeType(latexwalker.LatexEnvironmentNode) \
        #    or node.displaytype == 'display':
        #     return delims[0] + self._fmt_indented_block(content, indent='') + delims[1]
        # else:
        #     return delims[0] + content + delims[1]
        return delims[0] + content + delims[1]

    elif self.math_mode == 'text':
        with _PushEquationContext(self):
            content = self.nodelist_to_text(node.nodelist).strip()
        if node.isNodeType(latexwalker.LatexEnvironmentNode) \
           or node.displaytype == 'display':
            return self._fmt_indented_block(content)
        else:
            return content

    else:
        raise RuntimeError("unknown math_mode={} !".format(self.math_mode))

def chars_node_to_text(self, node, textcol=0):

    content = re.sub('\n\n(\n)*', " <br> ", node.chars)
    content = re.sub('\n', " ", content)
    if self.fill_text: # None or column width
        content = self.do_fill_text(content, textcol=textcol)
    if not self.strict_latex_spaces['between-latex-constructs'] \
       and len(content.strip()) == 0:
        return ""
    return content

def newline_to_text(n, l2tobj):
    return "<br>"

def anki_card_to_text(n, l2tobj):
    return '\t'.join(list(map(lambda x:l2tobj.nodelist_to_text([x]).strip(), n.nodeargd.argnlist)))

def textbf_to_text(n, l2tobj):
    return "<b>" + l2tobj.nodelist_to_text(n.nodeargd.argnlist).strip() + "</b>"

def get_anki_l2t():
    l2t_db = latex2text.get_default_latex_context_db()
    l2t_db.add_context_category(
        'anki-cards',
        prepend=True,
        macros=[
            latex2text.MacroTextSpec('ankiCard', simplify_repl=anki_card_to_text),
            latex2text.MacroTextSpec('\\', simplify_repl=newline_to_text),
            latex2text.MacroTextSpec('item', simplify_repl=item_to_text),
            latex2text.MacroTextSpec('textbf', simplify_repl=textbf_to_text),
        ],
        environments=[
            latex2text.EnvironmentTextSpec('enumerate', simplify_repl=enum_environment_to_text),
            latex2text.EnvironmentTextSpec('itemize', simplify_repl=enum_environment_to_text),
        ],
    )

    # monkey patch
    latex2text.LatexNodes2Text.chars_node_to_text = chars_node_to_text
    latex2text.LatexNodes2Text.math_node_to_text = math_node_to_text

    # create l2t object
    return latex2text.LatexNodes2Text(latex_context=l2t_db, math_mode='with-delimiters')
