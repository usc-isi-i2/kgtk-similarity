import json
from sklearn.metrics.pairwise import cosine_similarity
from semantic_similarity.utility import Utility
import math

config = json.load(open('semantic_similarity/config.json'))


class SemanticSimilarity(object):
    def __init__(self):
        self.config = config
        self.util = Utility()
        self.embeddings_type = ['complex', 'text', 'transe', 'class']
        self.N = float(42123553)

    def semantic_similarity(self, q1: str, q2: str, embeddings_type: str):

        if embeddings_type == "class":
            return self.compute_class_similarity(q1, q2)
        else:
            q1_result = self.util.get_embeddings_and_label(q1, embeddings_type)
            q2_result = self.util.get_embeddings_and_label(q2, embeddings_type)
            if q1_result.get('embedding', None) is None:
                return {'error': f"The qnode: {q1} is not present in DWD"}

            if q2_result.get('embedding', None) is None:
                return {'error': f"The qnode: {q2} is not present in DWD"}

            if embeddings_type in self.embeddings_type:
                return {
                    'similarity': cosine_similarity(q1_result.get('embedding', None).reshape(1, -1),
                                                    q2_result.get('embedding', None).reshape(1, -1))[0][0],
                    'q1': q1,
                    'q1_label': q1_result.get('label'),
                    'q2': q2,
                    'q2_label': q2_result.get('label')
                }

    def compute_class_similarity(self, q1, q2):
        qnode_class_dict, qnode_labels_dict = self.util.get_class_counts(q1, q2)
        feature_dict, feature_count_dict = self.build_qnode_feature_dict(qnode_class_dict)
        normalized_classes_idf = self.normalize_idf_classes(feature_dict, feature_count_dict)
        q1_cl = set(feature_dict[q1])
        q2_cl = set(feature_dict[q2])
        q1_q2_intersection = q1_cl.intersection(q2_cl)

        _similarity = sum([normalized_classes_idf.get(c) for c in q1_q2_intersection])
        return {
            'similarity': _similarity,
            'q1': q1,
            'q1_label': qnode_labels_dict.get(q1),
            'q2': q2,
            'q2_label': qnode_labels_dict.get(q2)
        }

    @staticmethod
    def build_qnode_feature_dict(qnode_class_dict: dict) -> (dict, dict):
        feature_dict = {}
        feature_count_dict = {}

        for qnode in qnode_class_dict:
            feature_val = []
            cl = qnode_class_dict[qnode].split("|")
            for c in cl:
                vals = c.split(":")
                feature_val.append(vals[0])
                feature_count_dict[vals[0]] = float(vals[1])
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
