class Document:
    def __init__(self, title, author, date, url, text):
        self.title = title #titre du document
        self.author = author #nom de l’auteur
        self.date = date #date de publication
        self.url = url #url source
        self.text = text #contenu textuel du document

    def display(self):
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Date: {self.date}")
        print(f"URL: {self.url}")
        print(f"Text: {self.text[:100]}...")  #affiche les 100 premiers caractères du texte

    def __str__(self):
        return f"Document(title={self.title}, author={self.author}, date={self.date})"