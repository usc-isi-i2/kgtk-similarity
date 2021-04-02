import faiss
import json

config = json.load(open('semantic_similarity/config.json'))


class FAISS_Index(object):

    def __init__(self, efSearch: int = 400, nprobe: int = 4):
        self.config = config
        self._index = faiss.read_index(self.config['faiss_index_file'])
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

        self._k = k

    def get_neighbors(self, qnode: str, get_scores: bool = False, k: int = 5):
        ''' Find the neighbors for the given qnode '''
        scores, candidates = self._index.search(self._index.reconstruct(self._qnode_to_index[qnode]).reshape(1, -1), k)
        candidates = [self._index_to_qnode[x] for x in candidates[0] if x != -1]
        scores = scores[0][:len(candidates)]

        if get_scores:
            return [(c, s) for c, s in zip(candidates, scores)]
        return candidates

    @property
    def index(self):
        return self._index
