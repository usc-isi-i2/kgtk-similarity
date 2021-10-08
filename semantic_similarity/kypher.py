"""
Kypher query backend support for KGTK similarity computations.
"""

import os.path
import json

import numpy as np
import pandas as pd

import kgtk.kypher.api as kapi
from   kgtk.exceptions import KGTKException


config = json.load(open('semantic_similarity/config.json'))

BACKEND_CONFIG = {
    # defaults for configuration parameters that need to have values:
    'API_VERSION'           : config.get('api_version'),
    
    'GRAPH_CACHE'           : config.get('GRAPH_CACHE'),
    'INDEX_MODE'            : config.get('INDEX_MODE', 'none'),
    'DEFAULT_LANGUAGE'      : config.get('DEFAULT_LANGUAGE', 'en'),
    'MAX_RESULTS'           : config.get('MAX_QUERY_RESULTS', 1000000),
    'MAX_CACHE_SIZE'        : config.get('LRU_CACHE_SIZE', 250000),

    # input file names (or aliases) for various aspects of the KG:
    'KG_EDGES_GRAPH'        : config.get('KG_EDGES_GRAPH', 'claims'),
    'KG_LABELS_GRAPH'       : config.get('KG_LABELS_GRAPH', 'labels'),
    'KG_P279STAR_GRAPH'     : config.get('KG_P279STAR_GRAPH', 'p279star'),
    
    'ALL_CLASS_COUNTS_FILE'         : config.get('all_class_count_file_path'),
    'KG_CLASS_COUNTS_GRAPH'         : config.get('KG_CLASS_COUNTS_GRAPH'),
    'KG_CLASS_COUNTS_COMPACT_GRAPH' : config.get('KG_CLASS_COUNTS_COMPACT_GRAPH'),
    
    'KG_NODE2VEC_EMB_NUMIDS_GRAPH'  : config.get('KG_NODE2VEC_EMB_NUMIDS_GRAPH'),
    'KG_COMPLEX_EMB_NUMIDS_GRAPH'   : config.get('KG_COMPLEX_EMB_NUMIDS_GRAPH'),
    'KG_TRANSE_EMB_NUMIDS_GRAPH'    : config.get('KG_TRANSE_EMB_NUMIDS_GRAPH'),
    'KG_TEXT_EMB_NUMIDS_GRAPH'      : config.get('KG_TEXT_EMB_NUMIDS_GRAPH'),

    'NODE2VEC_EMBEDDINGS'           : config.get('NODE2VEC_EMBEDDINGS'),
    'COMPLEX_EMBEDDINGS'            : config.get('COMPLEX_EMBEDDINGS'),
    'TRANSE_EMBEDDINGS'             : config.get('TRANSE_EMBEDDINGS'),
    'TEXT_EMBEDDINGS'               : config.get('TEXT_EMBEDDINGS'),
}


