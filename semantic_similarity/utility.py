import json
import requests
import numpy as np
from typing import List
from functools import lru_cache

import semantic_similarity.kypher as kypher


config = json.load(open('semantic_similarity/config.json'))
embeddings_to_index_field = {
    "complex": "graph_embedding_complex",
    "text": "text_embedding",
    "transe": "graph_embeddings_transe",
    "class": "class_count"
}


class Utility(object):
    
    def __init__(self):
        self.config = config
        # the initial version 1 uses the ElasticSearch backend:
        self.api_version_1 = str(self.config.get('api_version')) == '1'
        self.backend = kypher.get_synced_backend()

    def get_qnode_details_via_es(self, qnodes: List[str], labels_only=False) -> dict:
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
                                # this should be more efficient than doing it by hand:
                                # TO DO: test with float32 here which should be sufficient
                                embedding = np.fromstring(embedding, dtype=float, sep=',')
                            else:
                                embedding = np.array([float(x) for x in embedding])
                            qnodes_dict[qnode][k] = embedding
                if 'labels' in _source:
                    _labels = _source['labels']
                    if 'en' in _labels:
                        label = _labels['en'][0]
                    qnodes_dict[qnode]['label'] = label

        return qnodes_dict

    def normalize_label(self, label):
        # TO DO: generalize this, currently assumes an LQ-string with an @en suffix:
        return label[1:-4] if label is not None else ''

    def get_qnode_details_via_kypher(self, qnodes: List[str], labels_only=False) -> dict:
        """Assembles the same data as 'get_qnode_details_via_es', but faster.
        """
        qnodes_dict = {}
        for qnode in qnodes:
            label = self.backend.get_node_label(qnode)
            if label:
                qnodes_dict[qnode] = {'label': self.normalize_label(label)}
            if labels_only:
                continue

            for info_key in embeddings_to_index_field.keys():
                if info_key == "class":
                    counts = self.backend.get_class_counts_compact(qnode)
                    if counts:
                        qnodes_dict.setdefault(qnode, {})[info_key] = counts
                else:
                    embed = self.backend.get_node_embedding(qnode, info_key)
                    if embed is not None:
                        qnodes_dict.setdefault(qnode, {})[info_key] = embed
        return qnodes_dict

    # full cache of this size will occupy about 3GB of RAM (or half of that if we go to float32);
    # we use a class method to make sure we have exactly one cache, not one per instance
    # (lru_cache is thread-safe according to its source):
    @classmethod
    @lru_cache(maxsize=config['LRU_CACHE_SIZE'])
    def get_qnode_details_cache(self, qnode, labels_only=False):
        """Support per-node caching by returning a cache entry that can be modified outside.
        This primarily exists to provide a size-limited cache facility on a per-node basis.
        """
        return [qnode, None]

    def get_qnode_details(self, qnodes: List[str], labels_only=False) -> dict:
        """LRU-caching version of 'get_qnode_details_via_es/kypher'.  Only looks up those nodes
        in 'qnodes' for which we currently don't have a cached version and LRU-caches them.
        Otherwise returns the exact same data structure as 'get_qnode_details_via_es/kypher'.
        """
        all_caches = []
        new_caches = []
        for qnode in qnodes:
            cache = self.get_qnode_details_cache(qnode, labels_only=labels_only)
            if cache[1] is None:
                new_caches.append(cache)
            all_caches.append(cache)
        if len(new_caches) > 0:
            if self.api_version_1:
                qnodes_dict = self.get_qnode_details_via_es([x[0] for x in new_caches], labels_only=labels_only)
            else:
                qnodes_dict = self.get_qnode_details_via_kypher([x[0] for x in new_caches], labels_only=labels_only)
            for cache in new_caches:
                # make sure to not break if we didn't get any result for a node;
                # we mark those with {} so we don't try to look them up again:
                cache[1] = qnodes_dict.get(cache[0], {})
        return {qnode: info for qnode, info in all_caches if info}


def cosine_similarity(x, y):
    """Faster version of cosine similarity that does not do any arg checking
    and expects two 1 or 2-dim numpy arrays as input.
    """
    # dwim 1-dim vectors to single-element 2-dim views:
    if x.ndim == 1:
        x = x.reshape(1, -1)
    if y.ndim == 1:
        y = y.reshape(1, -1)
    xnorm = x / np.linalg.norm(x, axis=1, keepdims=True)
    ynorm = y / np.linalg.norm(y, axis=1, keepdims=True)
    # TO DO: possibly coerce to full float type here:
    return np.matmul(xnorm, ynorm.T)
