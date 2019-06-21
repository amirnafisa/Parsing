from pcfg_grammar import *
from sentence import *

class ELYEntry:
    def __init__ (self, rule, ely_col, lookup_col, id):
        self._rule = rule
        self._dot = 0
        self._ely_col = ely_col
        self._lookup_col = lookup_col
        self._id = id
        self._bktrack = ['' for _ in range(len(rule.get_rhs()))]
        self._is_completed = False

    def set_dot_idx(self, dot_idx):
        self._dot = dot_idx

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

class ELYColumn:
    def __init__ (self, id):
        self._id = id
        self._rules = []
        self._entries = []

    def add_entry (self, entry):
        if not self.entry_exists(entry):
            self._rules.append([entry.get_rule(), entry.get_dot_idx()])
            self._entries.append(entry)
            return entry.get_id() + 1


        return entry.get_id()

    def entry_exists(self, entry):
        if [entry.get_rule(), entry.get_dot_idx()] in self._rules:
            return True
        return False

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
    def __init__ (self, tokens, gr):
        self._cur_col_idx = 0
        self._cur_entry_id = 0
        self._cur_col = ELYColumn(self._cur_col_idx)
        self._ELY = [self._cur_col]
        self._nELY = {}
        self._n_cols = 1
        self._root = 'ROOT'
        self._tokens = tokens
        self._gr = gr
        self.predict(self._root)


    def get_current_token (self):
        return self._tokens[self._cur_col_idx]

    def predict(self, token):
        for rule in self._gr.get_rules(token):
            entry = ELYEntry(rule, self._cur_col_idx, self._cur_col_idx, self._cur_entry_id)
            self._cur_entry_id = self._cur_col.add_entry(entry)
            prev_id = self._cur_entry_id
            if self._cur_entry_id != prev_id:
                self._nELY[prev_id] = new_entry

    def scan (self, entry):
        this_token = entry.get_next_rhs()
        if not this_token:
            return None
        if this_token == self.get_current_token():
            if self._cur_col_idx + 1 >= self._n_cols:
                new_col = ELYColumn(self._cur_col_idx + 1)
                self._n_cols += 1
                self._ELY.append(new_col)

            new_entry = ELYEntry(entry.get_rule(), self._cur_col_idx + 1, entry.get_lookup_col_idx(), self._cur_entry_id)
            new_entry.set_dot_idx(entry.get_dot_idx()+1)
            if new_entry.get_dot_idx() == len(new_entry.get_rule().get_rhs()):
                new_entry.set_completed()
            prev_id = self._cur_entry_id
            self._cur_entry_id = self._ELY[self._cur_col_idx + 1].add_entry(new_entry)
            if self._cur_entry_id != prev_id:
                self._nELY[prev_id] = new_entry

    def complete (self, completed_entry):
        lookup_token = completed_entry.get_rule().get_lhs()
        lookup_col = completed_entry.get_lookup_col_idx()
        iter = self._ELY[lookup_col].iterate_column(self._ELY[lookup_col])
        entry = iter.next()
        while(entry):
            if not entry.is_completed():
                if entry.get_next_rhs() == lookup_token:
                    new_entry = ELYEntry(entry.get_rule(), self._cur_col_idx, entry.get_lookup_col_idx(), self._cur_entry_id)
                    new_entry.set_dot_idx(entry.get_dot_idx()+1)
                    if new_entry.get_dot_idx() == len(new_entry.get_rule().get_rhs()):
                        new_entry.set_completed()
                    new_entry.add_bktrack(entry, completed_entry.get_id())
                    prev_id = self._cur_entry_id
                    self._cur_entry_id = self._ELY[self._cur_col_idx].add_entry(new_entry)
                    if self._cur_entry_id != prev_id:
                        self._nELY[prev_id] = new_entry
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

        for col in range(self._n_cols):
            print("Column",col,":")
            iter = self._ELY[col].iterate_column(self._ELY[col])
            entry = iter.next()
            while(entry):
                print("Entry",j,",ID",entry.get_id(),":",entry.get_rule().get_lhs(),end='\t->\t')
                rhs = entry.get_rule().get_rhs()
                bktrack = entry.get_bktrack()
                for k in range(len(rhs)):
                    if k==entry.get_dot_idx():
                        print('.', end='')
                    print(rhs[k]+' - '+str(bktrack[k]),sep=' ',end=' ')
                print('\t',entry.get_rule().get_prob())
                entry = iter.next()

    def print_parse (self):
        def recurse_print(id):
            if id not in self._nELY:
                return ""
            entry = self._nELY[id]
            rhses = entry.get_rule().get_rhs()
            output_str = '( '
            for rhs, bktrk in zip(rhses, entry.get_bktrack()):
                output_str += rhs
                output_str += ' '
                output_str += recurse_print(bktrk)
            output_str += ') '
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


def parse_sen(pcfg_gram, sen2parse, result_slot):

    myELYChart = ELYChart(sen2parse.get_tokens(),pcfg_gram)
    for i in range(len(sen2parse.get_tokens())+1):
        myELYChart.set_cur_col_idx(i)
        worker_column = myELYChart.get_column(i)
        prev_predicted_NT = []
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
                        prev_predicted_NT.append(next_token)
                else:
                    myELYChart.scan(ely_entry)
            ely_entry = iter.next()


    output_str = myELYChart.print_parse()
    result_slot['result'] = output_str

if __name__ == '__main__':

    pcfg_gram = PCFG_Grammar(sys.argv[1])
    sen2parse = Sentence(sys.argv[2])

    parse_sen (pcfg_gram, sen2parse, result_slot = {'result':''})
    print(result_slot['result'])
