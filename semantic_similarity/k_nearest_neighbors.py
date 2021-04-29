import faiss
import json
from semantic_similarity.utility import Utility

config = json.load(open('semantic_similarity/config.json'))


class FAISS_Index(object):

    def __init__(self, efSearch: int = 400, nprobe: int = 8):
        self.config = config
        if config['faiss_index_file'] != "":
            self._index = faiss.read_index(self.config['faiss_index_file'])
            self.util = Utility()
            try:
                # Set the parameters
                faiss.downcast_index(self._index.quantizer).hnsw.efSearch = efSearch
                self._index.nprobe = nprobe
            except Exception as e:
                print(e)
                print('Cannot set parameters for this index')

            # Load the entity to index map
            with open(self.config['qnode_to_ids_file']) as fd:
                self._qnode_to_index = json.load(fd)
            self._index_to_qnode = {v: k for k, v in self._qnode_to_index.items()}

    def get_neighbors(self, qnode: str, k: int = 5):
        ''' Find the neighbors for the given qnode '''

        # faiss returns the same qnode as first result
        k += 1
        scores, candidates = self._index.search(self._index.reconstruct(self._qnode_to_index[qnode]).reshape(1, -1), k)
        candidates = [self._index_to_qnode[x] for x in candidates[0] if x != -1]
        scores = scores[0][:len(candidates)]
        scores = [float(x) for x in scores][1:]
        candidates = candidates[1:]

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

    @property
    def index(self):
        return self._index
