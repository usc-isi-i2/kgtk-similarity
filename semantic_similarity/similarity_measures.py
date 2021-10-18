"""
Standardized API for a number of different similarity measures.
"""

import math
import statistics
import json
from   functools import lru_cache

import numpy as np
import pandas as pd

from   semantic_similarity.utility import Utility, cosine_similarity
import semantic_similarity.kypher as kypher
from   semantic_similarity.k_nearest_neighbors import FAISS_Index

config = json.load(open('semantic_similarity/config.json'))


class SimilarityMeasure(object):
    """API class wrapping 'legacy' similarity computations provided by
    'semantic_similarity' and additional measures extending them.
    """
    
    def __init__(self, embedding_type=None):
        self.config = config
        self.util = Utility()
        self.api_version_1 = self.util.api_version_1
        self.backend = kypher.get_synced_backend()
        self.embedding_type = embedding_type

    def compute_similarity(self, c1, c2):
        return self.compute_pairwise_similarities([(c1, c2)])[0]

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        This is a bulk-computation method aimed at minimizing server round trips and
        maximizing vectorized computations.  This is the core method that needs to be
        implemented by subclasses, others will be simulated if not available, but should
        be implemented if they can achieve better performance.
        """
        raise Exception('Not implemented')

    def compute_pairwise_embedding_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        This calls out to precomputed embeddings hosted on ElasticSearch server/Kypher.
        """
        qnodes = set([p[0] for p in pairs])
        qnodes.update([p[1] for p in pairs])
        qnode_dict = self.util.get_qnode_details(list(qnodes))
        # this is slightly more complex, because we want to perform the distance
        # computations in a single efficient vectorized call instead of one-by-one:
        emb_shape = None
        for info in qnode_dict.values():
            emb = info.get(self.embedding_type)
            if emb is not None:
                emb_shape = emb.shape
                break
        if emb_shape is None:
            return [0.0] * len(pairs)
        oppo1, oppo2 = np.ones(emb_shape), np.ones(emb_shape) * -1
        emb1s, emb2s = [], []
        for q1, q2 in pairs:
            if q1 in qnode_dict and q2 in qnode_dict:
                emb1 = qnode_dict[q1].get(self.embedding_type)
                emb2 = qnode_dict[q2].get(self.embedding_type)
                if emb1 is not None and emb2 is not None:
                    emb1s.append(emb1)
                    emb2s.append(emb2)
                    continue
            # force 0.0 similarity for this pair with vectors in opposite directions:
            emb1s.append(oppo1)
            emb2s.append(oppo2)
        # map negative similarities which represent anti-correlation of some kind onto 0:
        # TO DO: clean up float coercion
        sims = [max(float(cosine_similarity(e1, e2)[0][0]), 0.0) for e1, e2 in zip(emb1s, emb2s)]
        return sims

    def compute_node_similarities(self, node, others):
        """Compute similarities between 'node' and 'others' and return the result as a list.
        This is a bulk-computation similar to 'compute_pairwise_similarities' but aimed
        at comparing a single 'node' to many potential neighbors.
        """
        return self.compute_pairwise_similarities([(node, other) for other in others])

    def compute_node_embedding_similarities(self, node, others):
        """Compute embedding similarities between 'node' and 'others' and return the result as a list.
        This is a bulk-computation similar to 'compute_pairwise_embedding_similarities' but aimed
        at comparing a single 'node' to many potential neighbors.
        """
        if self.api_version_1:
            return self.compute_pairwise_embedding_similarities([(node, other) for other in others])
        if not others:
            return []
        nodeemb = self.backend.get_node_embedding(node, self.embedding_type)
        if nodeemb is None:
            return [0.0] * len(others)
        otherembs = self.backend.get_node_embeddings(others, self.embedding_type)
        # if emb is undefined, force a negative sim by using -nodeemb:
        otherembs = [emb if emb is not None else -nodeemb for emb in otherembs]
        sims = cosine_similarity(nodeemb, np.array(otherembs))[0]
        # map negative similarities which represent anti-correlation of some kind onto 0:
        # TO DO: clean up float coercion
        sims = [max(float(sim), 0.0) for sim in sims]
        return sims
    
    def get_most_similar_df(self, c, topn=20):
        return None

    def get_most_similar(self, c, topn=20):
        return []


