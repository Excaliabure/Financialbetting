
from sentence_transformers import SentenceTransformer
from transformers import pipeline

"""
### Sentence sentimence

Quick start:
    pip install transformers
    

senti = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")


### sentence comparassion

from sentence_transformers import SentenceTransformer
sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(sentences)
print(embeddings)


"""