import os
from conn import get_redis
from sklearn.feature_extraction.text import CountVectorizer


redis = get_redis()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

class BagofWordsGenerator():
	def __init__(self):
		self.corpus = []
		self.corpusDict = {}

	def add_to_corpus(self, diagram_description):
		self.corpus.append(diagram_description)

	def add_to_corpus_dict(self,diagramid, diagram_description):
		self.corpusDict[diagramid] = diagram_description

	def get_ordered_corpus(self):
		return self.corpusDict

	def generate_bag_of_words(self):
		words = []
		vectorizer = CountVectorizer()
		features = vectorizer.fit_transform(self.corpus).todense()
		vocab =  vectorizer.vocabulary_
		for key, value in vocab.items():
			words.append([key, int(value)])
		return words