class ClassSimilarity(SimilarityMeasure):
    """
    Class similarity computations.
    Most of this was moved here from the original version in 'SemanticSimilarity'.
    """
    
    EMBEDDING_KEY = 'class'

    def __init__(self, *args, **kwdargs):
        super().__init__(*args, embedding_type=self.EMBEDDING_KEY, **kwdargs)
        #self.N = float(42123553)
        self.N = self.backend.get_max_class_count()

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        qnodes = set([p[0] for p in pairs])
        qnodes.update([p[1] for p in pairs])
        qnode_dict = self.util.get_qnode_details(list(qnodes))
        similarities = []
        for q1, q2 in pairs:
            sim = 0.0
            if q1 in qnode_dict and q2 in qnode_dict:
                # just extract the sim-value and discard the info components such as labels;
                # NOTE that we can get empty strings here, thus the 'or':
                sim = self.compute_class_similarity(q1, q2).get('similarity') or 0.0
            # guard against negative similiarities:
            sim = max(sim, 0.0)
            similarities.append(sim)
        return similarities

    def compute_class_similarity(self, q1, q2):
        # Original version of SemanticSimilarity.compute_class_similarity
        qnodes_dict = self.util.get_qnode_details([q1, q2])
        feature_dict, feature_count_dict = self.build_qnode_feature_dict(qnodes_dict)
        normalized_classes_idf = self.normalize_idf_classes(feature_dict, feature_count_dict)
        if q1 in feature_dict and q2 in feature_dict:
            q1_cl = set(feature_dict[q1])
            q2_cl = set(feature_dict[q2])
            q1_q2_intersection = q1_cl.intersection(q2_cl)

            _similarity = sum([normalized_classes_idf.get(c) for c in q1_q2_intersection])
            return {
                'similarity': _similarity,
                'q1': q1,
                'q1_label': qnodes_dict.get(q1, {}).get('label', ''),
                'q2': q2,
                'q2_label': qnodes_dict.get(q2, {}).get('label', '')
            }
        return {
            'similarity': '',
            'q1': q1,
            'q1_label': qnodes_dict.get(q1, {}).get('label', ''),
            'q2': q2,
            'q2_label': qnodes_dict.get(q2, {}).get('label', '')
        }

    def build_qnode_feature_dict(self, qnodes_dict: dict) -> (dict, dict):
        # Original version of SemanticSimilarity.build_qnode_feature_dict
        feature_dict = {}
        feature_count_dict = {}

        for qnode in qnodes_dict:
            if "class" in qnodes_dict[qnode]:
                feature_val = []
                cl = qnodes_dict[qnode]['class'].split("|")

                for c in cl:
                    vals = c.split(":")
                    feature_val.append(vals[0])
                    feature_count_dict[vals[0]] = float(vals[1])
                if qnode not in feature_val:
                    feature_val.append(qnode)
                if qnode not in feature_count_dict:
                    feature_count_dict[qnode] = self.backend.get_class_count(qnode, 1.0)
                feature_dict[qnode] = feature_val

        return feature_dict, feature_count_dict

    def normalize_idf_classes(self, feature_dict, feature_count_dict):
        # Original version of SemanticSimilarity.normalize_idf_classes
        classes_count = {}
        for qnode in feature_dict:

            classes = feature_dict[qnode]
            for c in classes:
                if c not in classes_count:
                    classes_count[c] = 0
                classes_count[c] += 1

        classes_idf = self.calculate_idf_features(feature_count_dict)

        # multiply class count with idf
        for c in classes_idf:
            classes_idf[c] = classes_count[c] * classes_idf[c]

        # normalize the idf scores so that they sum to 1
        classes_idf_sum = sum([classes_idf[x] for x in classes_idf])
        for c in classes_idf:
            classes_idf[c] = classes_idf[c] / classes_idf_sum

        return classes_idf

    def calculate_idf_features(self, feature_count_dict):
        # Original version of SemanticSimilarity.calculate_idf_features
        _ = {}
        for c in feature_count_dict:
            _[c] = math.log(self.N / feature_count_dict[c])
        return _


