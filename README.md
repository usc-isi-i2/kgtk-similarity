# KGTK Semantic Similarity


## Parameters

- `q1`: The first qnode for comparison, eg: Q144 (dog)
- `q2`: The second qnode for comparison. eg: Q146 (house cat)
- `embedding_type`: type of embedding vector(s) to be used, valid values are [`complex`, `transe`, `text`]

## Examples

1. `/similarity_api?q1=Q144&q2=Q146&embedding_type=complex

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

2. `/similarity_api?q1=Q144&q2=Q146&embedding_type=text`

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
