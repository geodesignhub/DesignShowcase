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
import utils
import redis
import os
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)

from rq import Queue
from worker import conn

q = Queue(connection=conn)

# Imports


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
		
		myBagofWordsGenerator = utils.BagofWordsGenerator()
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
			result = q.enqueue(utils.createSenteceSimilarity,{'data':tmpCorpusDict,'key':key})
			sentenceSimilarity = {}
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
