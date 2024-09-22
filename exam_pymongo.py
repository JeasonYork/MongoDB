from pymongo import MongoClient

from pprint import pprint

################### Connexion à la base de données ####################

# a) Se connecter à MongoDB
client = MongoClient(
    host="127.0.0.1",
    port=27017,
    username="admin",
    password="pass",
    # authSource est la BDD d'authentification
    authSource="admin"

)

# (b) Liste des BDD
database_list = client.list_database_names()

# Afficher la liste des BDD
print("b) Liste des bases de données disponibles:")
for db_name in database_list:
    print(db_name)

# (c) Liste des collections
database_name = "sample"
db = client[database_name]
collection_list = db.list_collection_names()

print(f"(c) liste des collections de la BDD {database_name} :")
for col_name in collection_list:
    print(col_name)

# (d) Afficher un des documents de cette collection.
collection_name = "books"
col = db[collection_name]
doc = col.find_one()
print("(d) afficher un document depuis la collection bookd")
pprint(doc)


# (e) Afficher le nombre de documents dans cette collection
document_count = col.count_documents({})
print("(e) Les bombre de document de la collection: ",document_count)

#################### Exploration de la base ###########################"
print("\n------------------Exploration de la base-----------------")
# (a) 1.Afficher le nombre de livres avec plus de 400 pages
books_gt_400pg = col.count_documents({
    "pageCount": {"$gt": 400}
})
print("(a.1) Le nombre de livres avec plus de 400 pages",books_gt_400pg)

# (a) 2.Afficher le nombre de livres avec plus de 400 pages et publiés
books_gt_400_pg_pub = col.count_documents({
    "pageCount": {"$gt": 400},
    "status": "PUBLISH"
})
print("(a.2) Le nombre de livres avec plus de 400 pages et pbuliés: ", books_gt_400_pg_pub)

#(b) Afficher le nombre de livres ayant le mot-clé Android dans leur description (brève ou longue)
books_android = col.count_documents({
     "$or": [
        {"shortDescription": {"$regex": "Android", "$options": "i"}},
        {"longDescription": {"$regex": "Android", "$options": "i"}}
     ]
})
print("(b) Afficher le nombre de livres ayant le mot-clé Android dans leur description (brève ou longue): ",books_android)

#(c) Afficher deux listes de catégorie distinctes
categories = [
    {
        "$group": {
            "_id": None,
            "categories_0": {"$addToSet": {"$arrayElemAt": ["$categories", 0]}},
            "categories_1": {"$addToSet": {"$arrayElemAt": ["$categories", 1]}}
        }
    }
]
  ## Construire une liste de catégorie avec une agregation
categories_list = list(col.aggregate(categories))
  ## Afficher les catégories pour les index 0 et 1
categories_0 = categories_list[0]["categories_0"]
categories_1 = categories_list[0]["categories_1"]

print("\n(c) Liste des catégories distincts pour l'index 0: ",categories_0)
print("\n(c) Liste des catégories distincts pour l'index 1: ",categories_1)

#(d) Afficher le nombre de livres qui contiennent des noms de langages suivant dans leur description longue : Python, Java, C++, Scala
books_prog_language = col.count_documents({
     "$or": [
        {"longDescription": {"$regex": "Python", "$options": "i"}},
        {"longDescription": {"$regex": "Java", "$options": "i"}},
        {"longDescription": {"$regex": "C++", "$options": "i"}},
        {"longDescription": {"$regex": "Scala", "$options": "i"}}
     ]
})
print("\n(d)Le nombre de livres qui contiennent des noms de langages suivant dans leur description longue : Python, Java, C++, Scala: ",books_prog_language)

#(e) Afficher diverses informations statistiques
pipeline_categories = [
    {
        "$unwind": "$categories"
    },
    {
        "$group": {
            "_id": "$categories",
            "maxPages": {"$max": "$pageCount"},
            "minPages": {"$min": "$pageCount"},
            "avgPages": {"$avg": "$pageCount"},
            "totalBooks": {"$sum": 1}
        }
    }
]

result_list = list(col.aggregate(pipeline_categories))
formatted_result = {}

for category in result_list:
    category_name= category["_id"]
    max_pages = category["maxPages"]
    min_pages = category["minPages"]
    avg_pages = category["avgPages"]
    #print("\nCatégorie",category_name)
    #print("\nMax pages",max_pages)
    #print("\nMin pages",min_pages)
    #print("\nMoyenne pages",avg_pages)
    category_info = {
        "Categorie": category_name,
        "Max Pages": max_pages,
        "Min Pages": min_pages,
        "Avg Pages": avg_pages,
    }

    formatted_result[category_name] = category_info
####Afficher le resultat
print("\n(e)Afficher diverses informations statistiques:\n",formatted_result)

#(f) Via une pipeline d'agregation, extraire l'année, le mois, le jour

pipeline_publishedDate = [
    {
        "$project": {
            "title": 1,
            "publishedDate": 1,
            "year": {"$year": "$publishedDate"},
            "month": {"$month": "$publishedDate"},
            "day": {"$dayOfMonth": "$publishedDate"}
        }
    },
    {
        "$match": {
            "year": {"$gt": 2009}
        }
    },
    {
        "$limit": 20
    }
]


result_list = list(col.aggregate(pipeline_publishedDate))
formatted_result = {}

