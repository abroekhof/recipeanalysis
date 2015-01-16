from recipeapp import db
from recipeapp.models import Synonym, ScrapedIng
import re, nltk, pprint 
import random

print "Reading database"
rawIngredients = db.session.query(ScrapedIng).all()
random.shuffle(rawIngredients)
print "Extracting names"
ingList = [ing.name for ing in rawIngredients]
print "Making string"
ingString = ".  \n".join(ingList)
print "Tokenizing"
tokens = nltk.word_tokenize(ingString)
text = nltk.Text(tokens)


#for ing in ingList:
#    ingString = ingString + ing + ".  "
    
#    match =  re.match('(\d+ )?(\d/)?\d+ (cup|tablespoon|tbsp|teaspoon|tsp|pint|pound|lb|ounce|oz)',ing.name) 
 #   if match:
  #      good = good + 1
  #      print ing.name
  #      print match.group()
  #  else:
  #      #print ing.name
  #      bad = bad + 2

#print good
#print bad
#print good+bad
