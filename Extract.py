import json
import html
import os
import urllib.request
import urllib.parse
import xmltodict
import pandas as pd

from Document import DocumentFactory
from datetime import datetime
from Author import Author
from Corpus import Corpus

### Partie 1 : chargement des données

# la thématique choisie, à modifier librement
theme = "climate"
id2doc = {}
id2aut = {}
next_id = 0

def ajouter_document(document, auteurs):
    global next_id

    identifiant = next_id
    id2doc[identifiant] = document
    next_id += 1

    for nom_auteur in auteurs:
        nom_auteur = nom_auteur.strip()

        if nom_auteur:
            if nom_auteur not in id2aut:
                id2aut[nom_auteur] = Author(nom_auteur)

            id2aut[nom_auteur].add(identifiant, document)

if os.path.exists("corpus.csv"):
    df = pd.read_csv("corpus.csv", sep="\t")
    for _, ligne in df.iterrows():
        identifiant = int(ligne["id"])
        source = str(ligne.get("source", "Document"))
        if source == "Hacker News":
            document = DocumentFactory.create(
                source="hackernews",
                title=str(ligne["titre"]),
                author=str(ligne["auteur"]),
                date=str(ligne["date"]),
                url=str(ligne["url"]),
                text=str(ligne["texte"]),
                nb_comments=int(ligne.get("nb_comments", 0))
            )
        elif source == "Arxiv":
            coauthors = str(ligne.get("coauthors", ""))

            if coauthors and coauthors != "nan":
                liste_auteurs = [
                    auteur.strip()
                    for auteur in coauthors.split(" | ")
                    if auteur.strip()
                ]
            else:
                liste_auteurs = [
                    auteur.strip()
                    for auteur in str(ligne["auteur"]).split(",")
                    if auteur.strip()
                ]

            document = DocumentFactory.create(
                "arxiv",
                str(ligne["titre"]),
                str(ligne["auteur"]),
                str(ligne["date"]),
                str(ligne["url"]),
                str(ligne["texte"]),
                coauthors=liste_auteurs,
            )
        else:
            document = DocumentFactory.create(
                "document",
                str(ligne["titre"]),
                str(ligne["auteur"]),
                str(ligne["date"]),
                str(ligne["url"]),
                str(ligne["texte"]),
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
        nb_comments = hit.get("num_comments", 0)

        document = DocumentFactory.create(
            "hackernews",
            titre,
            auteur,
            date,
            url,
            texte,
            nb_comments=nb_comments,
        )

        ajouter_document(document, [auteur] if auteur else [])

    # Partie 1.2 : récupération des données Arxiv
    url_arxiv = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": "all:" + theme,
        "start": 0,
        "max_results": 10,
    })

    try:
        with urllib.request.urlopen(url_arxiv) as reponse:
            d_arxiv = xmltodict.parse(reponse.read())

    except urllib.error.HTTPError as erreur:
        if erreur.code == 429:
            print("Arxiv a refusé la requête : HTTP 429")

            retry_after = erreur.headers.get("Retry-After")

            if retry_after:
                print("Retry-After :", retry_after)
            else:
                print("Arxiv n'a fourni aucun Retry-After.")

        raise

    entrees = d_arxiv["feed"].get("entry", [])
    if isinstance(entrees, dict):
        entrees = [entrees]

    for entree in entrees:
        titre = entree.get("title", "").replace("\n", " ").strip()
        texte = entree.get("summary", "").replace("\n", " ").strip()
        date = entree.get("published", "")
        url = entree.get("id", "")
        auteur_xml = entree.get("author", [])

        if isinstance(auteur_xml, dict):
            auteur_xml = [auteur_xml]
        elif not isinstance(auteur_xml, list):
            auteur_xml = []

        liste_auteurs = []
        for auteur_info in auteur_xml:
            if isinstance(auteur_info, dict):
                nom = auteur_info.get("name", "").strip()

                if nom:
                    liste_auteurs.append(nom)

        auteur = ", ".join(liste_auteurs)
        document = DocumentFactory.create(
            "arxiv",
            titre,
            auteur,
            date,
            url,
            texte,
            coauthors=liste_auteurs,
        )
        ajouter_document(document, liste_auteurs)

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
            "source": document.getType(),
        })

    df = pd.DataFrame(donnees)
    #print(df.shape)
    #print(df.head())
    df.to_csv("corpus.csv", sep="\t", index=False)
    #print(df.shape)
    #print(df.head())
    #print(df.columns)

    # 2.2
    # On a pris soin de retirer les sauts de ligne des textes : sans cela, ils
    # casseraient le fichier csv, qui sépare ses lignes avec ce même caractère.
    #df.to_csv("corpus.csv", sep="\t", index=False)

    # 2.3
    #df = pd.read_csv("corpus.csv", sep="\t")
    #print(df.shape)
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

# Creation du corpus

corpus = Corpus.get_instance("Climate")

corpus.id2doc = id2doc
corpus.authors = id2aut
corpus.ndoc = len(id2doc)
corpus.naut = len(id2aut)
print(corpus)
corpus.display()
corpus.save("corpus.csv")

corpus_charge = Corpus.load(
    filename="corpus.csv",
    name="Climate chargé",
)

print(corpus_charge)
corpus_charge.display()
corpus_charge.display_by_date(10)
corpus_charge.display_by_title(10)

# Quelques statistiques par auteur

nom = input("Entrez le nom d'un auteur : ").strip()

if nom in id2aut:
    auteur = id2aut[nom]

    print("Nombre de documents :", auteur.ndoc)
    print("Taille moyenne :", auteur.average_document_length())
else:
    print("Auteur inconnu.")

