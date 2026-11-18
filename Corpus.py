import pandas as pd
from Document import Document
from Author import Author

class Corpus: 
    def __init__(self, name):
        self.name = name
        self.authors = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0

    def display(self):
        print(f"Corpus: {self.name}")
        print(f"Number of documents: {self.ndoc}")
        print(f"Number of authors: {self.naut}")
        print("Authors:")
        for author_name, author in self.authors.items():
            print(f"  {author_name}: {author.ndoc} document(s)")

    def display_by_date(self, nombre):
        documents = sorted(
            self.id2doc.values(),
            key=lambda document: document.date,
        )

        for document in documents[:nombre]:
            print(document.date, "-", document)

    def display_by_title(self, nombre):
        documents = sorted(
            self.id2doc.values(),
            key=lambda document: document.title.lower(),
        )

        for document in documents[:nombre]:
            print(document.title)

    def __repr__(self):
        return f"Corpus(name={self.name}, ndoc={self.ndoc}, naut={self.naut})"

    def save(self, filename="corpus.csv"):
        data = []
        for identifiant, document in self.id2doc.items():
            data.append({
                "id": identifiant,
                "titre": document.title,
                "auteur": document.author,
                "date": document.date,
                "url": document.url,
                "texte": document.text,
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, sep="\t", index=False)
        print("Corpus sauvegardé dans", filename)

    @classmethod
    def load(cls, filename="corpus.csv", name="Corpus"):
        new_corpus = cls(name)
        df = pd.read_csv(filename, sep="\t")
        for _, ligne in df.iterrows():
            identifiant = int(ligne["id"])

            document = Document(
                title=str(ligne["titre"]),
                author=str(ligne["auteur"]),
                date=str(ligne["date"]),
                url=str(ligne["url"]),
                text=str(ligne["texte"]),
            )
            new_corpus.id2doc[identifiant] = document
            for nom_auteur in document.author.split(","):
                nom_auteur = nom_auteur.strip()
                if nom_auteur and nom_auteur != "Auteur inconnu":
                    if nom_auteur not in new_corpus.authors:
                        new_corpus.authors[nom_auteur] = Author(nom_auteur)
                    new_corpus.authors[nom_auteur].add(
                        identifiant,
                        document,
                    )
                    
        new_corpus.ndoc = len(new_corpus.id2doc)
        new_corpus.naut = len(new_corpus.authors)
        print("Corpus chargé depuis", filename)
        return new_corpus