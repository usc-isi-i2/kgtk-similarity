from flask import request
from flask_restful import Resource
from semantic_similarity.semantic_similarity import SemanticSimilarity
from semantic_similarity.k_nearest_neighbors import FAISS_Index
import pandas as pd
import json


class QnodeSimilarity(Resource):
    ss = SemanticSimilarity()
    valid_embedding_types = ['complex', 'text', 'transe']

    def get(self):
        q1 = request.args.get('q1', None)
        q2 = request.args.get('q2', None)
        embedding_type = request.args.get('embedding_type', None)

        if q1 is None or q2 is None or embedding_type is None:
            return {'error': "q1, q2 and embedding_type cannot be None"}

        if embedding_type not in self.valid_embedding_types:
            return {'error': "embedding_type should be one of ['complex', 'text', 'transe']"}

        return self.ss.semantic_similarity(q1, q2, embedding_type)

    def post(self):

        input_file = request.files.get('file', None)
        if input_file is None:
            return {'error': 'no file provided'}

        df = pd.read_csv(input_file, dtype=object, sep='\t')

        df.fillna('', inplace=True)

        qnode_truples = list(zip(df.q1, df.q2))
        r = []
        for qnode_truple in qnode_truples:
            q1 = qnode_truple[0]
            q2 = qnode_truple[1]
            scores = {
                'q1': q1,
                'q2': q2,
                'complex': '',
                'transe': '',
                'text': ''
            }
            for embedding_type in self.valid_embedding_types:
                _ = self.ss.semantic_similarity(q1, q2, embedding_type)
                if 'error' not in _:
                    scores[embedding_type] = _['similarity']
            r.append(scores)

        return r


class NN(Resource):
    fi = FAISS_Index()

    def get(self):
        qnode = request.args.get("qnode")
        if qnode is None:
            return {'error': "The url parameter: 'qnode' required"}

        k = int(request.args.get('k', 5))
        return self.fi.get_neighbors(qnode, k=k)
