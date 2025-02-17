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




@app.route("/", methods=["GET"])
def api_root():
    """This is the root of the web service, upon successful authentication a text will be displayed in the browser"""

    session_id = str(uuid.uuid4())
    projectid, design_team_id, api_token, synthesis_id = get_request_args()

    if not all([projectid, design_team_id, api_token, synthesis_id]):
        return error_response("Could not parse Project ID, Diagram ID or API Token ID. One or more of these were not found in your JSON request.")

    my_api_helper = GeodesignHub.GeodesignHubClient(
        url=config.apisettings["serviceurl"], project_id=projectid, token=api_token
    )

    r, s, b, diagrams = fetch_data(my_api_helper, projectid, design_team_id, synthesis_id)

    if not all([r, s, b, diagrams]):
        return error_response("Error in getting data from Geodesignhub")

    final_synthesis, systems, bounds = parse_responses(r, s, b)

    formatted_final_synthesis, word_frequency = process_synthesis(final_synthesis, synthesis_id, diagrams)

    design_data = {
        "synthesis_id": synthesis_id,
        "session_id": session_id,
        "systems": systems,
        "synthesis": formatted_final_synthesis,
        "bounds": bounds,
        "word_frequency": word_frequency,
        "diagrams": diagrams,
    }

    msg = {
        "status": 1,
        "message": "Diagrams have been uploaded",
        "data": design_data,
    }

    return render_template("home.html", op=msg)


def get_request_args():
    try:
        projectid = request.args.get("projectid")
        design_team_id = request.args.get("cteamid")
        api_token = request.args.get("apitoken")
        synthesis_id = request.args.get("synthesisid")
        return projectid, design_team_id, api_token, synthesis_id
    except KeyError:
        return None, None, None, None


def error_response(message):
    msg = json.dumps({"message": message})
    return Response(msg, status=400, mimetype="application/json")


def fetch_data(api_helper, projectid, design_team_id, synthesis_id):
    try:
        r = api_helper.get_single_synthesis(teamid=int(design_team_id), synthesisid=synthesis_id)
        s = api_helper.get_all_systems()
        b = api_helper.get_project_bounds()
        diagrams = get_diagrams(api_helper, projectid)
        return r, s, b, diagrams
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None, None, None, None


def get_diagrams(api_helper, projectid):
    all_diagrams_key = projectid + "-all-diagrams"
    all_diagrams_str = redis.get(all_diagrams_key)

    if all_diagrams_str:
        return json.loads(all_diagrams_str)
    else:
        d = api_helper.get_all_diagrams()
        if d.status_code == 200:
            redis.set(all_diagrams_key, d.text)
            return json.loads(d.text)
        else:
            return None


def parse_responses(r, s, b):
    try:
        final_synthesis = json.loads(r.text) if r.status_code == 200 else None
        systems = json.loads(s.text) if s.status_code == 200 else None
        bounds = json.loads(b.text)["bounds"] if b.status_code == 200 else None
        return final_synthesis, systems, bounds
    except Exception as e:
        logger.error(f"Error parsing responses: {e}")
        return None, None, None


def process_synthesis(final_synthesis, synthesis_id):
    my_bag_of_words_generator = utils.BagofWordsGenerator()
    formatted_final_synthesis = {"type": "FeatureCollection", "features": []}

    for f in final_synthesis["features"]:
        diagram_id = f["properties"]["diagramid"]
        diagram_name = f["properties"]["description"]
        notes = f["properties"].get("notes", None)

        formatted_final_synthesis["features"].append(f)
        my_bag_of_words_generator.add_to_corpus(diagram_name)
        if notes:
            my_bag_of_words_generator.add_to_corpus(notes)
        my_bag_of_words_generator.add_to_corpus_dict(diagram_id, diagram_name)

    bow_key = "bow-" + synthesis_id
    word_frequency = redis.get(bow_key)

    if word_frequency:
        word_frequency = json.loads(word_frequency)
    else:
        word_frequency = my_bag_of_words_generator.generate_bag_of_words()
        redis.set(bow_key, json.dumps(word_frequency))

    return formatted_final_synthesis, word_frequency


if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5001))
    app.run(port=5001)
