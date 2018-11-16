from flask_restful import Resource, reqparse


class ExpectFeedbackResource(Resource):
    """This resource just sets up the request parser used by the (single) resource in all feedback APIs (which subclass this)."""
    parser = reqparse.RequestParser()
    parser.add_argument('request')
    parser.add_argument('response')
    parser.add_argument('status')
