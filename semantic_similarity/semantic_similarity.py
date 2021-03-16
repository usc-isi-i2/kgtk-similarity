import json
import requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

config = json.load(open('semantic_similarity/config.json'))

embeddings_to_index = {
    "complex": config['complex_ge_index'],
    "text": config['text_embeddings_index']
}


class SemanticSimilarity(object):
    def __init__(self):
        self.config = config

    def semantic_similarity(self, q1: str, q2: str, embeddings_type: str):

        q1_embeddings = self.get_embeddings(q1, embeddings_type)
        q2_embeddings = self.get_embeddings(q2, embeddings_type)
        if q1_embeddings is None:
            return {'error': f"The qnode: {q1} is not present in DWD"}

        if q2_embeddings is None:
            return {'error': f"The qnode: {q2} is not present in DWD"}

        if embeddings_type == 'complex':
            return {
                'similarity': np.dot(q1_embeddings, q2_embeddings),
                'q1': q1,
                'q1_label': self.get_label(q1),
                'q2': q2,
                'q2_label': self.get_label(q2)
            }
        if embeddings_type == 'text':
            return {
                'similarity': cosine_similarity(q1_embeddings.reshape(1, -1), q2_embeddings.reshape(1, -1))[0][0],
                'q1': q1,
                'q1_label': self.get_label(q1),
                'q2': q2,
                'q2_label': self.get_label(q2)
            }

    def get_embeddings(self, qnode, embeddings_type):
        es_search_url = f"{self.config['es_url']}/{embeddings_to_index[embeddings_type]}/_doc/{qnode}"
        qnode_result = requests.get(es_search_url).json()
        embedding = None
        if '_source' in qnode_result:
            embedding = qnode_result['_source']['embedding']

            if isinstance(embedding, str):
                embedding = embedding.split(" ")
            embedding = np.array([float(x) for x in embedding])
        return embedding

    def get_label(self, qnode):
        es_search_url = f"{self.config['es_url']}/{self.config['labels_index']}/_doc/{qnode}"
        qnode_doc = requests.get(es_search_url).json()
        label = ''
        if '_source' in qnode_doc:
            _labels = qnode_doc['_source']['labels']
            if 'en' in _labels:
                label = _labels['en'][0]
        return label


ss = SemanticSimilarity()
print(json.dumps(ss.semantic_similarity('Q76', 'Q30', 'complex')))
