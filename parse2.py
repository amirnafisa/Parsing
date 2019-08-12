from pcfg_grammar import *
from sentence import *
from speedup import *
import sys

class ELYEntry:
    def __init__ (self, rule, ely_col, lookup_col, id):
        self._rule = rule
        self._dot = 0
        self._score = 0
        self._ely_col = ely_col
        self._lookup_col = lookup_col
        self._id = id
        self._bktrack = ['' for _ in range(len(rule.get_rhs()))]
        self._is_completed = False

    def set_dot_idx(self, dot_idx):
        self._dot = dot_idx
        if dot_idx == len(self._rule.get_rhs()):
            self._is_completed = True

    def get_dot_idx(self):
        return self._dot

    def add_bktrack(self, entry, bktrack_id):
        rhs_idx = entry.get_dot_idx()
        prior_bktrack = entry.get_bktrack()
        for i in range(rhs_idx):
            self._bktrack[i] = prior_bktrack[i]
        self._bktrack[rhs_idx] = bktrack_id

    def get_bktrack(self):
        return self._bktrack

    def get_id(self):
        return self._id

    def set_id(self, id):
        self._id = id

    def get_rule(self):
        return self._rule

    def get_next_rhs(self):
        rhs = self._rule.get_rhs()
        if self._dot >= len(rhs):
            return None
        return rhs[self._dot]

    def get_col_idx(self):
        return self._ely_col

    def set_completed(self):
        self._is_completed = True

    def is_completed(self):
        return self._is_completed

    def get_lookup_col_idx(self):
        return self._lookup_col

    def get_score(self):
        return self._score

    def add_score_by(self, score):
        self._score += score

class ELYColumn:
    def __init__ (self, id):
        self._id = id
        self._rules = []
        self._entries = []

    def add_entry (self, entry):
        idx = self.entry_exists(entry)

        if idx == -1:
            self._rules.append([entry.get_rule(), entry.get_dot_idx(), entry.get_lookup_col_idx()])
            self._entries.append(entry)
            return 1
        elif self._entries[idx].get_score() < entry.get_score():
            return -1
        else:
            return_cur_id = entry.get_id()
            entry.set_id(self._entries[idx].get_id())
            self._entries[idx] = entry
            return 0

    def get_id(self):
        return self._id

    def entry_exists(self, entry):
        idx = -1
        if [entry.get_rule(), entry.get_dot_idx(), entry.get_lookup_col_idx()] in self._rules:
            idx = self._rules.index([entry.get_rule(), entry.get_dot_idx(), entry.get_lookup_col_idx()])
        return idx

    def get_entry (self, idx):
        if idx >= len(self._entries):
            return None
        return self._entries[idx]

    class iterate_column:
        def __init__ (self, super_self):
            self.cur_entry_idx = 0
            self.super_self = super_self
        def next(self):
            next_entry = self.super_self.get_entry(self.cur_entry_idx)
            self.cur_entry_idx += 1
            return next_entry