"""
>>> sim = ClassSimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.39130290159946657
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.43292026043050924
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.5835489126378834
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.0
"""


class JiangConrathSimilarity(SimilarityMeasure):
    """
    Jiang Conrath similarity computations.
    """
    
    def __init__(self, *args, **kwdargs):
        super().__init__(*args, **kwdargs)

    # NOTES:
    # - formula: dist(c1, c2) = 2*log p(mss(c1, c2)) - (log p(c1) + log p(c2))
    # - prob p is from frequency of c1 relative to N
    #   - we use instance counts, original work used corpus statistics of words
    #   - making these counts more robust could improve the measure
    # - mss is the lowest super ordinate or most specific common super class
    # - if we have multiple mss's we aggregate them like parallel resistors
    #   where each distance is treated as a resistance D = 1 / (1/d1 + 1/d2 + ...)
    #   - but for now we simply use the min distance (max sim) instead
    # - for normalization we can use the largest possible distance the formula can
    #   produce based on N (the count of entity), possibly relative to c1/c2
    # - the returned mss dataframe provides a nice explanation for the sim value
    # See: https://arxiv.org/abs/cmp-lg/9709008
    # See: Budanitsky+Hirst-2006.pdf pp. 21-22
    # See also:
    # - http://maraca.d.umn.edu/similarity/measures.html
    #   - note that the relatedness measure there is an inverse distance, not a similarity
    # - https://en.wikipedia.org/wiki/Semantic_similarity
    
    def compute_similarity_df(self, c1, c2):
        """Compute JC similarity between classes 'c1' and 'c2' and return the result as a data frame.
        """
        mss = self.backend.most_specific_subsumers_df(c1, c2)
        cols = ('super', 'label', 'count', 'dist', 'sim', 'agg_dist', 'agg_sim', 'max_sim')
        N = float(self.backend.get_max_class_count())
        c1_count = self.backend.get_class_count(c1, 1)
        c2_count = self.backend.get_class_count(c2, 1)
        term2 = math.log(c1_count / N) + math.log(c2_count / N)
        if len(mss) == 0:
            return pd.DataFrame([[None, '', 0, math.nan, 0.0, 0.0, 0.0, 0.0]], columns=cols)
        elif c1 == c2:
            # this simplifies things, since otherwise we'd have to protect against zero distances:
            return pd.DataFrame([[c1, '', c1_count, 0.0, 1.0, 1.0, 1.0, 1.0]], columns=cols)
        # this normalizes based on maximum possible distance:
        #max_dist = -2 * math.log(1/N)
        # this normalizes based on maximum possible distance between c1 and c2 going
        # through the ontology top-node 'entity' which makes sims a bit lower; this
        # also means all immediate children of 'entiy' will have similarity=0:
        max_dist = -term2
        mss['count'] = mss['super'].apply(lambda row: self.backend.get_class_count(row))
        mss['dist'] = mss['count'].apply(lambda row: 2 * math.log(row / N) - term2)
        mss['sim']  = mss['dist'].apply(lambda row: 1.0 - row / max_dist)
        # fix issues with negative distances due to count problems (e.g., "Q29182" vs. "Q133485"):
        mss.loc[(mss.dist < 0), 'sim'] = 0.0
        mss.loc[(mss.dist < 0), 'dist'] = math.nan
        # here we aggregate multiple distances from independent mss, which increases
        # the overall similarity value, but maybe it is better to use the max:
        try:
            agg_dist = 1.0 / mss['dist'].apply(lambda row: 1.0 / row).sum()
        except:
            agg_dist = max_dist
        agg_sim  = 1.0 - agg_dist / max_dist
        mss['agg_dist'] = agg_dist
        mss['agg_sim'] = agg_sim
        mss['max_sim'] = mss['sim'].max()
        mss.sort_values('sim', ascending=False, inplace=True)
        return mss

    def compute_similarity_fast(self, c1, c2):
        """Same as 'compute_similarity_df' but do not use Pandas.
        Return the equivalent of max-sim as the sole result.
        """
        mss = self.backend.most_specific_subsumers(c1, c2)
        N = float(self.backend.get_max_class_count())
        c1_count = self.backend.get_class_count(c1, 1)
        c2_count = self.backend.get_class_count(c2, 1)
        term2 = math.log(c1_count / N) + math.log(c2_count / N)
        if len(mss) == 0:
            return 0.0
        elif c1 == c2:
            # this simplifies things, since otherwise we'd have to protect against zero distances:
            return 1.0
        # this normalizes based on maximum possible distance:
        #max_dist = -2 * math.log(1/N)
        # this normalizes based on maximum possible distance between c1 and c2 going
        # through the ontology top-node 'entity' which makes sims a bit lower; this
        # also means all immediate children of 'entiy' will have similarity=0:
        max_dist = -term2
        mss_counts = [self.backend.get_class_count(row) for row in mss]
        # fix issues with negative distances due to count problems (e.g., "Q29182" vs. "Q133485"):
        mss_dists =  [max(2 * math.log(row / N) - term2, 0.0) for row in mss_counts]
        mss_sims  =  [max(1.0 - row / max_dist, 0.0) for row in mss_dists]
        return mss_sims[0] if len(mss_sims) == 1 else max(*mss_sims)

    def compute_similarity(self, c1, c2):
        """Compute JC similarity between classes 'c1' and 'c2' and return the result.
        This picks the maximum similarity over all most-specific subsumers.
        """
        #simdf = self.compute_similarity_df(c1, c2)
        #return simdf['max_sim'][0]
        return self.compute_similarity_fast(c1, c2)

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return [self.compute_similarity(c1, c2) for c1, c2 in pairs]

