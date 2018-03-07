
# import nltk.corpus
# from nltk.corpus import wordnet
# import nltk.tokenize.punkt
# import nltk.stem.snowball

# Source: http://nbviewer.jupyter.org/urls/gist.github.com/mjbommar/e2a019e346b879c13d3d/raw/74a206c2629d6e661645e18369f05f6c79d15b65/fuzzy-sentence-matching-python.ipynb 
# class FuzzyMatcher():
# 	def __init__(self):
# 		self.stopwords = nltk.corpus.stopwords.words('english')
# 		self.stopwords.extend(string.punctuation)
# 		self.stopwords.append('')

# 		# Create tokenizer and stemmer
# 		self.tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
# 		self.lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
# 		self.sentences = []
# 		self.corpusDict = {}

# 		self.matches = {}
# 		self.matchingDict = {}

# 	def generateSentences(self, corpusDict):
# 		self.corpusDict = corpusDict
# 		for diagramid, desc in corpusDict.items():
# 			self.sentences.append(desc)


# 	def get_wordnet_pos(self, pos_tag):
# 		if pos_tag[1].startswith('J'):
# 			return (pos_tag[0], wordnet.ADJ)
# 		elif pos_tag[1].startswith('V'):
# 			return (pos_tag[0], wordnet.VERB)
# 		elif pos_tag[1].startswith('N'):
# 			return (pos_tag[0], wordnet.NOUN)
# 		elif pos_tag[1].startswith('R'):
# 			return (pos_tag[0], wordnet.ADV)
# 		else:
# 			return (pos_tag[0], wordnet.NOUN)

# 	def is_ci_partial_seq_token_stopword_lemma_match(self,a, b):
# 		"""Check if a and b are matches."""
# 		pos_a = map(self.get_wordnet_pos, nltk.pos_tag(self.tokenizer.tokenize(a)))
# 		pos_b = map(self.get_wordnet_pos, nltk.pos_tag(self.tokenizer.tokenize(b)))
# 		lemmae_a = [self.lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
# 		if token.lower().strip(string.punctuation) not in self.stopwords]
# 		lemmae_b = [self.lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
# 		if token.lower().strip(string.punctuation) not in self.stopwords]
# 		s = difflib.SequenceMatcher(None, lemmae_a, lemmae_b)

# 		return (s.ratio() > 0.66)

# 	# def is_ci_partial_noun_set_token_stopword_lemma_match(self,a, b):
# 	# 	"""Check if a and b are matches."""
# 	# 	pos_a = map(self.get_wordnet_pos, nltk.pos_tag(self.tokenizer.tokenize(a)))
# 	# 	pos_b = map(self.get_wordnet_pos, nltk.pos_tag(self.tokenizer.tokenize(b)))
# 	# 	lemmae_a = [self.lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_a \
# 	# 	if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in self.stopwords]
# 	# 	lemmae_b = [self.lemmatizer.lemmatize(token.lower().strip(string.punctuation), pos) for token, pos in pos_b \
# 	# 	if pos == wordnet.NOUN and token.lower().strip(string.punctuation) not in self.stopwords]
# 	# 	try: 
# 	# 		ratio = len(set(lemmae_a).intersection(lemmae_b)) / float(len(set(lemmae_a).union(lemmae_b)))
# 	# 	except ZeroDivisionError as ze:
# 	# 		ratio = 0
# 	# 	return (ratio > 0.66)

# 	def doFuzzyMatching(self):
# 		print (self.sentences)
# 		for idx, t in enumerate(self.sentences):
# 			cDictList = list(self.corpusDict.items())
# 			matchlist = []
# 			sourcediagramid = cDictList[idx][0]
# 			target_sentence = t

# 			for sid, sentence in enumerate(self.sentences):

# 				if (self.is_ci_partial_seq_token_stopword_lemma_match(target_sentence, sentence)):
# 					targetdiagramid = cDictList[sid][0]
# 					matchlist.append(targetdiagramid)
# 				else:
# 					matchlist.append(0)
# 			self.matchingDict[sourcediagramid] = matchlist

# 		return self.matchingDict
# 		# return 0