class ELYChart:
    def __init__ (self, tokens, gr, speedup):
        self._cur_col_idx = 0
        self._cur_entry_id = 0
        self._cur_col = ELYColumn(self._cur_col_idx)
        self._ELY = [self._cur_col]
        self._nELY = {}
        self._n_cols = 1
        self._root = 'ROOT'
        self._tokens = tokens
        self._gr = gr
        self.speedup = speedup
        self.RTable, self.LAncestorTable = {}, {}
        if speedup:
            filter_grammar(self._gr, self._tokens)
            self.RTable = extract_R_table(self._gr)
            self.LAncestorTable = extract_left_ancestor_table(self._gr, extract_left_parent_table(self._gr))

        self.predict(self._root)

    def get_current_token (self):
        if self._cur_col_idx < len(self._tokens):
            return self._tokens[self._cur_col_idx]
        return None

    def add_entry(self, entry, column):
        ret = column.add_entry(entry)
        if ret == 1:
            self._nELY[self._cur_entry_id] = entry
            self._cur_entry_id += 1
        elif ret == 0:
            self._nELY[entry.get_id()] = entry


    def predict(self, token):
        if self.speedup and token in self.LAncestorTable:
            for rhs in self.LAncestorTable[token]:
                for rule in self.RTable[(token,rhs)]:
                    new_entry = ELYEntry(rule, self._cur_col_idx, self._cur_col_idx, self._cur_entry_id)
                    new_entry.add_score_by(rule.get_score())
                    self.add_entry(new_entry, self._cur_col)
        else:
            for rule in self._gr.get_rules(token):
                new_entry = ELYEntry(rule, self._cur_col_idx, self._cur_col_idx, self._cur_entry_id)
                new_entry.add_score_by(rule.get_score())
                self.add_entry(new_entry, self._cur_col)

    def scan (self, entry):
        this_token = entry.get_next_rhs()
        if not this_token:
            return None
        if this_token == self.get_current_token():
            if self._cur_col_idx + 1 >= self._n_cols:
                self._ELY.append(ELYColumn(self._cur_col_idx + 1))
                self._n_cols += 1
            new_col = self._ELY[self._cur_col_idx + 1]

            new_entry = ELYEntry(entry.get_rule(), self._cur_col_idx + 1, entry.get_lookup_col_idx(), self._cur_entry_id)
            new_entry.add_score_by(entry.get_rule().get_score())
            new_entry.set_dot_idx(entry.get_dot_idx()+1)
            new_entry.add_bktrack(entry, None)

            self.add_entry(new_entry, new_col)

    def complete (self, completed_entry):
        lookup_token = completed_entry.get_rule().get_lhs()
        lookup_col = completed_entry.get_lookup_col_idx()
        iter = self._ELY[lookup_col].iterate_column(self._ELY[lookup_col])
        entry = iter.next()
        while(entry):
            if not entry.is_completed():
                if entry.get_next_rhs() == lookup_token:
                    entry_lookup_col = entry.get_lookup_col_idx()
                    new_entry = ELYEntry(entry.get_rule(), self._cur_col_idx, entry_lookup_col, self._cur_entry_id)
                    new_score = entry.get_score()+completed_entry.get_score()
                    new_entry.set_dot_idx(entry.get_dot_idx()+1)
                    new_entry.add_bktrack(entry, completed_entry.get_id())
                    new_entry.add_score_by(new_score)
                    discard = False
                    if self.speedup:
                        discard = do_discard(self._cur_col_idx-entry_lookup_col, new_score)
                    if not discard:
                        self.add_entry(new_entry, self._cur_col)

            entry = iter.next()

    def get_chart (self):
        return self._ELY

    def get_column(self, col_idx):
        return self._ELY[col_idx]

    def set_cur_col_idx(self, col_idx):
        self._cur_col_idx = col_idx
        self._cur_col = self._ELY[col_idx]

    def get_cur_col_idx(self):
        return self._cur_col_idx

    def print_chart (self):
        print("Printing Chart")
        for col in range(self._n_cols):
            print("Column",col,":")
            iter = self._ELY[col].iterate_column(self._ELY[col])
            entry = iter.next()
            while(entry):
                print("Entry ID",entry.get_id()," Lookup ID",entry.get_lookup_col_idx(),":",entry.get_rule().get_lhs(),end='\t->\t')
                rhs = entry.get_rule().get_rhs()
                bktrack = entry.get_bktrack()
                for k in range(len(rhs)):
                    if k==entry.get_dot_idx():
                        print('.', end='')
                    print(rhs[k]+' - '+str(bktrack[k]),sep=' ',end=' ')
                print('\t',entry.get_score())
                entry = iter.next()

    def print_parse (self):
        def recurse_print(id):
            if id not in self._nELY:
                return ""
            entry = self._nELY[id]
            rhses = entry.get_rule().get_rhs()
            output_str = ''
            for rhs, bktrk in zip(rhses, entry.get_bktrack()):
                if bktrk:
                    output_str += '('
                output_str += rhs
                output_str += ' '
                output_str += recurse_print(bktrk)
                if bktrk:
                    output_str += ')'

            return output_str

        iter = self._cur_col.iterate_column(self._cur_col)
        entry = iter.next()
        while(entry):
            if entry.get_rule().get_lhs() == 'ROOT':
                output_str = '( ROOT '
                output_str += recurse_print(entry.get_id())
                output_str += ')'
                return output_str

            entry = iter.next()
        return None


def parse_sen(pcfg_gram, sen2parse, send_end = None, speedup=True):


    myELYChart = ELYChart(sen2parse.get_tokens(),pcfg_gram, speedup)
    for i in range(len(sen2parse.get_tokens())+1):
        if myELYChart.get_current_token() not in pcfg_gram.get_terminals():
            return ''
        myELYChart.set_cur_col_idx(i)
        worker_column = myELYChart.get_column(i)
        prev_predicted_NT = set()
        iter = worker_column.iterate_column(worker_column)
        ely_entry = iter.next()
        while(ely_entry):
            if ely_entry.is_completed():
                myELYChart.complete(ely_entry)
            elif i < len(sen2parse.get_tokens()):
                next_token = ely_entry.get_next_rhs()
                if next_token in pcfg_gram.get_non_terminals():
                    if next_token not in prev_predicted_NT:
                        myELYChart.predict(next_token)
                        prev_predicted_NT.add(next_token)
                else:
                    myELYChart.scan(ely_entry)
            ely_entry = iter.next()

    output_str = myELYChart.print_parse()
    if send_end:
        send_end.send(output_str)

    return output_str

if __name__ == '__main__':

    pcfg_gram = PCFG_Grammar(sys.argv[1])
    sen2parse = Sentence(sys.argv[2])

    output_str = parse_sen (pcfg_gram, sen2parse, speedup=True)
    print(output_str)
