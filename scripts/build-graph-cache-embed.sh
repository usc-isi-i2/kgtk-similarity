#!/bin/bash

# Populate a DWD graph cache with everything we need for similarity computations.

KGTK_CODE_HOME=$HOME/Projects/kgtk/code/kgtk.branches/feature_kypher_indexing/kgtk
KGTK_SIM_HOME=$HOME/Projects/kgtk/code/kgtk-similarity
KGTK_ENV=ksink39

WIKIDATA_VERSION=wikidata-20210215-dwd-v2
KGTK_DATA_HOME=kgtk:/datasets/$WIKIDATA_VERSION
LOCAL_DATA_HOME=/data/kgtk/wikidata/wikidata-20210215-dwd-node-vectors

CLAIMS_FILE=claims.tsv.gz
LABELS_FILE=labels.en.tsv.gz
P279STAR_FILE=derived.P279star.tsv.gz
CLASS_COUNTS_FILE=dwd_isa_class_count.compact.tsv.gz
NUMIDS_FILE=data/edges/wikidata-20210215-dwd-qnode-numids.tsv.gz
COMPLEX_EMB_FILE=wikidatadwd.complEx.graph-embeddings.txt
TRANSE_EMB_FILE=wikidatadwd.transE.graph-embeddings.txt
TEXT_EMB_FILE=text-embeddings-concatenated.tsv.gz

DB_HOME=/data/tmp
DWD_CACHE=$DB_HOME/$WIKIDATA_VERSION-similarity-embed.`date +%FT%R`.sqlite3.db

export SQLITE_TMPDIR=$DB_HOME
export TMPDIR=$DB_HOME

KGTK_HEADER=/tmp/kgtk-header.tsv


. $HOME/miniconda3/bin/activate ${KGTK_ENV}
PYTHONPATH=$KGTK_CODE_HOME

MEASURE_SPACE="ls -l $DWD_CACHE; kgtk query --graph-cache $DWD_CACHE --show-cache"
# use -0 to let everything through:
HEAD="-0"


date
rm -f $DWD_CACHE
cd $KGTK_CODE_HOME

set -x

# we start with the largest file to have extra room for journal ops:
rclone cat $KGTK_DATA_HOME/$TEXT_EMB_FILE | zcat | head -n $HEAD | $KGTK_SIM_HOME/scripts/transcode_vectors.py --format kgtk --input-label text_embedding --label emb \
     | time kgtk --debug query -i - --as textemb --idx mode:attgraph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

rclone cat $KGTK_DATA_HOME/$COMPLEX_EMB_FILE | head -n $HEAD | $KGTK_SIM_HOME/scripts/transcode_vectors.py --format plain --label emb \
     | time kgtk --debug query -i - --as complexemb --idx mode:attgraph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

rclone cat $KGTK_DATA_HOME/$TRANSE_EMB_FILE | head -n $HEAD | $KGTK_SIM_HOME/scripts/transcode_vectors.py --format plain --label emb \
     | time kgtk --debug query -i - --as transeemb --idx mode:attgraph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date
