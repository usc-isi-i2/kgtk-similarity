import faiss
import json

from semantic_similarity.utility import Utility
import semantic_similarity.kypher as kypher

config = json.load(open('semantic_similarity/config.json'))


class FAISS_Index(object):

    # make the actual index objects a singleton, so we don't load them multiple times:
    _index = None
    _qnode_to_index = None
    _index_to_qnode = None

    DEFAULT_INDEX_NPROBE = 64
    DEFAULT_INDEX_HNSW_SEARCH_DEPTH = 128

    def __init__(self, efSearch: int = None, nprobe: int = None):
        self.config = config
        self.util = Utility()
        self.api_version_1 = self.util.api_version_1
        self.backend = kypher.get_synced_backend()

        efSearch = efSearch or 400 if self.api_version_1 else self.DEFAULT_INDEX_HNSW_SEARCH_DEPTH
        nprobe = nprobe or 8 if self.api_version_1 else self.DEFAULT_INDEX_NPROBE

        # TO DO: make this a constructor parameter, since eventually we'll have multiple indexes:
        index_file = config['faiss_index_file'] if self.api_version_1 else config.get("COMPLEX_EMB_FAISS_INDEX")
        if self._index is None and index_file:
            print('Loading FAISS index...')
            FAISS_Index._index = faiss.read_index(index_file)
            try:
                # Set the parameters
                faiss.downcast_index(self._index.quantizer).hnsw.efSearch = efSearch
                self._index.nprobe = nprobe
            except Exception as e:
                print(e)
                print('Cannot set parameters for this index')

            if self.api_version_1:
                # Load the entity to index map
                with open(self.config['qnode_to_ids_file']) as fd:
                    FAISS_Index._qnode_to_index = json.load(fd)
                FAISS_Index._index_to_qnode = {v: k for k, v in self._qnode_to_index.items()}

    def get_neighbors_v1(self, qnode: str, k: int = 5):
        ''' Find the neighbors for the given qnode '''

        # faiss returns the same qnode as first result
        k += 1
        scores, candidates = self._index.search(self._index.reconstruct(self._qnode_to_index[qnode]).reshape(1, -1), k)
        candidates = [self._index_to_qnode[x] for x in candidates[0] if x != -1]
        scores = scores[0][:len(candidates)]
        scores = [float(x) for x in scores][1:]
        candidates = candidates[1:]

        # this takes the most time for larger values of 'k', so speeding up that part
        # and maybe restricting to embedding types we actually need would help:
        candidates_label_dict = self.util.get_qnode_details(candidates)

        result = []

        tuples = [(c, s) for c, s in zip(candidates, scores)]
        for t in tuples:
            _qnode = t[0]
            score = t[1]
            label = candidates_label_dict.get(_qnode, {}).get('label', '')
            result.append({
                "qnode": _qnode,
                "score": score,
                "label": label
            })
        return result

    def get_neighbors(self, qnode: str, k: int = 5):
        """Find the top-k nearest neighbors for the given 'qnode'.
        """
        if self.api_version_1:
            return self.get_neighbors_v1(qnode, k=k)

        result = []
        embed = self.backend.get_node_embedding(qnode, 'complex')
        if embed is None:
            return result

        # NOTE: faiss returns the identical 'qnode' as the first result:
        scores, candidates = self._index.search(embed.reshape(1, -1), k + 1)
        for i, (cand, score) in enumerate(zip(candidates[0], scores[0])):
            if i > 0 and cand != -1:
                for node, numid, label in self.backend.get_node_and_label_from_complex_emb_numid(cand):
                    result.append({"qnode": node, "score": score, "label": self.util.normalize_label(label)})
                    break
        return result

    @property
    def index(self):
        return self._index
