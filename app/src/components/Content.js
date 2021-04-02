import React, {useState} from 'react'

import Header from './Header'
import Search from './Search'
import Subject from './Subject'
import TestNodes from './TestNodes'


const TYPES = [{
  label: 'ComplEx',
  value: 'complex',
}, {
  label: 'TransE',
  value: 'transe',
}, {
  label: 'Text',
  value: 'text',
}]


const Content = () => {

  const [subject, setSubject] = useState()
  const [selected, setSelected] = useState([])

  const downloadCSV = () => {
    const rows = [
      ['q1', 'q2', ...TYPES.map(type => type.label)]
    ]
    selected.forEach(q2 => {
      rows.push([subject.qnode, q2.qnode, ...TYPES.map(type => q2.similarity[type.value])])
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

  return (
    <React.Fragment>
      <Header
        subject={subject}
        download={downloadCSV} />
      { subject ? (
        <React.Fragment>
          <Subject
            subject={subject}
            setSubject={subject => setSubject(subject)} />
          <TestNodes
            types={TYPES}
            subject={subject}
            selected={selected}
            setSelected={setSelected}
          />
        </React.Fragment>
      ) : (
        <Search setSubject={subject => setSubject(subject)} />
      )}
    </React.Fragment>
  )
}


export default Content
