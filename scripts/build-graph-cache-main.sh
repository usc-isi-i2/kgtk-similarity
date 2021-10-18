#!/bin/bash

# Populate a DWD graph cache with everything we need for similarity computations.

KGTK_CODE_HOME=$HOME/Projects/kgtk/code/kgtk.branches/feature_kypher_indexing/kgtk
KGTK_SIM_HOME=$HOME/Projects/kgtk/code/kgtk-similarity
KGTK_ENV=ksink39

WIKIDATA_VERSION=wikidata-20210215-dwd-v2
KGTK_DATA_HOME=kgtk:/datasets/$WIKIDATA_VERSION
LOCAL_DATA_HOME=/data/kgtk/wikidata/wikidata-20210215-dwd-node-vectors
LOCAL_DATA_HOME2=/data/tmp

CLAIMS_FILE=claims.tsv.gz
LABELS_FILE=labels.en.tsv.gz
P279STAR_FILE=derived.P279star.tsv.gz
CLASS_COUNTS_FILE=dwd_isa_class_count.compact.tsv.gz
NUMIDS_FILE=data/edges/wikidata-20210215-dwd-qnode-numids.tsv.gz

COMPLEX_EMB_FILE=wikidatadwd.complEx.graph-embeddings.txt
TRANSE_EMB_FILE=wikidatadwd.transE.graph-embeddings.txt
TEXT_EMB_FILE=text-embeddings-concatenated.tsv.gz

COMPLEX_EMB_NUMIDS_FILE=wikidata-20210215-dwd-v2-similarity-embed.2021-10-03T12:14.complexemb.numids.tsv.gz
TRANSE_EMB_NUMIDS_FILE=wikidata-20210215-dwd-v2-similarity-embed.2021-10-03T12:14.transeemb.numids.tsv.gz
TEXT_EMB_NUMIDS_FILE=wikidata-20210215-dwd-v2-similarity-embed.2021-10-03T12:14.textemb.numids.tsv.gz

DB_HOME=/data/tmp
DWD_CACHE=$DB_HOME/$WIKIDATA_VERSION-similarity-main.`date +%FT%R`.sqlite3.db

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

rclone cat $KGTK_DATA_HOME/$CLAIMS_FILE | zcat | head -n $HEAD | time kgtk --debug query -i - --as claims --idx mode:graph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

rclone cat $KGTK_DATA_HOME/$LABELS_FILE | zcat | head -n $HEAD | time kgtk --debug query -i - --as labels --idx mode:valuegraph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

rclone cat $KGTK_DATA_HOME/$P279STAR_FILE | zcat | head -n $HEAD | time kgtk --debug query -i - --as p279star --idx mode:monograph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

# the class counts file records transitive class counts per node in a compact format, so we have to convert that first:
# TO DO: use compressed sort, since this blows up to 30GB due to the heavy repetition
echo 'id	node1	label	node2' > $KGTK_HEADER
rclone cat $KGTK_DATA_HOME/$CLASS_COUNTS_FILE | zcat | head -n $HEAD | tail -n +2 | cut -f 3 | tr '|' '\n' | sort | uniq \
     | sed -e 's/^/\t/' -e 's/:/\tcount\t/' \
     | cat $KGTK_HEADER - | kgtk add-id -i - \
     | time kgtk --debug query -i - --as classcounts --idx mode:valuegraph --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

# unfortunately, we also need the compact version for the class sim computation, so another 30+ GB:
rclone cat $KGTK_DATA_HOME/$CLASS_COUNTS_FILE | zcat | head -n $HEAD | kgtk add-id \
     | time kgtk --debug query -i - --as classcounts_compact --idx mode:valuegraph --graph-cache $DWD_CACHE --limit 5

# TO DO: guard against non-existing numids file:
zcat $LOCAL_DATA_HOME/$NUMIDS_FILE | head -n $HEAD | time kgtk --debug query -i - --as numids --idx node1 node2 --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

zcat $LOCAL_DATA_HOME2/$COMPLEX_EMB_NUMIDS_FILE | head -n $HEAD | time kgtk --debug query -i - --as complexemb_numids --idx node1 node2 --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

zcat $LOCAL_DATA_HOME2/$TRANSE_EMB_NUMIDS_FILE | head -n $HEAD | time kgtk --debug query -i - --as transeemb_numids --idx node1 node2 --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

zcat $LOCAL_DATA_HOME2/$TEXT_EMB_NUMIDS_FILE | head -n $HEAD | time kgtk --debug query -i - --as textemb_numids --idx node1 node2 --graph-cache $DWD_CACHE --limit 5
eval $MEASURE_SPACE
date

time pigz -6 -p 8 -b 2048 $DWD_CACHE
date