"""
>>> sim = JiangConrathSimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity_df("Q107711", "Q384593")
     super            label      count       dist       sim  agg_dist   agg_sim   max_sim
0   Q28640  'profession'@en  1423733.0  13.443540  0.334215  6.006707  0.702521  0.462247
1  Q703534    'employee'@en   390888.0  10.858307  0.462247  6.006707  0.702521  0.462247
>>> sim.compute_similarity("Q107711", "Q384593")
0.4622472947595052
# firefighter vs. paramedic:
>>> sim.compute_similarity_df("Q107711", "Q330204")
       super            label      count       dist       sim  agg_dist   agg_sim   max_sim
0  Q17126809     'rescuer'@en      783.0   2.587871  0.893712   2.25612  0.907337  0.893712
1     Q28640  'profession'@en  1423733.0  17.599191  0.277171   2.25612  0.907337  0.893712
>>> sim.compute_similarity("Q107711", "Q330204")
0.8937117243814836
# iron vs. aluminum:
>>> sim.compute_similarity_df("Q677", "Q663")
    super                  label   count      dist       sim  agg_dist   agg_sim   max_sim
0  Q11344  'chemical element'@en   996.0  6.508373  0.765776   2.55125  0.908185  0.765776
1  Q11426             'metal'@en  2519.0  8.364113  0.698991   2.55125  0.908185  0.765776
2  Q12140        'medication'@en  2591.0  8.420477  0.696963   2.55125  0.908185  0.765776
>>> sim.compute_similarity("Q677", "Q663")
0.7657757628493442
# iron vs. Neil Young:
>>> sim.compute_similarity_df("Q677", "Q633")
    super        label       count       dist  sim   agg_dist  agg_sim  max_sim
0  Q35120  'entity'@en  41575722.0  31.154228  0.0  31.154228      0.0      0.0
>>> sim.compute_similarity("Q677", "Q633")
0.0
"""


