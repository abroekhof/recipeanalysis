import numpy as np
from recipeapp import db
from recipeapp.models import Synonym, RefIng, ScrapedRecipe
from collections import defaultdict
import pickle
from sqlalchemy.orm import joinedload_all


def recurseHierarchy(ingObject, setOfIngs):
    # Test if the ingredient has a parent
    if ingObject.parentIng:
        setOfIngs = recurseHierarchy(ingObject.parent, setOfIngs)
    
    # Only add the parent ingredient if it is in the synonym list, 
    # i.e. it is actually an ingredient you would find in a recipe
    if db.session.query(Synonym).filter_by(synonym =
                                           ingObject.ingredient).first():
        setOfIngs.add(ingObject.ingredient)
    return setOfIngs

numRecs = db.session.query(ScrapedRecipe).count()

ingredDict = defaultdict( lambda: defaultdict(int))
ingredCount = defaultdict(int)
ingredIndex = []

ingSetDict = {}
print 'Making ingredient set dictionary'
for ing in db.session.query(RefIng).all():
    setOfIngs = set()
    # For each ingredient, see if their is a relevant parent ingredient
    setOfIngs = recurseHierarchy(ing,setOfIngs)
    ingSetDict[ing.id] = frozenset(setOfIngs)

count = 0 
print 'Count collocations'
# Look at each recipe
for recipe in db.session.query(ScrapedRecipe).options(joinedload_all('ingredients')).all():
    # Make sure there is more than one ingredient or else collocations don't make sense
    if len(recipe.ingredients) > 1:
        # Progress meter
        count += 1
        if count%100 == 0:
            print count, 'of', numRecs
    
        setOfSetsOfIngs = set()
        # Scan through each ingredient in the recipe
        # for each ingredient, there is a list of parent ingredients that also
        # should be counted towards the bigrams
        checkDupes = set()
        for ing in recipe.ingredients:
            if ing not in checkDupes and ing.refIng_id:
                checkDupes.add(ing)
                setOfSetsOfIngs.add(ingSetDict[ing.refIng_id])
        
        # Go through list of lists and count the bigrams
        checkDupes = set()
        checkDupes2 = set()
        while len(setOfSetsOfIngs) > 0:
            setOfIngs = setOfSetsOfIngs.pop()
            for rowIng in setOfIngs:
                # Increment the count of this ingredient
                if rowIng not in checkDupes2:
                    checkDupes2.add(rowIng)
                    ingredCount[rowIng] += 1
                # Record where the ingredient will appear in the data array
                for colSetOfIngs in setOfSetsOfIngs:
                    for colIng in colSetOfIngs:
                        checkSet = frozenset([rowIng,colIng])
                        if checkSet not in checkDupes:
                            checkDupes.add(checkSet)
                            ingredDict[rowIng][colIng] += 1
                            ingredDict[colIng][rowIng] += 1
                        
             
# convert to plain dictionary
ingredDict = dict(ingredDict)
ingredCount = dict(ingredCount)
print ingredCount
pickle.dump(ingredDict, open('matrices/ingredDict.pkl', "wb" ))
pickle.dump(ingredCount, open('matrices/ingredCount.pkl', "wb" ))
