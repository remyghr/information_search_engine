import json
import html
import urllib.request
import urllib.parse
import xmltodict
import pandas as pd

### Partie 1 : chargement des données

# la thématique choisie, à modifier librement
theme = "climate"
docs = []
origines = []

# 1.1
# On construit l'adresse avec urlencode pour que les caractères spéciaux
# (espaces, accents...) soient correctement encodés.
url_hn = "https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(
    {"query": theme, "tags": "story", "hitsPerPage": 50})
print(url_hn)

with urllib.request.urlopen(url_hn) as reponse:
    d_hn = json.load(reponse)

print(d_hn.keys())           # hits, nbHits, page, nbPages, hitsPerPage...
print(d_hn["nbHits"])        # nombre total de documents trouvés par le moteur
hits = d_hn["hits"]
print(len(hits))             # 50 : ce que l'API nous a effectivement renvoyé
print(hits[0].keys())        # les champs disponibles pour un document

# Le champ contenant le contenu textuel est story_text. Il est absent des
# documents qui ne pointent que vers un lien extérieur : dans ce cas on se
# rabat sur le titre (champ title), toujours présent.
for hit in hits:
    texte = hit.get("story_text")
    if not texte:
        texte = hit.get("title", "")
    # le texte contient du HTML : <p> pour les paragraphes et des caractères
    # échappés comme &#x27; pour l'apostrophe
    texte = html.unescape(texte).replace("<p>", " ").strip()
    docs.append(texte)
    origines.append("hackernews")

print("Documents Hacker News :", len(docs))

# 1.2
url_arxiv = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
    {"search_query": "all:" + theme, "start": 0, "max_results": 50})
print(url_arxiv)

with urllib.request.urlopen(url_arxiv) as reponse:
    d_arxiv = xmltodict.parse(reponse.read())

print(d_arxiv.keys())                # feed : la racine du document XML
print(d_arxiv["feed"].keys())        # title, id, updated, entry...

# Attention : s'il n'y a qu'un seul résultat, xmltodict renvoie un simple
# dictionnaire et non une liste ; s'il n'y en a aucun, la clef entry est absente.
entrees = d_arxiv["feed"].get("entry", [])
if isinstance(entrees, dict):
    entrees = [entrees]
print(len(entrees))
print(entrees[0].keys())             # les champs disponibles pour un article

# Le champ contenant le contenu textuel est summary (le résumé de l'article).
for entree in entrees:
    texte = entree["summary"].replace("\n", " ").strip()
    docs.append(texte)
    origines.append("arxiv")

print("Taille du corpus :", len(docs))


### Partie 2 : sauvegarde des données

# 2.1
df = pd.DataFrame({"id": range(len(docs)),
                   "texte": docs,
                   "origine": origines})
print(df.shape)
print(df.head())
print(df["origine"].value_counts())

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
print("Nombre de documents :", len(df))

# 3.2
for texte in df["texte"]:
    mots = texte.split(" ")
    phrases = texte.split(".")
    print(len(mots), "mots,", len(phrases), "phrases")

# 3.3
# Les documents les plus courts sont les titres récupérés sur Hacker News
# lorsque le champ story_text était absent.
print("Avant filtrage :", len(df))
df = df[df["texte"].str.len() >= 20]
print("Après filtrage :", len(df))

# 3.4
chaine = " ".join(df["texte"])
print(len(chaine))
print(chaine[:500])