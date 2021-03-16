from flask import request
from flask_restful import Resource
from semantic_similarity.semantic_similarity import SemanticSimilarity


class QnodeSimilarity(Resource):
    ss = SemanticSimilarity()

    def get(self):
        q1 = request.args.get('q1', None)
        q2 = request.args.get('q2', None)
        embedding_type = request.args.get('embedding_type', None)

        if q1 is None or q2 is None or embedding_type is None:
            return {'error': "q1, q2 and embedding_type cannot be None"}

        return self.ss.semantic_similarity(q1, q2, embedding_type)
