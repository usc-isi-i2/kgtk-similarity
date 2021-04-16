import json
import requests
import numpy as np
from typing import List

config = json.load(open('semantic_similarity/config.json'))
embeddings_to_index_field = {
    "complex": "graph_embedding_complex",
    "text": "text_embedding",
    "transe": "graph_embeddings_transe",
    "class": "class_count"
}


class Utility(object):
    config = config

    def get_embeddings_and_label(self, qnode, embeddings_type):
        es_search_url = f"{self.config['es_url']}/{self.config['es_index']}/_doc/{qnode}"
        qnode_result = requests.get(es_search_url).json()
        embedding = None
        label = ''
        qnode_dict = {}
        if '_source' in qnode_result and embeddings_to_index_field[embeddings_type] in qnode_result['_source']:
            embedding = qnode_result['_source'][embeddings_to_index_field[embeddings_type]]

            if isinstance(embedding, str):
                embedding = embedding.split(",")
            embedding = np.array([float(x) for x in embedding])

            _labels = qnode_result['_source']['labels']
            if 'en' in _labels:
                label = _labels['en'][0]

        qnode_dict['embedding'] = embedding
        qnode_dict['label'] = label
        return qnode_dict

    def get_labels(self, qnodes: List[str]):
        _ = {}
        ids_query = {
            "_source": ["labels.en"],
            "query": {
                "ids": {
                    "values": qnodes
                }
            },
            "size": len(qnodes)
        }

        es_search_url = f"{self.config['es_url']}/{self.config['es_index']}/_search"
        results = requests.post(es_search_url, json=ids_query).json()
        if "hits" in results:
            hits = results['hits']['hits']
            for hit in hits:
                try:
                    _[hit['_id']] = hit['_source']['labels']['en'][0]
                except:
                    _[hit['_id']] = ''
        return _

    def get_class_counts(self, qnode1: str, qnode2: str) -> (dict, dict):
        cc_dict = {}
        labels_dict = {}
        ids_query = {
            "_source": ["class_count", "labels.en"],
            "query": {
                "ids": {
                    "values": [qnode1, qnode2]
                }
            },
            "size": 2
        }

        es_search_url = f"{self.config['es_url']}/{self.config['es_index']}/_search"
        results = requests.post(es_search_url, json=ids_query).json()
        if "hits" in results:
            hits = results['hits']['hits']
            for hit in hits:
                try:
                    cc_dict[hit['_id']] = hit['_source']['class_count']
                except:
                    print('no class_count for: {}'.format(hit['_id']))

                try:
                    labels_dict[hit['_id']] = hit['_source']['labels']['en'][0]
                except:
                    labels_dict[hit['_id']] = ''
        return cc_dict, labels_dict
