#!/usr/bin/env python

import sys
import nltk
from collections import defaultdict
from nltk import word_tokenize
from math import log

def parse_args():
    if len(sys.argv) < 3:
        raise ValueError("Required arguments foo.gr and foo.sen")

    return sys.argv[1], sys.argv[2]


def load_grammar(gr_file):
    gr = {}
    NT = set()
    with open (gr_file) as f:
        for line in f:
            line = word_tokenize(line.strip())

            gr[line[1]] = [[line[2:],log(float(line[0]))]] if line[1] not in gr else gr[line[1]]+[[line[2:],log(float(line[0]))]]

            NT.update([line[1]])

    return gr, NT


def load_sentences(sen_file):
    with open (sen_file) as f:
        text = list(map(lambda t: word_tokenize(t.lstrip()), f))

    return text


def complete (ELY, idx, lookup_token, lookup_idx, rule_wt):
    for ely_rule in ELY[lookup_idx]:
        print("\nComplete Function: rule ", ely_rule, "for lookup ",lookup_token, "at idx ", lookup_idx)
        remaining_dot = len(ely_rule[0]) - ely_rule[2]

        next_token = ely_rule[0][ely_rule[2]] if remaining_dot > 0 else None

        if next_token == lookup_token:

            new_entry = ely_rule.copy()
            new_entry[2] += 1
            new_entry[1] += rule_wt
            if new_entry not in ELY[idx]:
                ELY[idx].append(new_entry)
    return ELY


def scan (ELY, ely_rule, idx, term, sen):
    print("\nScan Function: rule ", ely_rule, "for terminal ",term)

    if idx == len(sen):
        return ELY

    if sen[idx] == term:
        if len(ELY) == idx + 1:
            ELY.append([])

        new_entry = ely_rule.copy()
        new_entry[2] += 1
        if new_entry not in ELY[idx+1]:
            ELY[idx+1].append(new_entry)

    return ELY

def predict(ELY, gr, idx, non_term):

    for rule in gr[non_term]:
        print("\nPreict Function: rule ", rule, "for nonterminal ",non_term)
        new_entry = rule+[0,non_term,idx]
        if new_entry not in ELY[idx]:
            ELY[idx].append(new_entry)

    return ELY


def parse(gr, sen):

    ELY = [[]]

    ELY = predict(ELY, gr, 0, 'ROOT')

    n = len(sen)

    for i in range(n+1):
        for ely_rule in ELY[i]:
            print("\nCurrent rule ",ely_rule, "index ", i)
            remaining_dot = len(ely_rule[0]) - ely_rule[2] #0 idx - RHS of the grammar rule and idx 2 - dot position in ely rule
            next_token = ely_rule[0][ely_rule[2]] if remaining_dot > 0 else None
            if next_token in NT and remaining_dot > 0:
                ELY = predict (ELY, gr, i, ely_rule[0][ely_rule[2]])

            if next_token not in NT and remaining_dot > 0:
                ELY = scan (ELY, ely_rule, i, next_token, sen)

            if next_token == None:
                ELY = complete (ELY, i, ely_rule[3], ely_rule[4], ely_rule[1])
        if i == n:
            for i in range(n+1):
                print("\n\n###################### ",i," #############################")
                print(ELY[i])

    return ELY


def find_best_parse(ELY):
    completed_tokens = list(filter(lambda t: t[3] == 'ROOT' and t[2] == len(t[0]), ELY[-1]))
    print("\n",len(completed_tokens), " parses possible.\n")

    best_parse_prob = float('-inf')
    for parse in completed_tokens:
        if parse[1] > best_parse_prob:
            best_parse_prob = parse[1]
            best_parse = parse

    return best_parse

####
    global str
    if ptr == None:
        return 0
    else:
        for p in ptr:
            #print("(",p[lhs_idx],"(",' '.join(p[rhs_idx]), "(")
            str += "( " + p[lhs_idx] + " "
            if print_parse(p[ptr_idx]) == 0:
                str += ' '.join(p[rhs_idx]) + " )\n"



def print_parse(ELY, last_rule):

    print("(ROOT ")
    recurse_print(ELY, last_rule[0])

    print(")")

def recurse_print(ELY, ptr):

    print("(")
    for p in ptr:
        print(p," ")
        completed_tokens = list(filter(lambda t: t[3] == p and t[2] == len(t[0]), ELY[-1]))

    sys.exit(-1)

if __name__ == '__main__':
    gr_file, sen_file = parse_args()

    gr, NT = load_grammar(gr_file)

    sen = load_sentences(sen_file)

    print("\n\nGrammar: ",gr)

    for s in sen:

        print("\n\nSentence: ",s)
        ELY = [defaultdict()]

        best_parse_prob = 0
        parse_found = False
        str = ""

        ELY = parse(gr, s)

        best_parse = find_best_parse(ELY)

        print_parse(ELY, best_parse)
        sys.exit(-1)
        if parse(gr, s):
            #for col in range(len(s)+1):
            #print("#",col,"-",ELY[col])
            col = len(s)
            for i in range(len(ELY[col])):
                if (ELY[col][i][lhs_idx] == 'ROOT') and (ELY[col][i][dot_idx] == len(ELY[col][i][rhs_idx])):
                    if ELY[col][i][wt_idx] > best_parse_prob:

                        best_parse_prob = ELY[col][i][wt_idx]
                        bparse_idx = i

            print_parse([ELY[len(s)][bparse_idx]])

            print(str)
            print(best_parse_prob)
        #print(ELY[-1][bparse_idx])
        print("# ",parse_found)
