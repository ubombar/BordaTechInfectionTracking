



def solution(L, k, s):
    if len(L) == 0: return []
    if len(L) == 1:
        time, result = L[0]
        if result:
            return [] if s + k < time else [(time - k, s)]# P
        else:
            return [] if s < time else [(time, s)]# N

    i, j = 0, 1
    period = []
    start, end = L[0][0] - k, L[1][0]

    itime, jtime = start, end
    end_append = False

    if end > s: return []

    while jtime < s and j < len(L):
        itime, iresult = L[i] # first
        jtime, jresult = L[j] # second

        if iresult and jresult: # P P
            end_append = True
            end = jtime 
            j += 1
        elif iresult and not jresult: # P N
            end = jtime
            period.append((start, end))
            i = j
            j += 1
        elif not iresult and jresult: # N P
            start = max(itime, jtime - k)
            i += 1
            j += 1
        else: # N N
            i += 1
            j += 1

    if end_append:
        period.append((start, s))
    return period



'''
1   F
2   F
3   T
4   T
5   T
6   F
7   F
8   F
9   F
'''

L = [(1, True), (2, True), (3, False), (4, True)]
k = 1
s = 20
print(f"run with arguments L={L}, k={k}, s={s}")
print(f"expected:    {[(4, 6)]}")
print(f"got:         {solution(L, k, s)}")