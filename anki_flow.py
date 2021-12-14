import secrets

def equip_with_uid(latex_str):
    latex_lines = latex_str.splitlines()

    card_identifier = "\\ankiCard{"
    n = len(card_identifier)
    for i, line in enumerate(latex_lines):
        pos = line.find(card_identifier)
        if pos != -1:
            uid = secrets.token_urlsafe(16)
            latex_lines[i] = line[:pos+n-1] + "[" + uid + "]" + line[pos+n-1:]

    return '\n'.join(latex_lines)


latex_str = """\\ankiCard{Theorem}{01.01}{
  This is a trivial front.
}{
  This is a trivial back.
}
"""

print(equip_with_uid(latex_str))
