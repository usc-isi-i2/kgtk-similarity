from kgtk.gt.gt_load import load_graph_from_kgtk
from kgtk.io.kgtkreader import KgtkReader
from graph_tool.all import find_vertex
from graph_tool.topology import all_paths
import json
from pathlib import Path

config = json.load(open('semantic_similarity/config.json'))


class KGTKPaths:
    def __init__(self):
        if config['input_kgtk_edge_file'].strip() != "":
            kr: KgtkReader = KgtkReader.open(Path(config['input_kgtk_edge_file']),
                                             error_file=None,
                                             options=None,
                                             value_options=None,
                                             verbose=False,
                                             very_verbose=False,
                                             )

            sub_index: int = kr.get_node1_column_index()
            pred_index: int = kr.get_label_column_index()
            obj_index: int = kr.get_node2_column_index()
            id_index: int = kr.get_id_column_index()
            if sub_index < 0 or pred_index < 0 or obj_index < 0 or id_index < 0:
                kr.close()
                raise Exception("Exiting due to missing columns.")

            self.G = load_graph_from_kgtk(kr, directed=True, ecols=(sub_index, obj_index))
        else:
            self.G = None

    def compute_paths(self, source_node, target_node, max_hops=2):
        if self.G:
            id_count = 0
            path_id = 0
            id_col = 'name'

            source_ids = find_vertex(self.G, prop=self.G.properties[('v', id_col)], match=source_node)
            target_ids = find_vertex(self.G, prop=self.G.properties[('v', id_col)], match=target_node)
            seen_paths = {}

            if len(source_ids) == 1 and len(target_ids) == 1:
                source_id = source_ids[0]
                target_id = target_ids[0]
                for path in all_paths(self.G, source_id, target_id, cutoff=max_hops, edges=True):
                    for edge_num, an_edge in enumerate(path):
                        edge_id = self.G.properties[('e', 'id')][an_edge]
                        node1: str = 'p%d' % path_id

                        if node1 not in seen_paths:
                            seen_paths[node1] = []
                        vals = edge_id.split("-")
                        if edge_num == 0:
                            seen_paths[node1].append(vals[0])

                        seen_paths[node1].append(vals[1])
                        seen_paths[node1].append(vals[2])

                        id_count += 1
                    path_id += 1

            return [seen_paths[k] for k in seen_paths]
        return []
