from flask import request
from flask_restful import Resource
from semantic_similarity.semantic_similarity import SemanticSimilarity
from semantic_similarity.k_nearest_neighbors import FAISS_Index
import pandas as pd
from semantic_similarity.utility import Utility


# from semantic_similarity.paths import KGTKPaths


class QnodeSimilarity(Resource):
    ss = SemanticSimilarity()
    valid_similarity_types = list(ss.CONFIGURED_SIMILARITY_TYPES.keys())
    utils = Utility()
    debug_requests = utils.config.get('debug_requests', False)

    def get(self):
        q1 = request.args.get('q1', None)
        q2 = request.args.get('q2', None)
        similarity_type = request.args.get('similarity_type', None) or request.args.get('embedding_type', None)

        if q1 is None or q2 is None or similarity_type is None:
            return {'error': "q1, q2 and similarity_type cannot be None"}

        if similarity_type not in self.valid_similarity_types:
            return {'error': f"similarity_type should be one of {self.valid_similarity_types}"}

        if self.debug_requests:
            print(f'QnodeSimilarity.get: {q1} {q2} {similarity_type}')
        return self.ss.semantic_similarity(q1, q2, similarity_type)

    # restrict the content one can ask about in a single request:
    file_max_lines = utils.config.get('file_api_max_lines', 100)

    def post(self):
        column1 = request.args.get('column1', "q1")
        column2 = request.args.get('column2', "q2")
        add_labels = request.args.get('add_labels', "true").lower() == 'true'
        file_format = request.args.get('file_type', "tsv")
        sim_types = request.args.get('similarity_types', "all").split(',')
        sim_types = [st for st in self.valid_similarity_types if st in sim_types or 'all' in sim_types]

        input_file = request.files.get('file', None)
        if input_file is None:
            return {'error': 'no file provided'}

        if file_format == 'tsv':
            df = pd.read_csv(input_file, dtype=object, sep='\t')
        else:
            df = pd.read_csv(input_file, dtype=object)

        df.fillna('', inplace=True)
        if self.debug_requests:
            print(f'QnodeSimilarity.post: {sim_types} {df}')

        qnode_truples = list(zip(df[column1], df[column2]))
        r = []
        for i, qnode_truple in enumerate(qnode_truples):
            if i >= self.file_max_lines:
                break
            q1 = qnode_truple[0]
            q2 = qnode_truple[1]
            scores = {
                column1: q1,
                column2: q2,
            }
            for sim_type in sim_types:
                _ = self.ss.semantic_similarity(q1, q2, sim_type)
                ok = 'error' not in _
                scores[sim_type] = _['similarity'] if ok else ''
                if add_labels:
                    scores[f'{column1}_label'] = _.get('q1_label')
                    scores[f'{column2}_label'] = _.get('q2_label')
            r.append(scores)

        rdf = pd.DataFrame(r)
        # TO DO: streamline return type, since this generates a string instead of a dict:
        return df.merge(rdf, on=[column1, column2]).to_json(orient='records')


class NN(Resource):
    ss = SemanticSimilarity()
    utils = Utility()
    api_version_1 = utils.api_version_1
    fi = FAISS_Index()

    valid_similarity_types = list(ss.CONFIGURED_SIMILARITY_TYPES.keys())
    valid_nn_similarity_types = list(ss.CONFIGURED_NN_SIMILARITY_TYPES.keys())

    # restrict the content one can ask about in a single request:
    nn_api_max_k = utils.config.get('nn_api_max_k', 100)
    debug_requests = utils.config.get('debug_requests', False)

    def get(self):
        qnode = request.args.get("qnode")
        similarity_type = request.args.get('similarity_type', self.valid_nn_similarity_types[0])
        if qnode is None:
            return {'error': "The url parameter: 'qnode' is required"}
        if similarity_type not in self.valid_nn_similarity_types:
            if similarity_type not in self.valid_similarity_types:
                return {'error': f"{similarity_type} is not a valid similarity type"}
            return {'error': f"{similarity_type} similarity is not currently supported for nearest neighbor requests"}

        if self.debug_requests:
            print(f'NN.get: {qnode} {similarity_type}')

        k = min(int(request.args.get('k', 5)), self.nn_api_max_k)
        if self.api_version_1:
            return self.fi.get_neighbors(qnode, k=k)
        else:
            return self.ss.get_most_similar(qnode, similarity_type, topn=k) or []

# class Paths(Resource):
#     kgp = KGTKPaths()
#
#     def get(self):
#         source = request.args.get("source", None)
#         target = request.args.get("target", None)
#         max_hops = int(request.args.get("hops", 2))
#         add_labels = request.args.get("labels", "false").strip().lower() == 'true'
#
#         if source is None or target is None:
#             return {"error": "source and target both required"}
#         if max_hops > 4:
#             return {"error": "Maximum hops can not be greater than 4"}
#         return self.kgp.compute_paths(source, target, max_hops=max_hops, add_labels=add_labels)
