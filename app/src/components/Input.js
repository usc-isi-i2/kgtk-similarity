import React, { useRef } from 'react'

import TextField from '@material-ui/core/TextField'
import { withStyles } from '@material-ui/core/styles'


const Input = ({ autoFocus, label, onChange }) => {

  const inputElement = useRef(null)

  const handleOnChange = event => {
    onChange(event.target.value)
  }

  return (
    <TextField
      ref={element => inputElement.current = element}
      id={'q'}
      name={'q'}
      label={label}
      autoFocus={autoFocus}
      autoComplete="off"
      fullWidth
      onChange={event => handleOnChange(event)}
    />
  )
}


export default Input
