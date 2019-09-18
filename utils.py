import os
import difflib
import nltk
import string
from collections import OrderedDict
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import redis
import json

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

# import averaged_perceptron_tagger
from sklearn.feature_extraction.text import CountVectorizer

class BagofWordsGenerator():
	def __init__(self):
		self.corpus = []
		self.corpusDict = {}

	def addtoCorpus(self, diagramdescirption):
		self.corpus.append(diagramdescirption)

	def addtoCorpusDict(self,diagramid, diagramdescirption):
		self.corpusDict[diagramid] = diagramdescirption

	def getOrderedCorpus(self):
		return self.corpusDict

	def generateBagofWords(self):
		words = []
		vectorizer = CountVectorizer()
		features = vectorizer.fit_transform(self.corpus).todense()
		vocab =  vectorizer.vocabulary_
		for key, value in vocab.items():
			words.append([key, int(value)])
		return words


# Source: http://nlpforhackers.io/wordnet-sentence-similarity/
class SentenceSimilarity():	
	def __init__(self):
		self.sentences = []
		self.corpusDict = {}

		self.matches = {}
		self.matchingDict = {}

	def generateSentences(self, corpusDict):
		self.corpusDict = corpusDict
		for diagramid, desc in corpusDict.items():
			self.sentences.append(desc)

	def penn_to_wn(self, tag):
		""" Convert between a Penn Treebank tag to a simplified Wordnet tag """
		if tag.startswith('N'):
			return 'n'
		if tag.startswith('V'):
			return 'v'
		if tag.startswith('J'):
			return 'a'
		if tag.startswith('R'):
			return 'r'
		return None

	def tagged_to_synset(self, word, tag):
		wn_tag = self.penn_to_wn(tag)
		if wn_tag is None:
			return None
		try:
			return wn.synsets(word, wn_tag)[0]
		except:
			return None

	def sentence_similarity(self, sentence1, sentence2):

		sentence1 = pos_tag(word_tokenize(sentence1))
		sentence2 = pos_tag(word_tokenize(sentence2))

		synsets1 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence1]
		synsets2 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence2]

		synsets1 = [ss for ss in synsets1 if ss]
		synsets2 = [ss for ss in synsets2 if ss]

		score, count = 0.0, 0
		best_score = [0.0]
		for ss1 in synsets1:
			for ss2 in synsets2:
				best1_score=ss1.path_similarity(ss2)
				if best1_score is not None:
					best_score.append(best1_score)
			max1=max(best_score)
			if best_score is not None:
				score += max1
				if max1 is not 0.0:
					count += 1
					best_score=[0.0]

		try:
			score /= count
		except ZeroDivisionError as ze: 
			score = 0
		return score


	def doSentenceSimilarity(self):
		
		for idx, t in enumerate(self.sentences):
			cDictList = list(self.corpusDict.items())
			matchlist = []
			sourcediagramid = cDictList[idx][0]
			target_sentence = t

			for sid, sentence in enumerate(self.sentences):
				# print("Similarity(\"%s\", \"%s\") = %s" % (target_sentence, sentence, self.sentence_similarity(target_sentence, sentence)))
				# print("Similarity(\"%s\", \"%s\") = %s" % (sentence, target_sentence, self.sentence_similarity(sentence, target_sentence)))
				if ((self.sentence_similarity(target_sentence, sentence) > 0.4 and self.sentence_similarity(sentence, target_sentence) > 0.6)):
					targetdiagramid = cDictList[sid][0]
					matchlist.append(targetdiagramid)
				else:
					matchlist.append(0)

				# if (self.is_ci_partial_seq_token_stopword_lemma_match(target_sentence, sentence)):
				# 	targetdiagramid = cDictList[sid][0]
				# 	matchlist.append(targetdiagramid)
				# else:
				# 	matchlist.append(0)
			self.matchingDict[sourcediagramid] = matchlist

		return self.matchingDict
		# return 0

def createSenteceSimilarity(inputdict):
	tmpCorpusDict = inputdict['data']
	key = inputdict['key']
	orderedCorpusDict = OrderedDict(sorted(tmpCorpusDict.items(), key=lambda t: t[0]))
	mySS = SentenceSimilarity()
	mySS.generateSentences(orderedCorpusDict)

	sentenceSimilarity = mySS.doSentenceSimilarity()
	
	redis.set(key, json.dumps(sentenceSimilarity))

