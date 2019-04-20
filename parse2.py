#!/usr/bin/env python

import sys

#Global Variables
start_idx = 0
lhs_idx = 1
rhs_idx = 2
dot_idx = 3
wt_idx = 4
ptr_idx = 5

nt_idx = 1
t_idx = 2
prob_idx = 0
bparse_idx = 0

parse_found = False
ELY = {}
NT = []
str = ""

def parse_args():
    if len(sys.argv) < 3:
        raise ValueError("Required arguments foo.gr and foo.sen")

    return sys.argv[1], sys.argv[2]

def load_grammar(gr_file):
    f = open(gr_file)
    gr =[]

    i = 0
    for line in f:
        l = (line.strip('\n')).split('\t')

        gr.append([l[prob_idx], l[lhs_idx], l[rhs_idx].split(' ')])

        if gr[i][lhs_idx] not in NT:
            NT.append(gr[i][lhs_idx])

        i += 1

    return gr

def load_sentences(sen_file):
    f = open(sen_file)
    sen = []
    for line in f:
        l = line.lstrip()
        if l:
            l = (l.strip('\n')).split(' ')
            sen.append(l)

    return sen

def complete(non_term, pos, start, wt, ptr):

    for const in ELY[start]:

        if len(const[rhs_idx]) > const[dot_idx]:
            l = []
            if const[ptr_idx] != None:

                l.append(const[ptr_idx][0])
            l.append(ptr)


            if (const[rhs_idx][const[dot_idx]] == non_term) and ([const[start_idx], const[lhs_idx], const[rhs_idx], const[dot_idx]+1, const[wt_idx]*wt, l] not in ELY[pos]):

                ELY[pos].append([const[start_idx], const[lhs_idx], const[rhs_idx], const[dot_idx]+1, const[wt_idx]*wt, l])

#               print("complete:", pos, [const[start_idx], const[lhs_idx], const[rhs_idx], const[dot_idx]+1, const[wt_idx]*wt, l])


def predict(grammar, pos, non_term):

    for rule in grammar:

        if (rule[nt_idx] == non_term) and ([pos, non_term, rule[t_idx], 0, float(rule[prob_idx]), None] not in ELY[pos]):
            ELY[pos].append([pos, non_term, rule[t_idx], 0, float(rule[prob_idx]), None])
#            print("pr:",pos, [pos, non_term, rule[t_idx], 0, float(rule[prob_idx]), None])

def scan(sen, pos, terminal):
    if pos >= len(sen):
        return 0
    if sen[pos] == terminal:
        return 1
    return 0

def attach(pos, start, lhs, rhs, dot, wt, ptr):

    if len(ELY) <= pos + 1:
        ELY.append([])

    if [start, lhs, rhs, dot+1, wt, None] not in ELY[pos+1]:
        if ptr != None:
            ptr.append([0,'',rhs[dot],0,0,None])

        ELY[pos+1].append([start, lhs, rhs, dot+1, wt, ptr])
#print("attach:",pos,[start, lhs, rhs, dot+1, wt, ptr])


def parse(gr, sen):

    global parse_found

    for r in gr:
        
        if r[lhs_idx] == 'ROOT':
            ELY[0] = [[0, 'ROOT', r[rhs_idx], 0, float(r[prob_idx]), None]]
    if not ELY[0]:
        return 0

    n = len(sen)

    for pos in range(n+1):

        for const in ELY[pos]:

            if len(const[rhs_idx]) == const[dot_idx]:

                complete(const[lhs_idx], pos, const[start_idx], const[wt_idx], const)

            elif const[rhs_idx][const[dot_idx]] not in NT:
                if scan(sen, pos, const[rhs_idx][const[dot_idx]]):
                    attach(pos, const[start_idx], const[lhs_idx], const[rhs_idx], const[dot_idx], const[wt_idx], const[ptr_idx])

            elif len(const[rhs_idx]) > const[dot_idx]:

                if (const[rhs_idx][const[dot_idx]] in NT)  and  (NT not in [y[1] for y in ELY[pos]]):

                    predict(gr, pos, const[rhs_idx][const[dot_idx]])
            if pos == n:
                if (const[lhs_idx] == "ROOT") and (const[dot_idx] == len(const[rhs_idx])):
                    parse_found = True
    if parse_found:
        return 1

    return 0

def print_parse(ptr):
    global str
    if ptr == None:
        return 0
    else:
        for p in ptr:
            #print("(",p[lhs_idx],"(",' '.join(p[rhs_idx]), "(")
            str += "( " + p[lhs_idx] + " "
            if print_parse(p[ptr_idx]) == 0:
                str += ' '.join(p[rhs_idx]) + " )\n"



gr_file, sen_file = parse_args()

gr = load_grammar(gr_file)

sen = load_sentences(sen_file)

for s in sen:

    ELY = [[]]
    best_parse_prob = 0
    parse_found = False
    str = ""
    print("#Sentence: ",s)
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
