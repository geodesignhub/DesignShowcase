from showcase import create_app
from flask_sse import sse
import time
from loguru import logger




def report_success(job, connection, result, *args, **kwargs):

    job_id = job.id
    app, babel = create_app()
    with app.app_context():
        sse.publish({"sentence_similarity_key": job_id}, type="sentence_similarity_complete")

def report_failure(job, connection, result, *args, **kwargs):
    logger.info("Job with %s failed.." % str(job.id))

