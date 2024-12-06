import os
import nltk
from collections import OrderedDict
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
import json
from conn import get_redis
from sklearn.feature_extraction.text import CountVectorizer


redis = get_redis()

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

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

		syn_sets_1 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence1]
		syn_sets_2 = [self.tagged_to_synset(*tagged_word) for tagged_word in sentence2]

		syn_sets_1 = [ss for ss in syn_sets_1 if ss]
		syn_sets_2 = [ss for ss in syn_sets_2 if ss]

		score, count = 0.0, 0
		best_score = [0.0]
		for ss1 in syn_sets_1:
			for ss2 in syn_sets_2:
				best1_score=ss1.path_similarity(ss2)
				if best1_score:
					best_score.append(best1_score)
			max1=max(best_score)
			if best_score:
				score += max1
				if max1 != 0.0:
					count += 1
					best_score=[0.0]

		try:
			score /= count
		except ZeroDivisionError as ze: 
			score = 0
		return score


	def perform_sentence_similarity(self):
		
		for idx, t in enumerate(self.sentences):
			corpus_dictionary_list = list(self.corpusDict.items())
			match_list = []
			source_diagram_id = corpus_dictionary_list[idx][0]
			target_sentence = t

			for sid, sentence in enumerate(self.sentences):
				# print("Similarity(\"%s\", \"%s\") = %s" % (target_sentence, sentence, self.sentence_similarity(target_sentence, sentence)))
				# print("Similarity(\"%s\", \"%s\") = %s" % (sentence, target_sentence, self.sentence_similarity(sentence, target_sentence)))
				if ((self.sentence_similarity(target_sentence, sentence) > 0.4 and self.sentence_similarity(sentence, target_sentence) > 0.6)):
					target_diagram_id = corpus_dictionary_list[sid][0]
					match_list.append(target_diagram_id)
				else:
					match_list.append(0)

				# if (self.is_ci_partial_seq_token_stopword_lemma_match(target_sentence, sentence)):
				# 	target_diagram_id = corpus_dictionary_list[sid][0]
				# 	match_list.append(target_diagram_id)
				# else:
				# 	match_list.append(0)
			self.matchingDict[source_diagram_id] = match_list

		return self.matchingDict
		# return 0

def create_sentence_similarity(input_dict):
	temporary_corpus_dictionary = input_dict['data']
	key = input_dict['key']
	orderedCorpusDict = OrderedDict(sorted(temporary_corpus_dictionary.items(), key=lambda t: t[0]))
	my_sentence_similarity = SentenceSimilarity()
	my_sentence_similarity.generateSentences(orderedCorpusDict)

	sentence_similarity = my_sentence_similarity.perform_sentence_similarity()
	
	redis.set(key, json.dumps(sentence_similarity))

