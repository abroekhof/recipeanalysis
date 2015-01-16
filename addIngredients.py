from recipeapp import db
from recipeapp.models import RefIng, Synonym
from datetime import datetime
import csv

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

f = open('ingredients.csv', 'rt')
reader = unicode_csv_reader(f)

# Initialize the tables
session = db.session

session.query(Synonym).delete()
session.query(RefIng).delete()
session.commit()
i = 0
try:
    for row in reader:
        i = i+1
        if i%100 == 0:
            print "Added",i,"ingredients"
        prevCell = ""
        prevCat = ""
        categories = []
        # Start by extracting category names
        for cell in row[0:4]:
            # Test if there is something in the cell
            if cell:
                # If there is, see if it's already in database
                cat = session.query(RefIng).filter(RefIng.ingredient==cell).first()
                if not cat:
                    # If it's not in the database, add it
                    cat = RefIng()
                    cat.ingredient = cell
                    cat.is_category = True
                    
                    # Test if there is a parent category (i.e. on the first cell
                    # there is none)
                    if prevCat:
                        cat.parent = prevCat
                        
                    session.add(cat)
                       
                categories.append(cat) 
                prevCat = cat
                prevCell = cell
        session.commit()
        
        # Once the categories are established, add the ingredient
        ingName = row[4]
            
        newIng = session.query(RefIng).filter(RefIng.ingredient==ingName).first()
        if not newIng:
            newIng = RefIng()
            newIng.ingredient = ingName
            newIng.is_category = False
            if prevCat:
                newIng.parent = prevCat
            session.add(newIng)

        for cell in row[4:]:
            if cell:
                syn = session.query(Synonym).filter(Synonym.synonym==cell).first()
                if not syn:
                    syn = Synonym()
                    syn.synonym = cell
                    session.add(syn)
                syn.ingredient = newIng
            
        session.commit()        
finally:
    f.close()


