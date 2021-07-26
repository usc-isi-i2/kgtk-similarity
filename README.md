# KGTK Semantic Similarity

Deployed URL: https://kgtk.isi.edu/similarity_api


## Parameters

- `q1`: The first qnode for comparison, eg: Q144 (dog)
- `q2`: The second qnode for comparison. eg: Q146 (house cat)
- `embedding_type`: type of embedding vector(s) to be used, valid values are [`complex`, `transe`, `text`, `class`]

## Examples

1. `https://kgtk.isi.edu/similarity_api?q1=Q144&q2=Q146&embedding_type=complex`

Result: 
```
{
  "similarity": 0.6160156449306466,
  "q1": "Q144",
  "q1_label": "dog",
  "q2": "Q146",
  "q2_label": "house cat"
}
```

2. `https://https://kgtk.isi.edu/similarity_api?q1=Q144&q2=Q146&embedding_type=text`

Result:
```
{
  "similarity": 0.670601640738558,
  "q1": "Q144",
  "q1_label": "dog",
  "q2": "Q146",
  "q2_label": "house cat"
}
```

3. `https://kgtk.isi.edu/similarity_api?q1=Q76&q2=Q30&embedding_type=transe`

Result:
```
{
  "similarity": 0.30353878656533795,
  "q1": "Q76",
  "q1_label": "Barack Obama",
  "q2": "Q30",
  "q2_label": "United States of America"
}
```

4. `https://kgtk.isi.edu/similarity_api?q1=Q31&q2=Q142&embedding_type=class`

Result:
```
{
  "similarity": 0.7720331034066785,
  "q1": "Q142",
  "q1_label": "France",
  "q2": "Q31",
  "q2_label": "Belgium"
}
```

# KGTK Semantic Similarity - Call with a file

Deployed URL: `https://kgtk.isi.edu/similarity_api`

Users can `POST` a file and get all the three similarity scores back using the following code

```
import os
import requests
import pandas as pd


def call_semantic_similarity(input_file, url):
    file_name = os.path.basename(input_file)

    files = {
        'file': (file_name, open(input_file, mode='rb'), 'application/octet-stream')
    }
    resp = requests.post(url, files=files)

    s = resp.json()

    return pd.DataFrame(s)


url = 'https://kgtk.isi.edu/similarity_api'
df = call_semantic_similarity('./test_file.tsv', url)
df.to_csv('test_file_similarity.tsv', index=False, sep='\t')

```
The input file should be a `tsv` file with 2 columns, `q1` and `q2`. A sample input file,

```
q1	q2
Q30	Q46
Q42	Q76
Q144	Q8441
Q144	Q5
Q144	Q6581097
```

The output is a file with three additional columns, `complex`, `transe` and `text`.

```
q1	q2	complex	transe	text
Q30	Q46	0.22498834595030964	0.1942162615818314	0.6726582386099983
Q42	Q76	0.42672478110028406	0.4630779771015916	0.5297489611517847
Q144	Q8441	0.5190834952974804	0.31953818960109237	0.3127916834195704
Q144	Q5	0.30464102198714577	0.23322851740055262	0.5355420570406739
Q144	Q6581097	0.17001426271543524	0.17211050667083094	0.27203387996107525
```
# KGTK Nearest Neighbors

Deployed URL: https://dsbox02.isi.edu:8888

## Parameters

- `qnode`: The input qnode to find nearest neighbors for
- `k`: The number of return nearest neighbors, default, k = 5

## Examples

1. `https://dsbox02.isi.edu:8888/nearest-neighbors?qnode=Q30` # Q30 = United States of Ameria

Result:
```
[
  {
    "qnode": "Q142",
    "score": 9.379401206970215,
    "label": "France"
  },
  {
    "qnode": "Q183",
    "score": 10.275091171264648,
    "label": "Germany"
  },
  {
    "qnode": "Q31",
    "score": 10.707923889160156,
    "label": "Belgium"
  },
  {
    "qnode": "Q35",
    "score": 10.993154525756836,
    "label": "Denmark"
  },
  {
    "qnode": "Q16",
    "score": 10.999225616455078,
    "label": "Canada"
  }
]
```

2. `https://dsbox02.isi.edu:8888/nearest-neighbors?qnode=Q42&k=3` # Q42 = Douglas Adams

Result:
```
    [
    {
      "qnode": "Q937084",
      "score": 9.607604026794434,
      "label": "Philip Reeve"
    },
    {
      "qnode": "Q737570",
      "score": 9.700998306274414,
      "label": "Jeff Noon"
    },
    {
      "qnode": "Q216398",
      "score": 10.034045219421387,
      "label": "Alan Sillitoe"
    }
]
```

# KGTK Paths

Deployed URL: https://dsbox02.isi.edu:8888

## Parameters

- `source`: The source qnode, start of the path
- `target`: The target qnode, destination of the path
- `hops`: Maximum number of hops between source and target qnodes. By default, 2. Maximum allowed: 4.

## Examples

1. `https://dsbox02.isi.edu:8888/paths?source=Q76&target=Q30&hops=2` # Source: Obama, Target: United States

Result:
```
  [
  [
    "Q76",
    "P102",
    "Q29552",
    "P17",
    "Q30"
  ],
  [
    "Q76",
    "P102",
    "Q29552",
    "P2541",
    "Q30"
  ],
  [
    "Q76",
    "P103",
    "Q1860",
    "P17",
    "Q30"
  ],
  [
    "Q76",
    "P1038",
    "Q2856335",
    "P27",
    "Q30"
  ],
  [
    "Q76",
    "P108",
    "Q131252",
    "P17",
    "Q30"
  ],
  [
    "Q76",
    "P108",
    "Q3483312",
    "P17",
    "Q30"
  ],
  [
    "Q76",
    "P108",
    "Q4537781",
    "P17",
    "Q30"
  ]
]
```
