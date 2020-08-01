from tabulate import tabulate
import re
from collections import OrderedDict

grammar_pattern = re.compile(r"(.+?)[=-]>\|?(.+)")
END = '$'
EMPTY = ''
EMPTY_IN = 'e'
EMPTY_OUT = 'e'
OR = '|'
AND = ' '


def grammar_definition(g):
    grammar_def = OrderedDict()

    def add(temp, v):
        m = grammar_def.get(temp, [])
        m += v
        grammar_def[temp] = m

    for i, match in enumerate(grammar_pattern.finditer(g)):
        t, s2 = match.group(1), match.group(2)
        t = t.strip()

        s2 = [s.strip().split(AND) for s in s2.split(OR)]
        add(t, s2)

    keys = list(grammar_def.keys())
    for i in range(len(keys)):
        grammar_def[i] = grammar_def[keys[i]]
        del grammar_def[keys[i]]

    mp = lambda s: keys.index(s) if s in keys else s if s != EMPTY_IN else EMPTY

    for k in grammar_def:
        grammar_def[k] = [[mp(s) for s in n] for n in grammar_def[k]]

    return grammar_def, keys


def first_set(grammar_def):
    """

    :param grammar_def:
    :return:
    """
    first = dict()

    def generate_first(element):
        r = []

        for S in grammar_def[element]:

            for s in S:
                if isinstance(s, str):
                    add(s, s)
                    r.insert(0, s)
                    if s == EMPTY:
                        add(element, s)

                    else:
                        break
                else:
                    temp = generate_first(s)

                    for x__ in {temp[i] for i in range(temp.index(EMPTY) if EMPTY in temp else len(temp))}:
                        r.insert(0, x__)
                        add(element, x__)

        for n in r:
            add(element, n)
        return r

    def add(key, v):
        m = first.get(key, set())
        m.add(v)
        first[key] = m

    for k in grammar_def:
        generate_first(k)

    return first


def follow_set(g, s, first=None):
    first = first or first_set(g)
    follow = dict()

    def add(k_temp, v):
        m = follow.get(k_temp, set())
        m.add(v)
        follow[k_temp] = m

    add(s, '$')

    def generate_follow(A):

        for E in g[A]:

            for i, x in enumerate(E):
                if not isinstance(x, str):
                    fst = []

                    for y in E[i + 1:]:
                        m = first.get(y, {y})
                        fst += m
                        if EMPTY not in m:
                            break

                    for y in fst:
                        if y != EMPTY:
                            add(x, y)

                    if len(fst) == 0 or EMPTY in fst:
                        for a in follow.get(A, {}):
                            add(x, a)

    h = lambda f: hash(n for v in f.values() for n in v)
    f_old = h(follow)

    while True:

        for k in g:
            generate_follow(k)
        if f_old == h(follow):
            break
        else:
            f_old = h(follow)

    return follow


def parse_table(G, first=None, follow=None):
    first = first_set(G)
    follow = follow_set(G, 0, first)

    result = dict()

    def add(N, k, F, t):
        m = result.get(N, dict())
        hm = m.get(k, set())
        hm.add((F, t))
        m[k] = hm
        result[N] = m

    def temp_first(a):
        frs = set()
        for x in a:
            f = first[x]
            frs = frs.union(f)
            if EMPTY not in f:
                break

        return frs - {EMPTY}

    def temp_p(A):
        for i, X in enumerate(G[A]):
            for a in temp_first(X):
                add(A, a, A, i)
            for x in X:

                if isinstance(x, str):

                    if x == EMPTY:
                        for b in follow[A]:
                            add(A, b, A, i)

                    else:

                        break

    for g in G:
        temp_p(g)
    return result


def create_table(grammar, keys, result=None, **kwargs):
    first = first_set(grammar)
    follow = follow_set(grammar, 0, first)
    terminals = set(n for v in first.values() for n in v).union(set(n for v in follow.values() for n in v))
    terminals -= {EMPTY}

    non_terminals = set(v for v in follow.keys())

    result = result or parse_table(grammar, first, follow)
    s = lambda s: s if s != EMPTY else EMPTY_OUT

    sorted_terminals = sorted(list(terminals))
    sorted_terminals.reverse()
    if len(sorted_terminals) > 4:
        sorted_terminals[4], sorted_terminals[3] = sorted_terminals[3], sorted_terminals[4]
    data = []
    for n in non_terminals:

        data2 = [keys[n]]
        for t in sorted_terminals:
            l3 = ""
            if result.get(n) and result[n].get(t):

                for i, p in enumerate(result[n][t]):
                    a, x = p
                    x = "".join([s(e) if isinstance(e, str) else keys[e] for e in grammar[a][x]])
                    if i > 0:
                        l3 += "\n"
                    l3 += ("%-2s → %-2s" % (keys[a], x))

            data2.append(l3)
        data2.append("  ".join(s(c) for c in first[n]))
        data2.append("  ".join(s(c) for c in follow[n]))
        data.append(data2)

    return tabulate(data, headers=["NON -\nTERMINALS"] + sorted_terminals + ["FIRST", "FOLLOW"], **kwargs)
