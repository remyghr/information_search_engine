class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add(self, identifiant, document):
        if identifiant not in self.production:
            self.production[identifiant] = document
            self.ndoc += 1

    def __str__(self):
        return f"Author(name={self.name}, ndoc={self.ndoc})"

    def display(self):
        print(f"Author: {self.name}")
        print(f"Number of documents: {self.ndoc}")
        print("Production:")
        for identifiant, document in self.production.items():
            print(f"  ID: {identifiant}, Document: {document.title}")