class ComplExSimilarity(SimilarityMeasure):
    """
    Similarity computations based on ComplEx graph embeddings.
    Currently these are 100-dimensional.
    """
    
    EMBEDDING_KEY = 'complex'

    # class slot so we only load this once:
    faiss_index = None

    def __init__(self, *args, **kwdargs):
        super().__init__(*args, embedding_type=self.EMBEDDING_KEY, **kwdargs)

    @classmethod
    def get_faiss_index(self):
        if self.faiss_index is None:
            # the first time this takes 20+GB of RAM and some time to load:
            self.faiss_index = FAISS_Index()
        return self.faiss_index

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return self.compute_pairwise_embedding_similarities(pairs)

    def compute_node_similarities(self, node, others):
        """Compute similarities between 'node' and 'others' and return the result as a list.
        """
        return self.compute_node_embedding_similarities(node, others)

    def get_most_similar(self, qnode, topn=20, poolsize=None):
        # these include raw scores from the index:
        poolsize = poolsize or topn * 5
        neighbors = self.get_faiss_index().get_neighbors(qnode, k=poolsize)
        
        # NOTE: the scores from the index lookup and associated ordering correspond to
        # the FAISS L2 metric we currently use for training, which does not give the same
        # ranking as cosine similarity.  For now we compute the actual cosine similarities
        # here, but in order to get a good top-k set of neighbors, a significantly larger
        # set of 'poolsize' has to be extracted in order to get good coverage
        # TO DO: use cosine similarity during training of the index (which requires normalization
        # of the embedding vectors), since even with large poolsize we are missing stuff
        similarities = self.compute_node_embedding_similarities(qnode, [n['qnode'] for n in neighbors])
        for sim, info in zip(similarities, neighbors):
            info['sim'] = sim
            info['score'] = float(info['score']) # coerce numpy float32s
        neighbors.sort(key=lambda i: i['sim'], reverse=True)
        return neighbors[0:topn]

"""
>>> sim = ComplExSimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5925805286218
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.5127900066858567
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.7300471869084028
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.14826926450712863
"""


class TransESimilarity(SimilarityMeasure):
    """
    Similarity computations based on TransE graph embeddings.
    Currently these are 100-dimensional.
    """
    
    EMBEDDING_KEY = 'transe'

    def __init__(self, *args, **kwdargs):
        super().__init__(*args, embedding_type=self.EMBEDDING_KEY, **kwdargs)

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return self.compute_pairwise_embedding_similarities(pairs)
    
    def compute_node_similarities(self, node, others):
        """Compute similarities between 'node' and 'others' and return the result as a list.
        """
        return self.compute_node_embedding_similarities(node, others)

"""
>>> sim = TransESimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5792073076217563
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.38376134647692317
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.5551595225585125
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.043927954317452854
"""


class TextSimilarity(SimilarityMeasure):
    """
    Similarity computations based on text embeddings.  Currently, this is
    linked to specific text embeddings created from KGTK node lexicalizations.
    Currently these are 1024-dimensional.
    """

    EMBEDDING_KEY = 'text'

    def __init__(self, *args, **kwdargs):
        super().__init__(*args, embedding_type=self.EMBEDDING_KEY, **kwdargs)

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return self.compute_pairwise_embedding_similarities(pairs)

    def compute_node_similarities(self, node, others):
        """Compute similarities between 'node' and 'others' and return the result as a list.
        """
        return self.compute_node_embedding_similarities(node, others)

"""
>>> sim = TextSimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5108304027429851
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.7159379812207856
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.8606787985250834
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.3192168789344966
"""


