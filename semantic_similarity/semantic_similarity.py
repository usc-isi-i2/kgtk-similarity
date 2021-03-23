import json
import requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

config = json.load(open('semantic_similarity/config.json'))

embeddings_to_index_field = {
    "complex": "graph_embedding_complex",
    "text": "text_embedding"
}


class SemanticSimilarity(object):
    def __init__(self):
        self.config = config

    def semantic_similarity(self, q1: str, q2: str, embeddings_type: str):

        q1_result = self.get_embeddings_and_label(q1, embeddings_type)
        q2_result = self.get_embeddings_and_label(q2, embeddings_type)
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

    def get_embeddings_and_label(self, qnode, embeddings_type):
        es_search_url = f"{self.config['es_url']}/{self.config['es_index']}/_doc/{qnode}"
        qnode_result = requests.get(es_search_url).json()
        embedding = None
        label = ''
        qnode_dict = {}
        if '_source' in qnode_result:
            embedding = qnode_result['_source'][embeddings_to_index_field[embeddings_type]]

            if isinstance(embedding, str):
                embedding = embedding.split(" ")
            embedding = np.array([float(x) for x in embedding])

            _labels = qnode_result['_source']['labels']
            if 'en' in _labels:
                label = _labels['en'][0]

        qnode_dict['embedding'] = embedding
        qnode_dict['label'] = label
        return qnode_dict
