import json
from sklearn.metrics.pairwise import cosine_similarity
from semantic_similarity.utility import Utility

config = json.load(open('semantic_similarity/config.json'))


class SemanticSimilarity(object):
    def __init__(self):
        self.config = config
        self.util = Utility()

    def semantic_similarity(self, q1: str, q2: str, embeddings_type: str):

        q1_result = self.util.get_embeddings_and_label(q1, embeddings_type)
        q2_result = self.util.get_embeddings_and_label(q2, embeddings_type)
        if q1_result.get('embedding', None) is None:
            return {'error': f"The qnode: {q1} is not present in DWD"}

        if q2_result.get('embedding', None) is None:
            return {'error': f"The qnode: {q2} is not present in DWD"}

        if embeddings_type == 'complex' or 'text':
            return {
                'similarity': cosine_similarity(q1_result.get('embedding', None).reshape(1, -1),
                                                q2_result.get('embedding', None).reshape(1, -1))[0][0],
                'q1': q1,
                'q1_label': q1_result.get('label'),
                'q2': q2,
                'q2_label': q2_result.get('label')
            }
