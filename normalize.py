import numpy as np
from recipeapp.models import ScrapedRecipe, RefIng
from recipeapp import db
import pickle
from sqlalchemy import func 
from collections import defaultdict

def lFunc(k,n,x):
    return k*np.log(x)+(n-k)*np.log(1-x)

print 'Resetting all canonical ingredient counts'
for ingredient in db.session.query(RefIng).all():
    ingredient.count = 0
    ingredient.arrayIndex = None
db.session.commit()


# Dictionary of dictionaries of collocations (i.e. 2d matrix)
ingredDict = pickle.load(open("matrices/ingredDict.pkl", "rb"))
ingredCount = pickle.load(open("matrices/ingredCount.pkl", "rb"))


ingredIndex = []
for ing, count in ingredCount.items():
    if count >= 10:
        ingredIndex.append(ing)


print 'Converting dictionary into ndarray'
N = len(ingredIndex)
nrmlz = N
print N
ingredMat = np.zeros((N,N))
for rowIndex, rowIng in enumerate(ingredIndex):
    ingredCount[rowIng] += 0
    sqlIng = db.session.query(RefIng).filter(RefIng.ingredient == rowIng).one()
    sqlIng.arrayIndex = rowIndex
    sqlIng.count = ingredCount[rowIng]
    if rowIng in ingredDict:
        for colIndex, colIng in enumerate(ingredIndex):
            if colIng in ingredDict[rowIng]:
                ingredMat[rowIndex][colIndex] += ingredDict[rowIng][colIng]
                if ingredDict[rowIng][colIng] == ingredCount[rowIng]:
                    print rowIng
db.session.commit()

np.save('matrices/rawDataArray', ingredMat)

newArray = np.zeros_like(ingredMat)
N = np.float64(db.session.query(ScrapedRecipe).count())

np.seterr(all='raise')
it = np.nditer(ingredMat, flags=['multi_index'])
i = 0
while not it.finished:
    index = it.multi_index
    c1 = np.float64(ingredCount[ingredIndex[index[0]]])
    c2 = np.float64(ingredCount[ingredIndex[index[1]]])
    c12 = np.float64(it[0])
    if c12 == 0:
        newArray[index] = -1
    else:
        newArray[index] = np.log((c12*N)/(c1*c2))/(-np.log(c12/N))
    it.iternext()
#     if index[0] != index[1] and it[0] != 0:
#         i += 1
#         if i%10000 == 0:
#             print i
#         
#         # index[0] divides by the row ingredient (normalizes data)
#         # index[1] divides by the column ingredient (conditional probability)
#         c12 = np.float64(it[0])
#         c1 = np.float64(ingredCount[ingredIndex[index[0]]])
#         c2 = np.float64(ingredCount[ingredIndex[index[1]]])
#         p = np.float64(c2/N)
#         p1 = np.float64(c12/c1)
#         p2 = np.float64((c2 - c12)/(N - c1))
#         likeRatio = -2*(lFunc(c12,c1,p)+lFunc(c2-c12,N-c1,p)-
#                 lFunc(c12,c1,p1)-lFunc(c2-c12,N-c1,p2))
#         try:
#             newArray[index] = chi2.cdf(likeRatio, 1)
#         except FloatingPointError as e:
#             print e
#             newArray[index] = 1
#             print ingredIndex[index[0]],ingredIndex[index[1]],c12, c1, c2, p, p1, p2, newArray[index]
#     else:
#         newArray[index] = 0
#     
    
    
np.save('matrices/dataArray',newArray)
