import json
import html
import os
import urllib.request
import urllib.parse
import xmltodict
import pandas as pd

from Document import Document
from datetime import datetime
from Author import Author

### Partie 1 : chargement des données

# la thématique choisie, à modifier librement
theme = "climate"
id2doc = {}
id2aut = {}
next_id = 0

if os.path.exists("corpus.csv"):
    df = pd.read_csv("corpus.csv", sep="\t")
    for _, ligne in df.iterrows():
        identifiant = int(ligne["id"])
        document = Document(
            title=str(ligne["titre"]),
            author=str(ligne["auteur"]),
            date=str(ligne["date"]),
            url=str(ligne["url"]),
            text=str(ligne["texte"]),
        )
        id2doc[identifiant] = document
        for nom_auteur in document.author.split(","):
            nom_auteur = nom_auteur.strip()

            if nom_auteur and nom_auteur != "Auteur inconnu":
                if nom_auteur not in id2aut:
                    id2aut[nom_auteur] = Author(nom_auteur)

                id2aut[nom_auteur].add(identifiant, document)
else:
    # Partie 1.1 : récupération des données Hacker News
    url_hn = "https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode({
        "query": theme,
        "tags": "story",
        "hitsPerPage": 50,
    })

    with urllib.request.urlopen(url_hn) as reponse:
        d_hn = json.load(reponse)

    for hit in d_hn["hits"]:
        texte = hit.get("story_text")

        if not texte:
            texte = hit.get("title", "")

        texte = html.unescape(texte).replace("<p>", " ").strip()

        titre = hit.get("title", "")
        auteur = hit.get("author", "Auteur inconnu")
        date = hit.get("created_at", "")
        url = hit.get("story_url") or hit.get("url") or ""

        document = Document(
            titre,
            auteur,
            date,
            url,
            texte,
        )
        identifiant = next_id
        id2doc[identifiant] = document

        if auteur:
            if auteur not in id2aut:
                id2aut[auteur] = Author(auteur)
            id2aut[auteur].add(identifiant, document)
        next_id += 1

    # Partie 1.2 : récupération des données Arxiv
    url_arxiv = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": "all:" + theme,
        "start": 0,
        "max_results": 50,
    })

    with urllib.request.urlopen(url_arxiv) as reponse:
        d_arxiv = xmltodict.parse(reponse.read())

    entrees = d_arxiv["feed"].get("entry", [])
    if isinstance(entrees, dict):
        entrees = [entrees]

    for entree in entrees:
        titre = entree.get("title", "").replace("\n", " ").strip()
        texte = entree.get("summary", "").replace("\n", " ").strip()
        date = entree.get("published", "")
        url = entree.get("id", "")
        auteur_xml = entree.get("author", "")
        if isinstance(auteur_xml, list):
            auteur = ", ".join(
                str(a.get("name", ""))
                for a in auteur_xml
                if isinstance(a, dict)
            )
        elif isinstance(auteur_xml, dict):
            auteur = auteur_xml.get("name", "Auteur inconnu")
        else:
            auteur = str(auteur_xml or "Auteur inconnu")
        document = Document(
            titre,
            auteur,
            date,
            url,
            texte,
        )
        identifiant = next_id
        id2doc[identifiant] = document
        for nom_auteur in auteur.split(","):
            nom_auteur = nom_auteur.strip()
            if nom_auteur:
                if nom_auteur not in id2aut:
                    id2aut[nom_auteur] = Author(nom_auteur)
                id2aut[nom_auteur].add(identifiant, document)
        next_id += 1


    ### Partie 2 : sauvegarde des données

    # 2.1
    donnees = []

    for identifiant, document in id2doc.items():
        donnees.append({
            "id": identifiant,
            "titre": document.title,
            "auteur": document.author,
            "date": document.date,
            "url": document.url,
            "texte": document.text,
        })

    df = pd.DataFrame(donnees)
    print(df.shape)
    print(df.head())
    df.to_csv("corpus.csv", sep="\t", index=False)
    print(df.shape)
    print(df.head())
    print(df.columns)

    # 2.2
    # On a pris soin de retirer les sauts de ligne des textes : sans cela, ils
    # casseraient le fichier csv, qui sépare ses lignes avec ce même caractère.
    df.to_csv("corpus.csv", sep="\t", index=False)

    # 2.3
    df = pd.read_csv("corpus.csv", sep="\t")
    print(df.shape)
# En pratique, on encadre la partie 1 par un test de la forme :
#     import os
#     if os.path.exists("corpus.csv"):
#         df = pd.read_csv("corpus.csv", sep="\t")
#     else:
#         ... interrogation des APIs, puis df.to_csv(...) ...
# de façon à n'interroger les APIs que la première fois.


### Partie 3 : premières manipulations des données

# 3.1
print("Nombre de documents :", len(id2doc))
print("Nombre d'auteurs :", len(id2aut))

premier_document = next(iter(id2doc.values()))
premier_document.display()

print(premier_document)
for nom_auteur, auteur in id2aut.items():
    print(nom_auteur, "-", auteur.ndoc, "document(s)")

# 3.2
for document in id2doc.values():
    texte = document.text
    mots = texte.split(" ")
    phrases = texte.split(".")
    print(len(mots), "mots,", len(phrases), "phrases")

# 3.3
# Les documents les plus courts sont les titres récupérés sur Hacker News
# lorsque le champ story_text était absent.
id2doc = {
    identifiant: document
    for identifiant, document in id2doc.items()
    if len(document.text) >= 20
}

# 3.4
chaine = " ".join(
    document.text
    for document in id2doc.values()
)

# Quelques statistiques par auteur

nom = input("Entrez le nom d'un auteur : ").strip()

if nom in id2aut:
    auteur = id2aut[nom]

    print("Nombre de documents :", auteur.ndoc)
    print("Taille moyenne :", auteur.average_document_length())
else:
    print("Auteur inconnu.")