class Node2VecSimilarity(SimilarityMeasure):
    """
    Similarity computations based on Node2Vec graph embeddings.
    """
    
    def __init__(self, *args, **kwdargs):
        super().__init__(*args, **kwdargs)

    def compute_similarity(self, c1, c2):
        try:
            c1id = self.backend.get_node_node2vec_emb_numid_and_label(c1, fmt='df')['numid'].iloc[0]
            c2id = self.backend.get_node_node2vec_emb_numid_and_label(c2, fmt='df')['numid'].iloc[0]
            sim = self.backend.get_node2vec_embeddings().wv.similarity(c1id, c2id)
            # map negative similarities which represent anti-correlation of some kind onto 0:
            return max(sim, 0.0)
        except KeyError:
            pass
        except IndexError:
            pass
        return 0.0

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return [self.compute_similarity(c1, c2) for c1, c2 in pairs]


    NODE2VEC_FRAME_COLUMNS = ['node1', 'node2', 'numid1', 'numid2', 'label1', 'label2', 'sim']

    def get_most_similar_df(self, c, topn=20):
        try:
            resdf = self.backend.get_node_node2vec_emb_numid_and_label(c, fmt='df')
            cid = resdf['numid'].iloc[0]
            clabel = resdf['label'].iloc[0]
            similar = self.backend.get_node2vec_embeddings().wv.most_similar(cid, topn=topn)
            rows = []
            for numid, sim in similar:
                resdf = self.backend.get_node_and_label_from_node2vec_emb_numid(numid, fmt='df')
                qnode = resdf['node1'].iloc[0]
                label = resdf['label'].iloc[0]
                rows.append([c, qnode, cid, numid, clabel, label, round(sim, 3)])
            return pd.DataFrame(rows, columns=self.NODE2VEC_FRAME_COLUMNS)
        except KeyError:
            pass
        except IndexError:
            pass
        return None

    def get_most_similar(self, c, topn=20):
        neighbors = self.get_most_similar_df(c, topn=topn)
        if isinstance(neighbors, pd.DataFrame):
            neighbors.rename(columns={'node2': 'qnode', 'label2': 'label'}, inplace=True)
            return neighbors.loc[:,['qnode', 'label', 'sim']].to_dict(orient='records')
        else:
            return []

"""
>>> sim = Node2VecSimilarity()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.36018994
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.4073951
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.67848825
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.03546055
"""


class ComboSimilarity_1(SimilarityMeasure):
    """Computes a simple average of the supplied similarity measures
    which default to ('complex', 'transe', 'text', 'class', 'jc').
    """
    
    def __init__(self, *args, measures=None, **kwdargs):
        super().__init__(*args, **kwdargs)
        if measures is None:
            measures = (ComplExSimilarity(),
                        TransESimilarity(),
                        TextSimilarity(),
                        ClassSimilarity(),
                        JiangConrathSimilarity())
        self.measures = measures

    def compute_pairwise_similarities(self, pairs):
        return [statistics.mean(sims) for sims in zip(*[m.compute_pairwise_similarities(pairs) for m in self.measures])]

    def compute_node_similarities(self, node, others):
        node_sims = []
        for m in self.measures:
            node_sims.append(m.compute_node_similarities(node, others))
        return [statistics.mean(nsims) for nsims in zip(*node_sims)]
    
"""
>>> sim = ComboSimilarity_1()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5072336870691027
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.5878242638391116
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.6990420366958453
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.10205590860747209
"""