class SimilarityBackend(kapi.KypherApi):
    """
    Kypher query backend supporting similarity computations.
    This strongly assumes a KGTK DWD database.
    """

    def __init__(self, config=BACKEND_CONFIG, loglevel=0):
        super().__init__(config=config, loglevel=loglevel)
        # the initial version using the ElasticSearch backend:
        self.api_version_1 = str(self.get_config('API_VERSION')) == '1'
        
        self.all_class_counts = None
        self.node2vec_embeddings = None
        self.complex_embeddings = None
        self.transe_embeddings = None
        self.text_embeddings = None
        
        # define internal names/handles we can use for these inputs:
        self.add_input(self.get_config('KG_EDGES_GRAPH'),        name='edges',   handle=True)
        self.add_input(self.get_config('KG_LABELS_GRAPH'),       name='labels',  handle=True)
        self.add_input(self.get_config('KG_P279STAR_GRAPH'),     name='p279*',   handle=True)
        if self.get_config('KG_CLASS_COUNTS_GRAPH') is not None:
            self.add_input(self.get_config('KG_CLASS_COUNTS_GRAPH'),   name='classcounts',  handle=True)
        if self.get_config('KG_CLASS_COUNTS_COMPACT_GRAPH') is not None:
            self.add_input(self.get_config('KG_CLASS_COUNTS_COMPACT_GRAPH'),   name='classcounts_compact',  handle=True)
        if self.get_config('KG_NODE2VEC_EMB_NUMIDS_GRAPH') is not None:
            self.add_input(self.get_config('KG_NODE2VEC_EMB_NUMIDS_GRAPH'),   name='node2vecemb_numids',  handle=True)
        if self.get_config('KG_COMPLEX_EMB_NUMIDS_GRAPH') is not None:
            self.add_input(self.get_config('KG_COMPLEX_EMB_NUMIDS_GRAPH'),   name='complexemb_numids',  handle=True)
        if self.get_config('KG_TRANSE_EMB_NUMIDS_GRAPH') is not None:
            self.add_input(self.get_config('KG_TRANSE_EMB_NUMIDS_GRAPH'),   name='transeemb_numids',  handle=True)
        if self.get_config('KG_TEXT_EMB_NUMIDS_GRAPH') is not None:
            self.add_input(self.get_config('KG_TEXT_EMB_NUMIDS_GRAPH'),   name='textemb_numids',  handle=True)

    # these embedding accessors are here since the embeddings could be served directly from the DB:

    def get_node2vec_embeddings(self):
        if self.node2vec_embeddings is None:
            import gensim
            self.node2vec_embeddings = gensim.models.Word2Vec.load(self.get_config('NODE2VEC_EMBEDDINGS'))
        return self.node2vec_embeddings

    def get_embeddings_data_shape(self, data_file, numids_graph, dtype=np.float32):
        """Derive the shape of a full memory-mapped embeddings array from its 'data_file' and 'numids_graph'.
        """
        ntotal = self.get_query(inputs=numids_graph, match='(n)', ret='count(n) as count').execute()[0][0]
        ndim = os.path.getsize(data_file) // ntotal // np.zeros(1, dtype=dtype).nbytes
        return ntotal, ndim

    def get_complex_embeddings(self):
        if self.complex_embeddings is None:
            data_file = self.get_config('COMPLEX_EMBEDDINGS')
            dtype = np.float32
            ntotal, ndim = self.get_embeddings_data_shape(data_file, 'complexemb_numids', dtype=dtype)
            self.complex_embeddings = np.memmap(data_file, dtype=dtype, mode='r', shape=(ntotal, ndim))
        return self.complex_embeddings
    
    def get_transe_embeddings(self):
        if self.transe_embeddings is None:
            data_file = self.get_config('TRANSE_EMBEDDINGS')
            dtype = np.float32
            ntotal, ndim = self.get_embeddings_data_shape(data_file, 'transeemb_numids', dtype=dtype)
            self.transe_embeddings = np.memmap(data_file, dtype=dtype, mode='r', shape=(ntotal, ndim))
        return self.transe_embeddings

    def get_text_embeddings(self):
        if self.text_embeddings is None:
            data_file = self.get_config('TEXT_EMBEDDINGS')
            dtype = np.float32
            ntotal, ndim = self.get_embeddings_data_shape(data_file, 'textemb_numids', dtype=dtype)
            self.text_embeddings = np.memmap(data_file, dtype=dtype, mode='r', shape=(ntotal, ndim))
        return self.text_embeddings

    def get_node_embedding(self, qnode, embedding_type):
        # TO DO: maybe have separate methods for these
        if embedding_type == "complex":
            embeddings = self.get_complex_embeddings()
            for node, numid, label in self.get_node_complex_emb_numid_and_label(qnode):
                return embeddings[int(numid)]
        elif embedding_type == "transe":
            embeddings = self.get_transe_embeddings()
            for node, numid, label in self.get_node_transe_emb_numid_and_label(qnode):
                return embeddings[int(numid)]
        elif embedding_type == "text":
            embeddings = self.get_text_embeddings()
            for node, numid, label in self.get_node_text_emb_numid_and_label(qnode):
                return embeddings[int(numid)]
        return None

    def get_node_embeddings(self, qnodes, embedding_type):
        # TO DO: maybe have separate methods for these
        numids = [None] * len(qnodes)
        if embedding_type == "complex":
            embeddings = self.get_complex_embeddings()
            for i, qnode in enumerate(qnodes):
                for node, numid, label in self.get_node_complex_emb_numid_and_label(qnode):
                    numids[i] = int(numid)
        elif embedding_type == "transe":
            embeddings = self.get_transe_embeddings()
            for i, qnode in enumerate(qnodes):
                for node, numid, label in self.get_node_transe_emb_numid_and_label(qnode):
                    numids[i] = int(numid)
        elif embedding_type == "text":
            embeddings = self.get_text_embeddings()
            for i, qnode in enumerate(qnodes):
                for node, numid, label in self.get_node_text_emb_numid_and_label(qnode):
                    numids[i] = int(numid)
        return [embeddings[i] if i is not None else None for i in numids]

    def get_class_count(self, klass, dflt=0):
        """Return the transitive instance count for 'klass',
        or 'dflt' if no class count is defined for 'klass'.
        """
        if self.api_version_1:
            if self.all_class_counts is None:
                self.all_class_counts = json.load(open(self.get_config('ALL_CLASS_COUNTS_FILE')))
            return self.all_class_counts.get(klass, dflt)
        else:
            query_name = 'get_class_count'
            query = (self.lookup_query(query_name) or
                     self.get_query(name=query_name,
                                    inputs=self.get_input('classcounts'),
                                    match='(n)-[]->(c)',
                                    where='n=$NODE',
                                    ret='n as node1, c as count',
                                limit=1))
            for node, count in self.execute_query(query, NODE=klass):
                return int(count)
            return dflt

    WD_ENTITY_CLASS_NODE = 'Q35120'
    
    def get_max_class_count(self):
        return self.get_class_count(self.WD_ENTITY_CLASS_NODE)
                   
    def get_class_counts_compact(self, node):
        """Return the transitive instance count for all supers of 'node'.
        This returns the compact format class1:count1|class2:count2|...
        which is used by the class similarity computation.
        """
        query_name = 'get_class_counts_compact'
        query = (self.lookup_query(query_name) or
                 self.get_query(name=query_name,
                                inputs=self.get_input('classcounts_compact'),
                                match='(n)-[]->(c)',
                                where='n=$NODE',
                                ret='n as node1, c as counts',
                            limit=1))
        for node, counts in self.execute_query(query, NODE=node):
            return counts
            
    def get_node_edges(self, node, fmt=None):
        """Retrieve all edges that have 'node' as their node1.
        """
        query_name = 'get_node_edges'
        query = (self.lookup_query(query_name) or
                 self.get_query(name=query_name,
                                inputs=self.get_input('edges'),
                                match='(n)-[r]->(n2)',
                                where='n=$NODE',
                                ret='r as id, n as node1, r.label as label, n2 as node2'))
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_label(self, node):
        """Retrieve one English label for 'node'.
        """
        query_name = 'get_node_label'
        query = (self.lookup_query(query_name) or
                 self.get_query(name=query_name,
                                inputs=self.get_input('labels'),
                                match='(n)-[r]->(l)',
                                where='n=$NODE and kgtk_lqstring_lang(l) = "en"',
                                ret='n as node1, l as label',
                                limit=1))
        for node, label in self.execute_query(query, NODE=node):
            return label
        return None

    def get_node_proper_supers(self, node, fmt=None):
        """Retrieve all supers for 'node' as well as their English labels.
        The first supers might be linked by P31 and/or P279, subsequent ones through P279 only.
        """
        query_name = 'get_node_proper_supers'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$edges: (n)-[r]->(class), $p279*: (class)-[]->(super)',
                                   where= 'n=$NODE and r.label in ["P31", "P279"]',
                                   opt=   '$labels: (super)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, super as super, l as label',
                                   order= 'n, super')
        return self.execute_query(query, fmt=fmt, NODE=node)
    
    def get_node_proper_supers_with_parents(self, node, fmt=None):
        """Retrieve all supers for 'node' as well as their English labels.
        The first supers might be linked by P31 and/or P279, subsequent ones through P279 only.
        Additionally retrieve any direct parents of each super class.
        """
        query_name = 'get_node_proper_supers_with_parents'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$edges: (n)-[r]->(class), $p279*: (class)-[]->(super)',
                                   where= 'n=$NODE and r.label in ["P31", "P279"]',
                                   opt=   '$labels: (super)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   # roots don't have parents, so this has to be an optional:
                                   opt2=  '$edges: (super)-[:P279]->(parent)',
                                   ret=   'distinct n as node1, super as super, l as label, parent as parent',
                                   order= 'n, super')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_direct_supers(self, node, fmt=None):
        """Retrieve all direct parents for 'node' as well as node's English label.
        Parents might be linked by P31 and/or P279.  This basically handles the '*' case for 'node'
        which we don't get from the P279star graph, since it only has P279 links but we also want
        any initial P31's.  Using the P31-P279star graph would be an alternative, but that is huge.
        And since we don't have union queries yet, we have to run them separately.
        """
        query_name = 'get_node_direct_supers'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$edges: (n)-[r]->(parent)',
                                   where= 'n=$NODE and r.label in ["P31", "P279"]',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, n as super, l as label, parent as parent',
                                   order= 'n, super')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_direct_subs(self, node, fmt=None):
        """Retrieve all direct children for 'node' as well as node's English label.
        Children may be linked via P279 only.  This could be done more simply but is
        done in close symmetry with 'get_node_direct_supers' for consistency.
        """
        query_name = 'get_node_direct_subs'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$edges: (child)-[r]->(n)',
                                   where= 'n=$NODE and r.label = "P279"',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, n as sub, l as label, child as child',
                                   order= 'n, sub')
        return self.execute_query(query, fmt=fmt, NODE=node)
    
    def get_node_supers(self, node, fmt=None):
        """Retrieve all supers for 'node' as well as their English labels (including 'node' itself).
        The first supers might be linked by P31 and/or P279, subsequent ones through P279 only.
        """
        dresult = [node, node, self.get_node_label(node)]
        presult = self.get_node_proper_supers(node, fmt=fmt)
        if fmt in ('df', 'dataframe'):
            dresult = pd.DataFrame([{'node1': dresult[0], 'super': dresult[1], 'label': dresult[2]}])
            return dresult.append(presult, ignore_index=True)
        else:
            return list(dresult) + list(presult)
    
    def get_node_supers_with_parents(self, node, fmt=None):
        """Retrieve all supers for 'node' as well as their English labels (including 'node' itself).
        The first supers might be linked by P31 and/or P279, subsequent ones through P279 only.
        Additionally retrieve any direct parents of each super class.
        """
        dresult = self.get_node_direct_supers(node, fmt=fmt)
        presult = self.get_node_proper_supers_with_parents(node, fmt=fmt)
        if fmt in ('df', 'dataframe'):
            return dresult.append(presult, ignore_index=True)
        else:
            return list(dresult) + list(presult)

    
    def get_node_node2vec_emb_numid_and_label(self, node, fmt=None):
        """Retrieve the numeric node ID and label for 'node'.
        """
        query_name = 'get_node_node2vec_emb_numid_and_label'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$node2vecemb_numids: (n)-[r]->(numid)',
                                   where= 'n=$NODE',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_and_label_from_node2vec_emb_numid(self, numid, fmt=None):
        """Retrieve the QNode ID and label for the node encoded by 'numid'.
        """
        query_name = 'get_node_and_label_from_node2vec_emb_numid'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$node2vecemb_numids: (n)-[r]->(numid)',
                                   where= 'numid=$NUMID',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NUMID=str(numid))

    def get_node_complex_emb_numid_and_label(self, node, fmt=None):
        """Retrieve the numeric node ID and label for 'node'.
        """
        query_name = 'get_node_complex_emb_numid_and_label'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$complexemb_numids: (n)-[r]->(numid)',
                                   where= 'n=$NODE',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_and_label_from_complex_emb_numid(self, numid, fmt=None):
        """Retrieve the QNode ID and label for the node encoded by 'numid'.
        """
        query_name = 'get_node_and_label_from_complex_emb_numid'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$complexemb_numids: (n)-[r]->(numid)',
                                   where= 'numid=$NUMID',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NUMID=str(numid))
    
    def get_node_transe_emb_numid_and_label(self, node, fmt=None):
        """Retrieve the numeric node ID and label for 'node'.
        """
        query_name = 'get_node_transe_emb_numid_and_label'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$transeemb_numids: (n)-[r]->(numid)',
                                   where= 'n=$NODE',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_and_label_from_transe_emb_numid(self, numid, fmt=None):
        """Retrieve the QNode ID and label for the node encoded by 'numid'.
        """
        query_name = 'get_node_and_label_from_transe_emb_numid'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$transeemb_numids: (n)-[r]->(numid)',
                                   where= 'numid=$NUMID',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NUMID=str(numid))
    
    def get_node_text_emb_numid_and_label(self, node, fmt=None):
        """Retrieve the numeric node ID and label for 'node'.
        """
        query_name = 'get_node_text_emb_numid_and_label'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$textemb_numids: (n)-[r]->(numid)',
                                   where= 'n=$NODE',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NODE=node)

    def get_node_and_label_from_text_emb_numid(self, numid, fmt=None):
        """Retrieve the QNode ID and label for the node encoded by 'numid'.
        """
        query_name = 'get_node_and_label_from_text_emb_numid'
        query = self.lookup_query(query_name)
        if query is None:
            query = self.get_query(name=query_name,
                                   match= '$textemb_numids: (n)-[r]->(numid)',
                                   where= 'numid=$NUMID',
                                   opt=   '$labels: (n)-[]->(l)',
                                   owhere='kgtk_lqstring_lang(l) = "en"',
                                   ret=   'distinct n as node1, numid as numid, l as label')
        return self.execute_query(query, fmt=fmt, NUMID=str(numid))

    
    def get_node_neighbors(self, node, maxup=1, maxdown=1):
        # step 1: find all parents up to a distance of 'maxup':
        seeds = {node}
        neighbors = set()
        for i in range(maxup):
            new = set()
            for seed in seeds:
                supers = [parent for node, super, label, parent in self.get_node_direct_supers(seed)]
                new.update(supers)
            seeds = new.difference(neighbors)
            neighbors.update(new)
        parents = neighbors
        
        # step 2: from node and all its parents, add all children up to a distance of 'maxdown':
        seeds = set(parents)
        seeds.add(node)
        neighbors = set()
        for i in range(maxdown):
            new = set()
            for seed in seeds:
                subs = [child for node, sub, label, child in self.get_node_direct_subs(seed)]
                new.update(subs)
            seeds = new.difference(neighbors)
            neighbors.update(new)
        neighbors.update(parents)
        return neighbors

    def most_specific_subsumers_df(self, c1, c2):
        """Compute the set of most specific subsumers of 'c1' and 'c2'.
        This will handle 'c1' and 'c2' being equal or one a parent of the other.
        Slower more descriptive version using Pandas.
        """
        c1_classes_df = self.get_node_supers_with_parents(c1, fmt='df')
        c2_classes_df = self.get_node_supers_with_parents(c2, fmt='df')
        c1_supers = set(c1_classes_df['super'])
        c2_supers = set(c2_classes_df['super'])
        # mss has to be in the intersection of superclasses:
        common = c1_supers.intersection(c2_supers)
        # now for each candidate in common, exclude all their direct parents using a pandas join.
        # TRICKY: since we have optional P31s at the beginning of super chains, we have to look at both superclass sets:
        exclude = set(pd.merge(c1_classes_df, pd.DataFrame(common, columns=('super',)), on='super')['parent'])
        exclude = exclude.union(set(pd.merge(c2_classes_df, pd.DataFrame(common, columns=('super',)), on='super')['parent']))
        mss = common.difference(exclude)
        mssdf = pd.merge(c1_classes_df, pd.DataFrame(mss, columns=('super',)), on='super').loc[:,['super', 'label']]
        mssdf = mssdf.drop_duplicates().copy()
        return mssdf

    def most_specific_subsumers(self, c1, c2):
        """Compute the set of most specific subsumers of 'c1' and 'c2'.
        This will handle 'c1' and 'c2' being equal or one a parent of the other.
        """
        c1_classes = self.get_node_supers_with_parents(c1, fmt='list')
        c2_classes = self.get_node_supers_with_parents(c2, fmt='list')
        c1_supers = set([row[1] for row in c1_classes])
        c2_supers = set([row[1] for row in c2_classes])
        # mss has to be in the intersection of superclasses:
        common = c1_supers.intersection(c2_supers)
        # now for each candidate in common, exclude all their direct parents using a pandas join.
        # TRICKY: since we have optional P31s at the beginning of super chains, we have to look at both superclass sets:
        exclude = set([row[3] for row in c1_classes if row[1] in common])
        exclude.update([row[3] for row in c2_classes if row[1] in common])
        mss = common.difference(exclude)
        return mss


