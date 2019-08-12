
import sys
def filter_grammar(gr, tokens):
    unused_term = gr.get_terminals() - set(tokens)
    gr.remove_terminals(unused_term)

def do_discard(n_tokens, score):
    if (score > n_tokens*13):
        return True
    return False

def extract_R_table(gr):
    RTable = {}
    non_terminals = gr.get_non_terminals()
    for non_term in non_terminals:
        rules = gr.get_rules(non_term)
        for rule in rules:
            key = (rule.get_lhs(), rule.get_rhs()[0])
            if key not in RTable:
                RTable[key] = set()

            RTable[key].add(rule)

    return RTable

def extract_left_parent_table(gr):
    LParentTable = {}

    non_terminals = gr.get_non_terminals()
    for non_term in non_terminals:
        rules = gr.get_rules(non_term)
        for rule in rules:
            key = rule.get_rhs()[0]
            if key not in LParentTable:
                LParentTable[key] = set()
            LParentTable[key].add(rule.get_lhs())

    return LParentTable


def extract_left_ancestor_table(gr, LParentTable):
    LAncestorTable = {}
    prev_looked_at = set()
    def recurse(non_term):
        if non_term not in LParentTable:
            return -1
        for nt in LParentTable[non_term]:
            if nt not in LAncestorTable:
                LAncestorTable[nt] = set()
            LAncestorTable[nt].add(non_term)
            prev_looked_at.add(non_term)
            if nt not in prev_looked_at:
                recurse(nt)

    for terminal in gr.get_terminals():
        for non_term in LParentTable[terminal]:
            if non_term not in LAncestorTable:
                LAncestorTable[non_term] = set()
            LAncestorTable[non_term].add(terminal)
            prev_looked_at.add(terminal)
            if non_term not in prev_looked_at:
                recurse(non_term)

    return LAncestorTable