class ComboSimilarity_2(SimilarityMeasure):
    """Computes a simple weighted average of embedding-based and ontology-based metrics.
    Embedding measures (default ('complex', 'transe', 'text')) are averaged and ontology
    measures (default ('class', 'jc')) are maxed.
    """
    
    def __init__(self, *args, emb_measures=None, onto_measures=None, weights=(0.4, 0.6), **kwdargs):
        super().__init__(*args, **kwdargs)
        if emb_measures is None:
            emb_measures = (ComplExSimilarity(),
                            TransESimilarity(),
                            TextSimilarity())
        if onto_measures is None:
            onto_measures = (ClassSimilarity(),
                             JiangConrathSimilarity())
        self.emb_measures = emb_measures
        self.onto_measures = onto_measures
        self.weights = weights

    def compute_pairwise_similarities(self, pairs):
        # we take the average of the embedding-based measures * w[0]:
        emb_sims = [statistics.mean(sims) * self.weights[0]
                    for sims in zip(*[m.compute_pairwise_similarities(pairs) for m in self.emb_measures])]
        # we take the max of the ontology-based measures * w[1]:
        onto_sims = [max(*sims) * self.weights[1]
                     for sims in zip(*[m.compute_pairwise_similarities(pairs) for m in self.onto_measures])]
        return [es + os for es, os in zip(emb_sims, onto_sims)]

"""
>>> sim = ComboSimilarity_2()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.501697475387242
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.7512256125466987
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.745583525441873
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.06818854636787723
"""


class ComboSimilarity_3(SimilarityMeasure):
    """Computes a simple weighted average of embedding-based and ontology-based metrics.
    Similar to ComboSimilarity_2 but takes the average of ontology measures instead of max
    and uses balanced weights by default.
    """
    
    def __init__(self, *args, emb_measures=None, onto_measures=None, weights=(0.5, 0.5), **kwdargs):
        super().__init__(*args, **kwdargs)
        if emb_measures is None:
            emb_measures = (ComplExSimilarity(),
                            TransESimilarity(),
                            TextSimilarity())
        if onto_measures is None:
            onto_measures = (ClassSimilarity(),
                             JiangConrathSimilarity())
        self.emb_measures = emb_measures
        self.onto_measures = onto_measures
        self.weights = weights

    def compute_pairwise_similarities(self, pairs):
        # we take the average of the embedding-based measures * w[0]:
        emb_sims = [statistics.mean(sims) * self.weights[0]
                    for sims in zip(*[m.compute_pairwise_similarities(pairs) for m in self.emb_measures])]
        # we take the max of the ontology-based measures * w[1]:
        onto_sims = [statistics.mean(sims) * self.weights[1]
                     for sims in zip(*[m.compute_pairwise_similarities(pairs) for m in self.onto_measures])]
        return [es + os for es, os in zip(emb_sims, onto_sims)]

"""
>>> sim = ComboSimilarity_3()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.4938239222541665
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.600406218600259
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.6949787535371401
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.08495204427941684
"""


class TopSimSimilarity(SimilarityMeasure):
    """Support for TopSim similarity measures based on computing top-similarity regions.
    """
    
    def __init__(self, *args, maxup=1, maxdown=1, topn=20, firstn=100, measure=None, **kwdargs):
        super().__init__(*args, **kwdargs)
        self.maxup = maxup
        self.maxdown = maxdown
        self.topn = topn
        self.firstn = firstn
        self.measure = measure or ComboSimilarity_1()
        self.complex = ComplExSimilarity()
        self.n2v = Node2VecSimilarity()

    @lru_cache(maxsize=config['LRU_CACHE_SIZE']) # thread-safe according to source
    def generate_candidates(self, nodes):
        # TO DO: handle redirects such as "order (Q567696) (redirected from Q24073594)"
        #        handle nodes that only have non-English labels
        candidates = []
        for node in [nodes] if isinstance(nodes, str) else nodes:
            onto_neighbors = self.backend.get_node_neighbors(node, maxup=self.maxup, maxdown=self.maxdown)
            n2v_neigbors = self.n2v.get_most_similar(node, topn=self.firstn)
            # reducing poolsize to 2*firstn to reduce compute time:
            complex_neigbors = self.complex.get_most_similar(node, topn=self.firstn, poolsize=2 * self.firstn)
            all_neigbors = onto_neighbors
            all_neigbors.update([info['qnode'] for info in n2v_neigbors])
            all_neigbors.update([info['qnode'] for info in complex_neigbors])
            # make sure 'node' isn't also one of the similarity candidates:
            if node in all_neigbors:
                all_neigbors.remove(node)
            candidates.append(all_neigbors)
        return candidates[0] if isinstance(nodes, str) else candidates

    @lru_cache(maxsize=config['LRU_CACHE_SIZE']) # thread-safe according to source
    def get_most_similar(self, node):
        # this is still a bit sluggish but will have to do for now:
        candidates = self.generate_candidates(node)
        sims = self.measure.compute_node_similarities(node, candidates)
        topsims = [{'qnode': cand, 'sim': sim} for cand, sim in zip(candidates, sims)]
        topsims.sort(key=lambda i: i['sim'], reverse=True)
        # TO DO: add labels
        return topsims[0:self.topn]

    def compute_pairwise_similarities(self, pairs):
        """Compute similarities over a sequence of pairs and return the result as a list.
        """
        return [self.compute_similarity(c1, c2) for c1, c2 in pairs]
    

