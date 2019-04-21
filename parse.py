#!/usr/bin/env python

import sys
import copy
#Optimize time for wallstreet grammar
#Evaluate on sample grammars and sentences
#Create a UI for displaying the work

def parse_args():
    if len(sys.argv) < 3:
        raise ValueError("Required arguments foo.gr and foo.sen")

    return sys.argv[1], sys.argv[2]


def load_grammar(gr_file):

    f = open(gr_file)
    gr = {}
    NT = set()

    with open (gr_file) as f:
        for line in f:
            line = (line.strip('\n')).split('\t')

            rhs = line[2].split(' ')
            if len(rhs) == 1 and line[1] == rhs[0]:
                continue
            elif line[1] not in gr:
                gr[line[1]] = [[rhs,float(line[0])]]
            else:
                gr[line[1]].append([line[2].split(' '),float(line[0])])

            NT.update([line[1]])

    return gr, NT


def load_sentences(sen_file):
    text = []
    with open (sen_file) as f:
        for line in f:
            line = (line.strip('\n')).split(' ')
            if line and line[0]!='#':
                text.append(line)

    return text


def complete (ELY, BKTRK, idx, lookup_token, lookup_idx, rule_wt, bktrk_idx):
    for j, ely_rule in enumerate(ELY[lookup_idx]):
        remaining_dot = len(ely_rule[0]) - ely_rule[1]

        next_token = ely_rule[0][ely_rule[1]] if remaining_dot > 0 else None

        if next_token == lookup_token:

            new_entry = ely_rule.copy()
            new_entry[1] += 1

            bktrk_entry = copy.deepcopy(BKTRK[lookup_idx][j])

            bktrk_entry[0].append((idx,bktrk_idx))
            bktrk_entry[1] *= rule_wt

            if new_entry not in ELY[idx] or bktrk_entry[1] > BKTRK[idx][ELY[idx].index(new_entry)][1]:

                ELY[idx].append(new_entry)
                BKTRK[idx].append(bktrk_entry)


    return ELY, BKTRK


def scan (ELY, BKTRK, ely_rule, idx, term, sen):

    if idx == len(sen):
        return ELY, BKTRK

    if sen[idx] == term:
        if len(ELY) == idx + 1:
            ELY.append([])
            BKTRK.append([])

        new_entry = ely_rule.copy()
        new_entry[1] += 1
        if new_entry not in ELY[idx+1]:
            ELY[idx+1].append(new_entry)
            BKTRK[idx+1].append([[],1])

    return ELY, BKTRK

def predict(ELY, BKTRK, gr, idx, non_term):

    for rule in gr[non_term]:
        new_entry = [rule[0]]+[0,non_term,idx]
        if new_entry not in ELY[idx]:
            ELY[idx].append(new_entry)
            BKTRK[idx].append([[],rule[1]])

    return ELY, BKTRK


def parse(gr, sen):

    ELY = [[]]
    BKTRK = [[]]

    ELY, BKTRK = predict(ELY, BKTRK, gr, 0, 'ROOT')

    n = len(sen)

    for i in range(n+1):
        prev_predicted_NT = []
        for j, ely_rule in enumerate(ELY[i]):
            remaining_dot = len(ely_rule[0]) - ely_rule[1] #0 idx - RHS of the grammar rule and idx 2 - dot position in ely rule
            next_token = ely_rule[0][ely_rule[1]] if remaining_dot > 0 else None
            if next_token in NT and remaining_dot > 0 and next_token not in prev_predicted_NT:
                ELY, BKTRK = predict (ELY, BKTRK, gr, i, ely_rule[0][ely_rule[1]])
                prev_predicted_NT.append(next_token)

            if next_token not in NT and remaining_dot > 0:
                ELY, BKTRK = scan (ELY, BKTRK, ely_rule, i, next_token, sen)

            if next_token == None:
                ELY, BKTRK = complete (ELY, BKTRK, i, ely_rule[2], ely_rule[3], BKTRK[i][j][1], j)


    return ELY, BKTRK


def find_best_parse(ELY, BKTRK):
    completed_tokens = list(filter(lambda t: t[2] == 'ROOT' and t[1] == len(t[0]), ELY[-1]))

    best_parse_prob = float('-inf')
    for parse in completed_tokens:
        idx = ELY[-1].index(parse)
        if BKTRK[-1][idx][1] > best_parse_prob:
            best_parse_prob = BKTRK[-1][idx][1]
            best_parse_idx = idx

    return idx

def print_parse(ELY, BKTRK, idx):

    print("( ROOT",end=" ")
    recurse_print(ELY, BKTRK, -1, idx)

    print(")")

def recurse_print(ELY, BKTRK, ridx, cidx):

    print("(",end=" ")
    ptr = BKTRK[ridx][cidx][0]
    if not ptr:
        print(ELY[ridx][cidx][0][0],end=" ")
    else:
        for p in ptr:
            print(ELY[p[0]][p[1]][2],end=" ")

            recurse_print(ELY, BKTRK, *p)
    print(")",end=" ")

if __name__ == '__main__':

    gr_file, sen_file = parse_args()

    gr, NT = load_grammar(gr_file)

    sen = load_sentences(sen_file)

    for s in sen:

        ELY, BKTRK = parse(gr, s)

        best_parse_idx = find_best_parse(ELY, BKTRK)

        print_parse(ELY, BKTRK, best_parse_idx)
