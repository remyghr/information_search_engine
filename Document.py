class Document:
    def __init__(self, title, author, date, url, text):
        self.title = title #titre du document
        self.author = author #nom de l’auteur
        self.date = date #date de publication
        self.url = url #url source
        self.text = text #contenu textuel du document
        self.type = "Document"

    def display(self):
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Date: {self.date}")
        print(f"URL: {self.url}")
        print(f"Text: {self.text[:100]}...")  #affiche les 100 premiers caractères du texte

    def __str__(self):
        return f"Document(title={self.title}, author={self.author}, date={self.date})"

    def getType(self):
        return self.type

# Document spécialisé pour les messages issus de Hacker News
class HackerNewsDocument(Document):
    def __init__(self, title, author, date, url, text, nb_comments):
        super().__init__(title, author, date, url, text)
        self.nb_comments = nb_comments
        self.type = "HackerNews"

    def get_nb_comments(self):
        return self.nb_comments

    def set_nb_comments(self, nb_comments):
        self.nb_comments = nb_comments

    def getType(self):
        return "Hacker News"

    def __str__(self):
        return (f"{self.title} "f"(Hacker News, {self.nb_comments} commentaires)")

# Document spécialisé pour les articles Arxiv
class ArxivDocument(Document):
    def __init__(self, title, author, date, url, text, coauthors):
        super().__init__(title, author, date, url, text)
        self.coauthors = coauthors
        self.type = "Arxiv"

    def get_coauthors(self):
        return self.coauthors

    def set_coauthors(self, coauthors):
        self.coauthors = coauthors

    def getType(self):
        return "Arxiv"

    def __str__(self):
        return f"{self.title} (Arxiv, co-auteurs: {', '.join(self.coauthors)})"

# Crée automatiquement le bon type de document selon sa source
class DocumentFactory:
    @staticmethod
    def create(source, title, author, date, url, text, **infos):
        if source == "hackernews":
            return HackerNewsDocument(title, author, date, url, text, infos.get("nb_comments", 0))
        if source == "arxiv":
            return ArxivDocument(title, author, date, url, text, infos.get("coauthors", []))
        return Document(title, author, date, url, text)