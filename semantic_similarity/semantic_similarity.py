import math
import json

from semantic_similarity.utility import Utility, cosine_similarity
import semantic_similarity.kypher as kypher
import semantic_similarity.similarity_measures as sm

config = json.load(open('semantic_similarity/config.json'))


class SemanticSimilarity(object):

    CONFIGURED_SIMILARITY_TYPES = {
        'complex': sm.ComplExSimilarity(),
        'transe':  sm.TransESimilarity(),
        'text':    sm.TextSimilarity(),
        'class':   sm.ClassSimilarity(),
        'jc':      sm.JiangConrathSimilarity(),
        'topsim':  sm.TopSimSimilarity_2(),
    }
    CONFIGURED_NN_SIMILARITY_TYPES = {
        'complex': sm.ComplExSimilarity(),
    }
    
    def __init__(self):
        self.config = config
        self.util = Utility()
        self.backend = kypher.get_backend()

    def semantic_similarity(self, q1: str, q2: str, similarity_type: str):

        sim = self.CONFIGURED_SIMILARITY_TYPES.get(similarity_type)
        if not sim:
            # this mirrors the original behavior for an undefined type:
            return None
        
        # this mirrors the original missing node error detection:
        # NOTE: it is possible to only get some of the embeddings, e.g., for Q17156448 we get text
        # but not complex/transe, plus there are about 14M fewer text embeddings than complex/transe:
        qnodes_dict = self.util.get_qnode_details([q1, q2])
        q1_result = qnodes_dict.get(q1, None)
        q2_result = qnodes_dict.get(q2, None)
        is_emb_sim = similarity_type in ('complex', 'text', 'transe')
        if not q1_result or is_emb_sim and q1_result.get(similarity_type, None) is None:
            return {'error': f"The qnode: {q1} is not present in DWD"}

        if not q2_result or is_emb_sim and q2_result.get(similarity_type, None) is None:
            return {'error': f"The qnode: {q2} is not present in DWD"}

        # we use the labels from the ES instance, since they don't contain language tags:
        return {
            'similarity': sim.compute_similarity(q1, q2),
            'q1': q1,
            'q1_label': q1_result.get('label', ''),
            'q2': q2,
            'q2_label': q2_result.get('label', ''),
        }

    def get_most_similar(self, qnode: str, similarity_type: str, topn: int = 20):
        sim = self.CONFIGURED_NN_SIMILARITY_TYPES.get(similarity_type)
        if not sim:
            return None
        elif similarity_type == 'complex':
            # supply poolsize that makes sense for 'complex':
            return sim.get_most_similar(qnode, topn=topn, poolsize=max(2*topn, 100))
        else:
            return sim.get_most_similar(qnode, topn=topn)


class SemanticSimilarity_v1(object):
    """Original semantic similarity entry point.  We keep this for now just in case
    we need to compare to the old version, even though the new implementation should
    compute the same numbers for class, complex, transe and text (or very close).
    """
    
    def __init__(self):
        self.config = config
        self.util = Utility()
        self.embeddings_type = ['complex', 'text', 'transe', 'class']
        self.N = float(42123553)  # TO DO: fix this to get the count from the counts file
        self.all_class_count_dict = json.load(open(config['all_class_count_file_path']))

    def semantic_similarity(self, q1: str, q2: str, embeddings_type: str):

        if embeddings_type == "class":
            return self.compute_class_similarity(q1, q2)
        else:
            qnodes_dict = self.util.get_qnode_details([q1, q2])
            q1_result = qnodes_dict.get(q1, None)
            q2_result = qnodes_dict.get(q2, None)
            if not q1_result or q1_result.get(embeddings_type, None) is None:
                return {'error': f"The qnode: {q1} is not present in DWD"}

            if not q2_result or q2_result.get(embeddings_type, None) is None:
                return {'error': f"The qnode: {q2} is not present in DWD"}

            if embeddings_type in self.embeddings_type:
                return {
                    'similarity': cosine_similarity(q1_result.get(embeddings_type).reshape(1, -1),
                                                    q2_result.get(embeddings_type).reshape(1, -1))[0][0],
                    'q1': q1,
                    'q1_label': q1_result.get('label', ''),
                    'q2': q2,
                    'q2_label': q2_result.get('label', '')
                }

    def compute_class_similarity(self, q1, q2):
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
                    feature_count_dict[qnode] = self.all_class_count_dict.get(qnode, 1.0)
                feature_dict[qnode] = feature_val

        return feature_dict, feature_count_dict

    def normalize_idf_classes(self, feature_dict, feature_count_dict):

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
        _ = {}
        for c in feature_count_dict:
            _[c] = math.log(self.N / feature_count_dict[c])
        return _
