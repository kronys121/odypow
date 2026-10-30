import json,re
d=json.load(open(__file__.rsplit('/',1)[0]+'/vo.json'))
W=[(re.sub(r"[^a-z0-9]","",w['word'].lower().replace('’',"'")),w['start'],w['end']) for w in d['words']]
W=[w for w in W if w[0]]
def at(phrase, after=0.0, end=False):
    toks=[re.sub(r"[^a-z0-9]","",t.lower().replace('’',"'")) for t in phrase.split()]
    toks=[t for t in toks if t]
    for i in range(len(W)-len(toks)+1):
        if W[i][1]<after: continue
        if all(W[i+j][0].startswith(toks[j]) for j in range(len(toks))):
            return W[i+len(toks)-1][2] if end else W[i][1]
    raise ValueError(phrase)