class SyncedBackend(object):
    """Synchronized wrapper for low-level requests to the backend.
    This gives us more fine-grained locking than doing it for top-level requests.
    This is a stop-gap until fine-grained locking is supported by the Kypher API.
    """
    
    def __init__(self, backend):
        self.backend = backend

    def get_node_label(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_label(*args, **kwargs)
        
    def get_max_class_count(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_max_class_count(*args, **kwargs)
        
    def get_class_count(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_class_count(*args, **kwargs)

    def get_class_counts_compact(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_class_counts_compact(*args, **kwargs)

    # this one also queries unfortunately, so we need to sync:
    def get_node_embedding(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_embedding(*args, **kwargs)

    def get_node_embeddings(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_embeddings(*args, **kwargs)
        
    def get_node_and_label_from_complex_emb_numid(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_and_label_from_complex_emb_numid(*args, **kwargs)
        
    def most_specific_subsumers_df(self, *args, **kwargs):
        with self.backend as backend:
            return backend.most_specific_subsumers_df(*args, **kwargs)
    
    def most_specific_subsumers(self, *args, **kwargs):
        with self.backend as backend:
            return backend.most_specific_subsumers(*args, **kwargs)
    
    def get_node_node2vec_emb_numid_and_label(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_node2vec_emb_numid_and_label(*args, **kwargs)
    
    def get_node2vec_embeddings(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node2vec_embeddings(*args, **kwargs)
    
    def get_node_and_label_from_node2vec_emb_numid(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_and_label_from_node2vec_emb_numid(*args, **kwargs)
    
    def get_node_neighbors(self, *args, **kwargs):
        with self.backend as backend:
            return backend.get_node_neighbors(*args, **kwargs)


_backend = SimilarityBackend()

def get_backend():
    return _backend

def get_synced_backend():
    return SyncedBackend(_backend)
