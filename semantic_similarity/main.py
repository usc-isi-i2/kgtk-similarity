from flask import request
from flask_restful import Resource
from semantic_similarity.semantic_similarity import SemanticSimilarity
from semantic_similarity.k_nearest_neighbors import FAISS_Index


class QnodeSimilarity(Resource):
    ss = SemanticSimilarity()

    def get(self):
        q1 = request.args.get('q1', None)
        q2 = request.args.get('q2', None)
        embedding_type = request.args.get('embedding_type', None)

        if q1 is None or q2 is None or embedding_type is None:
            return {'error': "q1, q2 and embedding_type cannot be None"}

        if embedding_type not in ['complex', 'text', 'transe']:
            return {'error': "embedding_type should be one of ['complex', 'text', 'transe']"}

        return self.ss.semantic_similarity(q1, q2, embedding_type)


class NN(Resource):
    fi = FAISS_Index()

    def get(self):
        qnode = request.args.get("qnode")
        if qnode is None:
            return {'error': "The url parameter: 'qnode' required"}

        k = int(request.args.get('k', 5))
        return self.fi.get_neighbors(qnode, get_scores=True, k=k)
