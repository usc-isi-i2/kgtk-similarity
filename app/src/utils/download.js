const downloadCSV = (types, subject, qnodes) => {
  const rows = [
    ['q1', 'q2', ...types.map(type => type.label)]
  ]

  qnodes.forEach(item => {
    rows.push([
      subject.qnode,
      item.qnode,
      ...types.map(type => item.similarity[type.value]),
    ])
  })

  const csvContent = 'data:text/csv;charset=utf-8,'
    + rows.map(row => row.join(',')).join('\n')

  const link = document.createElement('a')
  if (link.download !== undefined) { // feature detection
    link.setAttribute('href', encodeURI(csvContent))
    link.setAttribute('download', `${subject.qnode}_similarity.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}


export default downloadCSV
