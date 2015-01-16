from recipeapp import db
from recipeapp.models import Synonym, ScrapedIng
from porterstemmer import Stemmer
import unicodedata
import sys, re

def strip_accents(s):
   return ''.join((c for c in unicodedata.normalize('NFD', unicode(s)) if
                   unicodedata.category(c) != 'Mn'))

def cleanToken(token, stemmer):
    token = strip_accents(token)
    token = stemmer(token)
    return token
    
session = db.session

stemmer = Stemmer()
print "Reading ingredients into dictionary"
synIngs = []
for ing in session.query(Synonym).all():
    synonym = ing.synonym.lower()
    synonym = re.sub('\-',' ',synonym)
    synonym = synonym.split()
    synonym = [cleanToken(token,stemmer) for token in synonym]
    synonym = set(synonym)
    synIngs.append((synonym, len(ing.synonym), ing))
    ing.count = 0
    print synonym
session.commit()
print "Finished reading ingredients"

rawIngredients = session.query(ScrapedIng).all()
numIngredients = len(rawIngredients)
i = 0

for rawIng in rawIngredients:
    i += 1
    if i%100 == 0:
        print i, "of", numIngredients
        
    toMatch = rawIng.name.lower()
    toMatch = re.sub('\([^\(]+\)|\*','',toMatch)
    toMatch = re.sub('[,:\-;]',' ',toMatch)
    toMatch = toMatch.split()
    toMatch = [cleanToken(token,stemmer) for token in toMatch]
    toMatch = set(toMatch)
    
    maxLen = -1
    choice = ()
    for syn in synIngs:
        if len(syn[0] & toMatch) == len(syn[0]) and syn[1] > maxLen:
            maxLen = syn[1]
            choice = syn
    if len(choice)>1:
        rawIng.refIng_id = choice[2].parentIng
        rawIng.refIng_name = choice[2].synonym
        choice[2].count += 1
    else:
        rawIng.refIng_name = 'UNK'
session.commit()
