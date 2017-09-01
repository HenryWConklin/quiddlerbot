from string import ascii_lowercase, whitespace, punctuation
import operator
 
import sys

primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]

charMap = dict({c:primes[i] for i,c in enumerate(ascii_lowercase)}, **{'qu':primes[26],'in':primes[27],'er':primes[28],'cl':primes[29],'th':primes[30]})

words = []
with open('dict.txt', 'rU') as dfile:
    words = dfile.read().split('\n') 

words = filter(lambda s: len(s) >2, words)
words = filter(lambda s: s.isalpha(), words)
def letterHash(s):
    if isinstance(s, (int,long)): 
        return s
    else:
        return reduce(operator.mul, map(lambda x : charMap[x], s), 1)

wordmap = [(w,letterHash(w)) for w in words]
def gencomboentries():
    res = []
    for w in words:
        cms = ['th','qu','cl','er','in']
        ncms = {x:0 for x in cms} 
        nz = False
        for cm in cms: 
            ct = w.count(cm)
            if ct != 0:
                nz = True
            ncms[cm] = ct
        if nz:
            ar = ncms['th'] 
            br = ncms['qu'] 
            cr = ncms['cl'] 
            dr = ncms['er'] 
            er = ncms['in'] 
            nocombow = list(w.replace('th', '').replace('qu', '').replace('cl', '').replace('er', '').replace('in',''))
            for a in range(0,ar+1):
                subw = nocombow + ['t','h'] * (ar-a) + ['th'] * a
                for b in range(0,br+1):
                    subw2 = subw + ['q','u'] * (br-b) + ['qu'] * b
                    for c in range(0,cr+1):
                        subw3 = subw2 + ['c','l'] * (cr-c) + ['cl'] * c
                        for d in range(0,dr+1):
                            subw4 = subw3 + ['e','r'] * (dr-d) + ['er'] * d
                            for e in range(0,er+1):
                                subw5 = subw4 + ['i','n'] * (er-e) + ['in'] * e
                                res.append((w, letterHash(subw5)))
    return res

wordmap += gencomboentries()
wordmap = list(sorted(wordmap, key=lambda x: x[1]))

# Finds the index of a word with a hash matching h, or if none exists, the index of whatever word has the closest hash
def hashInd(h):
    a = 0
    b = len(wordmap)
    mid = (a+b)/2
    while a < b and wordmap[mid][1] != h:
        if wordmap[mid][1] > h:
            b = mid
        else:
            a = mid+1
        mid = (a+b)/2
    return mid
            

# Returns a set of all words with at least the given letters
def wordsg(s, ws=None):
    lhash = letterHash(s)
    sind = hashInd(lhash)
    res = set()
    if ws is None:
        for i in range(sind, len(wordmap)):
            if wordmap[i][1] % lhash == 0:
                res.add(wordmap[i])
    else:
        for w in ws:
            if w[1] % lhash == 0:
                res.add(w)
    return res

# Returns a set of words with unique hashes, subset of wordsl
def uwordsg(s, ws=None):
    return [(v,k) for k,v in {w[1]: w[0] for w in wordsg(s,ws)}.items()]

# Returns a set of all words that contain a subset of the letters given
def wordsl(s, ws=None):
    lhash = letterHash(s)
    res = set()
    if ws is None:
        sind = hashInd(lhash)
        for i in range(sind+1): 
            if lhash % wordmap[i][1] == 0:
                res.add(wordmap[i])
    else:
        for w in ws:
            if lhash % w[1] == 0:
                res.add(w)
    return res
    
# Returns a set of words with unique hashes, subset of wordsl
def uwordsl(s, ws=None):
    return [(v,k) for k,v in {w[1]: w[0] for w in wordsl(s,ws)}.items()]

# Returns a set of all words that contain exactly all of the letters given
def wordse(s, ws=None):
    lhash = letterHash(s)
    res = set()
    if ws is None:
        sind = hashInd(lhash)
        while wordmap[sind][1] == lhash:
            sind -= 1
        sind += 1
        while sind < len(wordmap):
            if wordmap[sind][1] == lhash:
                res.add(wordmap[sind])
            else:
                break
            sind += 1
    else:
        for w in ws:
            if w[1] == lhash:
                res.add(w)
    return res

# Wordse is already unique, this is here in case I forget
uwordse = wordse

if __name__ == '__main__':
    while True:
        s = raw_input().strip()
        if s == '':
            break
        print
        print wordmap[hashInd(letterHash(s))] 
        print '\n'.join(list(sorted(wordsl(s))[:10]))
        print '====='
        print '\n'.join(list(sorted(wordse(s))[:10]))
        print '====='
        print '\n'.join(list(sorted(wordsg(s))[:10]))
        print '-----'
