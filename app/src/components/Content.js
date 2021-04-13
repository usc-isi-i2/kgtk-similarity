import React, {useState} from 'react'

import Header from './Header'
import Search from './Search'
import Subject from './Subject'
import TestNodes from './TestNodes'

import downloadCSV from '../utils/download'


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

  const updateSubject = newSubject => {
    setSubject(subject => {
      setSelected(selected.map(x => ({...x, similarity: {}})))
      return newSubject
    })
  }

  return (
    <React.Fragment>
      <Header
        subject={subject}
        selected={selected}
        download={() => downloadCSV(TYPES, subject, selected)} />
      { subject ? (
        <React.Fragment>
          <Subject
            subject={subject}
            setSubject={subject => updateSubject(subject)} />
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
