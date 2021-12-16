from pylatexenc import latexwalker, macrospec

def get_anki_context_db():
    anki_context_db = latexwalker.get_default_latex_context_db()
    anki_context_db.add_context_category(
        'anki',
        prepend=True,
        macros=[
            macrospec.MacroSpec("ankiCard", args_parser = '[{{{{')
        ],
    )
    return anki_context_db