class TopSimSimilarity_1(TopSimSimilarity):
    """Computes the configured similarity between node1 and node2 if they are in each other's
    top-similarity regions, 0 otherwise.  So this primarily restricts the applicability of
    the measure, it does not give us any additional robustness.
    """

    def __init__(self, *args, **kwdargs):
        super().__init__(*args, **kwdargs)

    def compute_similarity(self, node1, node2):
        node1_sim = [info['qnode'] for info in self.get_most_similar(node1)]
        node2_sim = [info['qnode'] for info in self.get_most_similar(node2)]
        if node1 in node2_sim or node2 in node1_sim:
            return self.measure.compute_similarity(node1, node2)
        else:
            return 0.0

"""
# this is identical to ComboSimilarity_1 except for the last case:
>>> sim = TopSimSimilarity_1(topn=50, firstn=250)

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5072336870691027
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.5878242638391116
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.6990420366958453
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.0
"""


class TopSimSimilarity_2(TopSimSimilarity):
    """Computes the top-similarity regions for each node, and then computes a
    weighted average of similarities between node1 and node2 + its top-sim
    neighbors and vice versa.  This gives us a broader base for similarity
    between node1 and node2 based on their top similars which should increase
    the robustness of the measure.  Different aggregations are possible.
    """

    DEFAULT_TOP_K = 5

    def __init__(self, *args, k=None, **kwdargs):
        super().__init__(*args, **kwdargs)
        self.k = self.DEFAULT_TOP_K if k is None else k

    def compute_similarity(self, node1, node2):
        # TO DO: try to make this faster, it is still a bit sluggish
        #        even with all the caching, etc. we do
        if node1 == node2:
            return 1.0
        node1_sim = self.get_most_similar(node1)[0:self.k]
        node2_sim = self.get_most_similar(node2)[0:self.k]
        sims = self.measure.compute_similarity(node1, node2)
        weights = 1.0
        for info in node1_sim:
            sims += self.measure.compute_similarity(info['qnode'], node2)
            weights += info['sim']
        for info in node2_sim:
            sims += self.measure.compute_similarity(node1, info['qnode'])
            weights += info['sim']
        return min(sims / weights, 1.0)

"""
>>> sim = TopSimSimilarity_2()

# firefighter vs. police officer:
>>> sim.compute_similarity("Q107711", "Q384593")
0.5570331963248568
# firefighter vs. paramedic:
>>> sim.compute_similarity("Q107711", "Q330204")
0.7039592123711529
# iron vs. aluminum:
>>> sim.compute_similarity("Q677", "Q663")
0.7922966463605913
# iron vs. Neil Young:
>>> sim.compute_similarity("Q677", "Q633")
0.18452634444132293
"""
