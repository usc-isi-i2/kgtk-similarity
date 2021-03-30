# wikidata-semantic-similarity


## Parameters

- `q1`: The first qnode for comparison, eg: Q76
- `q2`: The second qnode for comparison. eg: Q30
- `embedding_type`: type of embedding vector(s) to be used, valid values are [`complex`, `transe`, `text`]

## Examples

1. `/similarity?q1=Q76&q2=Q30&embedding_type=complex`

Result: 
```
{
  "similarity": 5.083971988756343,
  "q1": "Q76",
  "q1_label": "Barack Obama",
  "q2": "Q30",
  "q2_label": "United States of America"
}
```

2. `/similarity?q1=Q76&q2=Q30&embedding_type=text`

Result:
```
{
  "similarity": 0.6253171604635588,
  "q1": "Q76",
  "q1_label": "Barack Obama",
  "q2": "Q30",
  "q2_label": "United States of America"
}
```
