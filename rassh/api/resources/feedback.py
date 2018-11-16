from rassh.api.resources import ExpectFeedbackResource

import logging

# You're probably using this for debugging, right?
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Feedback(ExpectFeedbackResource):
    """This resource is a generic endpoint for expect APIs to post feedback. It's probably not useful in production
    (you're more likely to want rassh.api.resources.postgres_feeback for that) but may help you with debugging when
    first writing a new API with rassh."""

    def post(self):
        args = Feedback.parser.parse_args()
        request = args['request']
        response = args['response']
        status = args['status']
        # Now, if this were a real system, we'd take this information and use it to update our local state somehow.
        # See PostgresFeedback (with BonairePostgresFeedback) for an example.
        response_string = request + " " + str(response) + " " + str(status) + " OK"
        logger.debug(response_string)
        return response_string, 204
