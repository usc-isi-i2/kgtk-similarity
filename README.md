# KGTK Semantic Similarity

Deployed URL: https://dsbox02.isi.edu:8888

## Parameters

- `q1`: The first qnode for comparison, eg: Q144 (dog)
- `q2`: The second qnode for comparison. eg: Q146 (house cat)
- `embedding_type`: type of embedding vector(s) to be used, valid values are [`complex`, `transe`, `text`]

## Examples

1. `https://dsbox02.isi.edu:8888/qnode-similarity?q1=Q144&q2=Q146&embedding_type=complex`

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

2. `https://dsbox02.isi.edu:8888/qnode-similarity?q1=Q144&q2=Q146&embedding_type=text`

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

3. `https://dsbox02.isi.edu:8888/qnode-similarity?q1=Q76&q2=Q30&embedding_type=transe`

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
