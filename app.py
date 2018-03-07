from flask import Flask, url_for
from flask import render_template
from functools import wraps
from flask import request, Response
import requests, json, GeodesignHub
import logging, config
import math, json
from shapely.ops import polygonize
from shapely.geometry.base import BaseGeometry
from shapely.geometry import shape, mapping, shape, asShape
from shapely.geometry import Polygon, MultiPolygon, MultiLineString
from shapely import speedups
import ShapelyHelper
import random
# import averaged_perceptron_tagger
from sklearn.feature_extraction.text import CountVectorizer
import redis
import os
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

# Imports
import difflib
import nltk
import string
from collections import OrderedDict
from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

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

		score /= count
		return score


	def doSentenceSimilarity(self):
		
		for idx, t in enumerate(self.sentences):
			cDictList = list(self.corpusDict.items())
			matchlist = []
			sourcediagramid = cDictList[idx][0]
			target_sentence = t

			for sid, sentence in enumerate(self.sentences):
				# print("Similarity(\"%s\", \"%s\") = %s" % (target_sentence, sentence, sentence_similarity(target_sentence, sentence)))
				# print("Similarity(\"%s\", \"%s\") = %s" % (sentence, target_sentence, sentence_similarity(sentence, target_sentence)))
				if ((self.sentence_similarity(target_sentence, sentence) > 0.4 and self.sentence_similarity(sentence, target_sentence) > 0.4)):
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


app = Flask(__name__)

@app.route('/', methods = ['GET'])
def api_root():
	''' This is the root of the webservice, upon successful authentication a text will be displayed in the browser '''
	try:
		projectid = request.args.get('projectid')
		cteamid = request.args.get('cteamid')
		apitoken = request.args.get('apitoken')
		synthesisid = request.args.get('synthesisid')
	except KeyError as e:
		msg = json.dumps({"message":"Could not parse Projectid, Diagram ID or API Token ID. One or more of these were not found in your JSON request."})
		return Response(msg, status=400, mimetype='application/json')

	if projectid and cteamid and apitoken and synthesisid:
		myAPIHelper = GeodesignHub.GeodesignHubClient(url = config.apisettings['serviceurl'], project_id=projectid, token=apitoken)

		r = myAPIHelper.get_synthesis(teamid = int(cteamid), synthesisid = synthesisid)
		s = myAPIHelper.get_systems()
		b = myAPIHelper.get_project_bounds()
		t = myAPIHelper.get_synthesis_timeline(teamid = int(cteamid), synthesisid = synthesisid)
		d = myAPIHelper.get_diagrams()

		try:
			assert r.status_code == 200
		except AssertionError as ae:
			print("Invalid reponse %s" % ae)
		else:
			finalsynthesis = json.loads(r.text)
			
		try:
			assert s.status_code == 200
		except AssertionError as ae:
			print("Invalid reponse %s" % ae)
		else:
			systems = json.loads(s.text)
		
		try:
			assert t.status_code == 200
		except AssertionError as ae:
			print("Invalid reponse %s" % ae)
		else:
			timeline = json.loads(t.text)
			timeline = timeline['timeline']

		try:
			assert d.status_code == 200
		except AssertionError as ae:
			print("Invalid reponse %s" % ae)
		else:
			diagrams = json.loads(d.text)
		
		myBagofWordsGenerator = BagofWordsGenerator()
		formattedfinalsynthesis = {"type":"FeatureCollection","features":[]}
		for f in finalsynthesis['features']:
			diagramid = f['properties']['diagramid']
			formattedfeature = f
			formattedfeature['properties']['start'] = timeline[str(diagramid)]['start'].replace('-','/')
			formattedfeature['properties']['end'] = (timeline[str(diagramid)]['end']).replace('-','/')
			formattedfinalsynthesis['features'].append(formattedfeature)
			myBagofWordsGenerator.addtoCorpus(f['properties']['description'])
			myBagofWordsGenerator.addtoCorpusDict(f['properties']['diagramid'],f['properties']['description'])

		bowkey = 'bow-'+ synthesisid
		wordfreq = redis.get(bowkey)
		if wordfreq:
			wordfreq = json.loads(wordfreq)
		else:
			wordfreq = myBagofWordsGenerator.generateBagofWords()
			
			redis.set(bowkey, json.dumps(wordfreq))


		key = 'ss-'+ synthesisid
		ss = redis.get(key)

		if (ss):
			sentenceSimilarity = json.loads(ss)
		else:
			tmpCorpusDict = myBagofWordsGenerator.getOrderedCorpus()
			orderedCorpusDict = OrderedDict(sorted(tmpCorpusDict.items(), key=lambda t: t[0]))
			mySS = SentenceSimilarity()
			mySS.generateSentences(orderedCorpusDict)
			sentenceSimilarity = mySS.doSentenceSimilarity()
			redis.set(key, json.dumps(sentenceSimilarity))
		# sentenceSimilarity ={}
		

		try:
			assert b.status_code == 200
		except AssertionError as ae:
			print("Invalid reponse %s" % ae)
		else:
			bounds = json.loads(b.text)
			bounds = bounds['bounds']
		

		designdata = {'systems':systems ,'synthesis':formattedfinalsynthesis,'bounds':bounds,'wordfreq':wordfreq,'fuzzymatches':sentenceSimilarity,'diagrams':diagrams}
		msg = {"status":1,"message":"Diagrams have been uploaded","data":designdata}
		# return Response(msg, status=400, mimetype='application/json')

	else:
		
		msg = {"status":0, "message":"Could not parse Project ID, Diagram ID or API Token ID. One or more of these were not found in your JSON request."}
		# return Response(msg, status=400, mimetype='application/json')

	return render_template('home.html', op = msg)

if __name__ == '__main__':
	app.debug = True
	port = int(os.environ.get("PORT", 5001))
	app.run(port =5001)
