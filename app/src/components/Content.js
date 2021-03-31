import React, {useState} from 'react'

import Header from './Header'
import Search from './Search'
import Subject from './Subject'
import TestNodes from './TestNodes'


const Content = () => {

  const [subject, setSubject] = useState()

  return (
    <React.Fragment>
      <Header />
      { subject ? (
        <Subject
          subject={subject}
          setSubject={subject => setSubject(subject)} />
      ) : (
        <Search setSubject={subject => setSubject(subject)} />
      )}
    </React.Fragment>
  )
}


export default Content
