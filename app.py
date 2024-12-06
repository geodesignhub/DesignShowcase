#!/usr/bin/env python3

from flask import render_template
from flask import request, Response
import GeodesignHub
import config
import json
import utils
import os
from loguru import logger
import logging
from rq import Queue, Callback
from worker import conn
from notifications_helper import report_failure, report_success
from conn import get_redis
from showcase import create_app
import uuid

redis = get_redis()

q = Queue(connection=conn)

MIMETYPE = "application/json"


# Imports
# create a custom handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


app, babel = create_app()
app.logger.addHandler(InterceptHandler())


@app.route("/get_sentence_similarity", methods=["GET"])
def get_sentence_similarity():
    synthesis_id = request.args.get("synthesis_id", "0")
    
    synthesis_key = "ss-" + synthesis_id
    synthesis_exists = redis.exists(synthesis_key)
    if synthesis_exists:
        s = redis.get(synthesis_key)
        sentence_similarity = json.loads(s)
    else:
        sentence_similarity = {}
    print(sentence_similarity)
    return Response(json.dumps(sentence_similarity), status=200, mimetype=MIMETYPE)


@app.route("/", methods=["GET"])
def api_root():
    """This is the root of the web service, upon successful authentication a text will be displayed in the browser"""

    session_id = str(uuid.uuid4())
    try:
        projectid = request.args.get("projectid")
        design_team_id = request.args.get("cteamid")
        api_token = request.args.get("apitoken")
        synthesis_id = request.args.get("synthesisid")

    except KeyError:
        msg = json.dumps(
            {
                "message": "Could not parse Projectid, Diagram ID or API Token ID. One or more of these were not found in your JSON request."
            }
        )
        return Response(msg, status=400, mimetype="application/json")

    if projectid and design_team_id and api_token and synthesis_id:
        # Initialize the API
        my_api_helper = GeodesignHub.GeodesignHubClient(
            url=config.apisettings["serviceurl"], project_id=projectid, token=api_token
        )
        # Download Data
        r = my_api_helper.get_single_synthesis(
            teamid=int(design_team_id), synthesisid=synthesis_id
        )
        s = my_api_helper.get_all_systems()
        b = my_api_helper.get_project_bounds()

        all_diagrams_key = projectid + "-all-diagrams"
        all_diagrams_str = redis.get(all_diagrams_key)

        if all_diagrams_str:
            diagrams = json.loads(all_diagrams_str)
        else:

            d = my_api_helper.get_all_diagrams()
            try:
                assert d.status_code == 200
            except AssertionError:
                return Response(
                    "Error in getting diagram data from Geodesignhub",
                    status=400,
                )
            else:
                redis.set(all_diagrams_key, d.text)
                diagrams = json.loads(d.text)

        # Check responses / data
        try:
            assert r.status_code == 200
        except AssertionError:
            return Response(
                "Error in getting synthesis data from Geodesignhub",
                status=400,
            )
        else:
            final_synthesis = json.loads(r.text)

        try:
            assert s.status_code == 200
        except AssertionError:
            return Response(
                "Error in getting systems data from Geodesignhub",
                status=400,
            )
        else:
            systems = json.loads(s.text)

        try:
            assert b.status_code == 200
        except AssertionError:
            return Response(
                "Error in getting bounds data from Geodesignhub",
                status=400,
            )
        else:
            bounds = json.loads(b.text)
            bounds = bounds["bounds"]
        # Loop over features and add to corpus and Corpus Dictionary
        my_bag_of_words_generator = utils.BagofWordsGenerator()
        formatted_final_synthesis = {"type": "FeatureCollection", "features": []}
        for f in final_synthesis["features"]:

            diagram_id = f["properties"]["diagramid"]
            diagram_name = f["properties"]["description"]
            try:
                notes = f["properties"]["notes"]
            except KeyError:
                notes = None
            formatted_feature = f
            formatted_final_synthesis["features"].append(formatted_feature)
            my_bag_of_words_generator.add_to_corpus(diagram_name)
            if notes:
                my_bag_of_words_generator.add_to_corpus(notes)
            my_bag_of_words_generator.add_to_corpus_dict(diagram_id, diagram_name)
        # Store / Cache in Redis
        bow_key = "bow-" + synthesis_id
        word_frequency = redis.get(bow_key)
        if word_frequency:
            word_frequency = json.loads(word_frequency)
        else:
            word_frequency = my_bag_of_words_generator.generate_bag_of_words()

            redis.set(bow_key, json.dumps(word_frequency))

        key = "ss-" + synthesis_id
        ss = redis.get(key)

        if ss:
            sentence_similarity = json.loads(ss)
        else:
            temporary_corpus_dictionary = my_bag_of_words_generator.get_ordered_corpus()
            result = q.enqueue(
                utils.create_sentence_similarity,
                {
                    "data": temporary_corpus_dictionary,
                    "key": key,
                    "session_id": session_id,
                },
                on_success=Callback(report_success),
                on_failure=Callback(report_failure),
                job_id=session_id,
            )

            sentence_similarity = {}

        design_data = {
            "synthesis_id": synthesis_id,
            "session_id": session_id,
            "systems": systems,
            "synthesis": formatted_final_synthesis,
            "bounds": bounds,
            "word_frequency": word_frequency,
            "fuzzy_matches": sentence_similarity,
            "diagrams": diagrams,
        }
        msg = {
            "status": 1,
            "message": "Diagrams have been uploaded",
            "data": design_data,
        }

    else:

        msg = {
            "status": 0,
            "message": "Could not parse Project ID, Diagram ID or API Token ID. One or more of these were not found in your JSON request.",
        }

    return render_template("home.html", op=msg)


if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5001))
    app.run(port=5001)