for book_info in result_list:
    title = book_info["title"]
    published_date = book_info["publishedDate"]
    year = book_info["year"]
    month = book_info["month"]
    day = book_info["day"]

    #print(f"\nTitle: {title}")
    #print(f"Published Date: {published_date}")
    #print(f"Year: {year}")
    #print(f"Month: {month}")
    #print(f"Day: {day}")

    category_info = {
        "titre": title,
        "date": published_date,
        "annee": year,
        "mois": month,
	"jour": day,
    }

    formatted_result[title] = category_info
####Afficher le resultat
print("\n(f)Extraire l'année, le mois et le jour de publishedDate:\n",formatted_result)

#(g) À partir de la liste des auteurs, créez de nouveaux attributs (author1, author2 ... author_n). Observez le comportement de "$arrayElemAt". N'affichez que les 20 premiers dans l'ordre chronologique.

pipeline_create_new_attributes = [
    {
        "$project": {
            "_id": 0,
            "authors": 1,
        }
    },
    {
        "$unwind": "$authors"
    },
    {
        "$match": {
            "authors": {"$ne": ""}
        }
    },
    {
        "$group": {
            "_id": None,
            "authors": {"$push": "$authors"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "authors": {
                "$slice": ["$authors", 20]
            }
        }
    },
    {
        "$unwind": "$authors"
    },
    {
        "$sort": {"authors": 1}  # Trier par ordre chronologique
    },
    {
        "$group": {
            "_id": None,
            "authors": {"$push": "$authors"}
        }
    },
    {
        "$project": {
            "_id": 0,
            "auteurs": {
                "$map": {
                    "input": {"$range": [0, {"$size": "$authors"}]},
                    "as": "index",
                    "in": {"$arrayElemAt": ["$authors", "$$index"]}
                }
            }
        }
    }
]

# Executer l'aggregation
result_create_new_attributes = list(col.aggregate(pipeline_create_new_attributes))

# formater le resultat
formatted_result_create_new_attributes = result_create_new_attributes[0] if result_create_new_attributes else {}

print("\n(g) Afficher les 20 premiers auteurs non vides dans l'ordre chronologique avec les nouveaux attributs:\n", formatted_result_create_new_attributes)

# Compter le nombre d'éléments dans auteurs pour vérifer le resultat
if "auteurs" in formatted_result_create_new_attributes:
    number_of_elements = len(formatted_result_create_new_attributes["auteurs"])
    print(f"Nombre d'éléments dans auteurs : {number_of_elements}")
else:
    print("Aucun résultat trouvé.")

# (h)créer une colonne contenant le nom du premier auteur

pipeline_count_articles = [
    {
        "$project": {
            "_id": 0,
            "first_auth": {"$arrayElemAt": ["$authors", 0]},  # Récupérer le premier auteur
        }
    },
    {
        "$group": {
            "_id": "$first_auth",
            "nombre_articles": {"$sum": 1}  # compter le nombre d'articles pour chaque premier auteur
        }
    },
    {
        "$project": {
            "auteur": "$_id",  # Renommer '_id' en 'auteur'
            "nombre_articles": 1
        }
    },
    {
        "$sort": {"nombre_articles": -1}  # trier par ordre decroissant 
    },
    {
        "$limit": 10  # Limiter les résultats aux 10 premiers auteurs les plus prolifiques
    }
]

# Exécuter le pipeline 
result_count_articles = list(col.aggregate(pipeline_count_articles))

# Afficher le nombre de publications pour les 10 premiers auteurs les plus prolifiques
print("\n(h) Nombre de publications pour les 10 premiers auteurs les plus prolifiques :\n", result_count_articles)

# (i) Afficher la distribution du nombre d'auteurs
pipeline_distribution_auteurs = [
    {
        "$project": {
            "_id": 0,
            "nombre_auteurs": {"$size": "$authors"}  #créer une nouvelle colonne avec le nombre d'auteurs
        }
    },
    {
        "$group": {
            "_id": "$nombre_auteurs",
            "nombre_publications": {"$sum": 1}  
        }
    },
    {
        "$sort": {"_id": 1}  
    }
]

# executer le pipeline d'agrégation
result_distribution_auteurs = list(col.aggregate(pipeline_distribution_auteurs))

# Afficher la distribution du nombre d'auteurs
print("\n(i) Distribution du nombre d'auteurs :\n", result_distribution_auteurs)

# (j) Afficher l'occurence de chaque auteur

pipeline_occurrence_auteurs = [
    {
        "$unwind": "$authors"  # separer les auteurs
    },
    {
        "$match": {
            "authors": {"$ne": ""}  # supprimer les auteurs vides
        }
    },
    {
        "$group": {
            "_id": {"auteur": "$authors", "index": "$authors"},
            "occurrence": {"$sum": 1}  # Compter l'occurrence de chaque auteur par index
        }
    },
    {
        "$sort": {"occurrence": -1},  
    },
    {
        "$limit": 20  
    }
]

# Exécuter le pipeline d'agrégation
result_occurrence_auteurs = list(col.aggregate(pipeline_occurrence_auteurs))

# Afficher l'occurrence de chaque auteur selon son index
print("\n(j) Occurrence de chaque auteur selon son index :\n", result_occurrence_auteurs)
