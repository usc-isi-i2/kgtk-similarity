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
    console.log('download requested')
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
