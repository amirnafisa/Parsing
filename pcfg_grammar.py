import sys

class PCFG_Rule:
    def __init__ (self, rule_string):
        sub_parts = rule_string.split('\t')
        if len(sub_parts) != 3:
            print("ERR: Incorrect rule - ",rule_string)
            return False

        self._lhs = sub_parts[1]
        self._rhs = sub_parts[2].split(' ')
        self._prob = float(sub_parts[0])

    def get_lhs(self):
        return self._lhs

    def get_rhs(self):
        return self._rhs

    def get_prob(self):
        return self._prob

    def print_rule(self):
        print("Rule: ",self._lhs," => ",','.join(self._rhs)," [",self._prob,"]",sep='')

class PCFG_Grammar:
    def __init__ (self, grammar_file):
        self.gr_file = grammar_file
        self._gr = {}
        self._NT = set()
        self._T = set()
        self._syms = set()
        with open(grammar_file, 'r') as f_gr:
            for line in f_gr:
                rule = PCFG_Rule(line.strip())

                lhs = rule.get_lhs()

                rhs = rule.get_rhs()
                if lhs not in self._gr:
                    self._gr[lhs] = []
                self._gr[lhs].append(rule)
                self._NT.add(lhs)
                self._syms.update(rhs)
        self._T = self._syms - self._NT

    def get_non_terminals(self):
        return self._NT

    def get_terminals(self):
        return self._T

    def get_rules(self, non_terminal):
        if non_terminal in self._NT:
            return self._gr[non_terminal]
        else:
            print("ERR: NonTerminal",non_terminal,"does not exist in the grammar")
            return False

    def print_grammar(self):
        print("Grammar ",self.gr_file,": ",sep='')
        for non_terminal, rules in self._gr.items():
            for rule in rules:
                rule.print_rule()

def demo_pcfg(grammar_file):
    gr = PCFG_Grammar(grammar_file)

    print("List of Non Terminals in the grammar: ",gr.get_non_terminals())
    print("List of Terminals in the grammar: ",gr.get_terminals())
    gr.print_grammar()
