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

    def get_qnode_details(self, qnodes: List[str], labels_only=False) -> dict:
        source_fields = ["labels.en"]
        if not labels_only:
            source_fields.extend([embeddings_to_index_field[k] for k in embeddings_to_index_field])

        qnodes_dict = {}
        ids_query = {
            "_source": source_fields,
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
                qnode = hit['_id']
                label = ''
                if qnode not in qnodes_dict:
                    qnodes_dict[qnode] = {}
                _source = hit['_source']
                for k in embeddings_to_index_field:
                    if embeddings_to_index_field[k] in _source:
                        if k == "class":
                            qnodes_dict[qnode][k] = _source[embeddings_to_index_field[k]]
                        else:

                            embedding = _source[embeddings_to_index_field[k]]
                            if isinstance(embedding, str):
                                embedding = embedding.split(",")
                            embedding = np.array([float(x) for x in embedding])
                            qnodes_dict[qnode][k] = embedding
                _labels = _source['labels']
                if 'en' in _labels:
                    label = _labels['en'][0]
                qnodes_dict[qnode]['label'] = label

        return qnodes_dict
