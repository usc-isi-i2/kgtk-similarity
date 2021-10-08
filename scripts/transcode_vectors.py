#!/usr/bin/env python

# Utility to preprocess embedding vector text files into KGTK format.
# Reads vectors from stdin and reformats them to stdout.

# TO DO: generalize to support generation of numpy mmap files

import sys
import os
import os.path
import base64
import numpy as np
import csv
import argparse

script_name = os.path.basename((len(sys.argv) > 0 and sys.argv[0]) or '')
script_home = os.path.dirname((len(sys.argv) > 0 and sys.argv[0]) or '')


### Command-line argument handling:

DEFAULT_FORMAT = 'plain'
DEFAULT_INPUT_LABEL = 'text_embedding'
DEFAULT_LABEL = 'emb'

parser = argparse.ArgumentParser()
parser.add_argument('--format', default=DEFAULT_FORMAT,
                    help='format of input vectors')
parser.add_argument('--input-label', default=DEFAULT_INPUT_LABEL,
                    help='label value used for input embeddings')
parser.add_argument('--label', default=DEFAULT_LABEL,
                    help='output value to use for the label column')


def transcode_plain_vectors(inp, out, label=DEFAULT_LABEL):
    """Plain format starts with a 'total ndim' line followed by 'qnodes v_1 v_2 ... v_ndim',
    everything separated by a single space.
    """
    sep = ' '
    chunksize = 100000
    writer = csv.writer(out, dialect=None, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\n')
    i = -1
    rows = []
    for line in inp:
        i += 1
        if i == 0:
            total, ndim = line.strip().split(sep)
            total, ndim = int(total), int(ndim)
            rows.append(['id', 'node1', 'label', 'node2'])
            continue
        qnode, vec = line.split(sep, 1)
        npvec = np.fromstring(vec, dtype=np.float32, sep=sep, count=ndim)
        # we add a leading '=' to ensure symbol type:
        rows.append(['e'+str(i), qnode, label, '=' + base64.b64encode(npvec.tobytes()).decode()])
        if len(rows) >= chunksize:
            writer.writerows(rows)
            rows = []
            sys.stderr.write('.')
            sys.stderr.flush()
    writer.writerows(rows)

def transcode_kgtk_vectors(inp, out, input_label=DEFAULT_INPUT_LABEL, label=DEFAULT_LABEL):
    """KGTK format which might include text strings.
    We could do some of this directly with KGTK, but not the transcoding.
    """
    sep = ','
    chunksize = 100000
    reader = csv.reader(inp, dialect=None, delimiter='\t', quoting=csv.QUOTE_NONE)
    writer = csv.writer(out, dialect=None, delimiter='\t', quoting=csv.QUOTE_NONE, lineterminator='\n')
    header = next(reader)
    n1col = header.index('node1')
    n2col = header.index('node2')
    lcol = header.index('label')
    ndim = None
    writer.writerow(['id', 'node1', 'label', 'node2'])
    i = 1
    rows = []
    while True:
        for row in reader:
            node1, inlabel, node2 = row[n1col], row[lcol], row[n2col]
            if inlabel != input_label:
                continue
            npvec = np.fromstring(node2, dtype=np.float32, sep=sep)
            # we add a leading '=' to ensure symbol type:
            rows.append(['e'+str(i), node1, label, '=' + base64.b64encode(npvec.tobytes()).decode()])
            i += 1
            if len(rows) >= chunksize:
                break
        if len(rows) == 0:
            break
        writer.writerows(rows)
        rows = []
        sys.stderr.write('.')
        sys.stderr.flush()


if __name__ == "__main__" and len(script_name) > 0:
    args = parser.parse_args()
    label = args.label
    if args.format == 'plain':
        transcode_plain_vectors(sys.stdin, sys.stdout, label=label)
    elif args.format == 'kgtk':
        transcode_kgtk_vectors(sys.stdin, sys.stdout, label=label)
    else:
        raise Exception(f'unsupported format: {args.format}')
