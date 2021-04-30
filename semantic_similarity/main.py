from flask import request
from flask_restful import Resource
from semantic_similarity.semantic_similarity import SemanticSimilarity
from semantic_similarity.k_nearest_neighbors import FAISS_Index
import pandas as pd
from semantic_similarity.utility import Utility
from semantic_similarity.paths import KGTKPaths


class QnodeSimilarity(Resource):
    ss = SemanticSimilarity()
    valid_embedding_types = ['complex', 'text', 'transe', 'class']
    utils = Utility()

    def get(self):
        q1 = request.args.get('q1', None)
        q2 = request.args.get('q2', None)
        embedding_type = request.args.get('embedding_type', None)

        if q1 is None or q2 is None or embedding_type is None:
            return {'error': "q1, q2 and embedding_type cannot be None"}

        if embedding_type not in self.valid_embedding_types:
            return {'error': "embedding_type should be one of ['complex', 'text', 'transe', 'class']"}

        return self.ss.semantic_similarity(q1, q2, embedding_type)

    def post(self):
        column1 = request.args.get('column1', "q1")
        column2 = request.args.get('column2', "q2")
        add_labels = request.args.get('add_labels', "true").lower() == 'true'
        file_format = request.args.get('file_type', "tsv")

        input_file = request.files.get('file', None)
        if input_file is None:
            return {'error': 'no file provided'}

        if file_format == 'tsv':
            df = pd.read_csv(input_file, dtype=object, sep='\t')
        else:
            df = pd.read_csv(input_file, dtype=object)

        df.fillna('', inplace=True)

        qnode_truples = list(zip(df[column1], df[column2]))
        r = []
        for qnode_truple in qnode_truples:
            q1 = qnode_truple[0]
            q2 = qnode_truple[1]
            scores = {
                column1: q1,
                column2: q2,
                'complex': '',
                'transe': '',
                'text': '',
                'class': ''
            }
            for embedding_type in self.valid_embedding_types:
                _ = self.ss.semantic_similarity(q1, q2, embedding_type)
                if 'error' not in _:
                    scores[embedding_type] = _['similarity']
                if add_labels:
                    scores[f'{column1}_label'] = _.get('q1_label')
                    scores[f'{column2}_label'] = _.get('q2_label')
            r.append(scores)

        rdf = pd.DataFrame(r)
        return df.merge(rdf, on=[column1, column2]).to_json(orient='records')


class NN(Resource):
    fi = FAISS_Index()

    def get(self):
        qnode = request.args.get("qnode")
        if qnode is None:
            return {'error': "The url parameter: 'qnode' required"}

        k = int(request.args.get('k', 5))
        return self.fi.get_neighbors(qnode, k=k)


class Paths(Resource):
    kgp = KGTKPaths()

    def get(self):
        source = request.args.get("source", None)
        target = request.args.get("target", None)
        max_hops = int(request.args.get("hops", 2))

        if source is None or target is None:
            return {"error": "source and target both required"}
        return self.kgp.compute_paths(source, target, max_hops=max_hops)
