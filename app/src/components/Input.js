import React, { useRef } from 'react'

import TextField from '@material-ui/core/TextField'
import { makeStyles } from '@material-ui/styles'


const useStyles = makeStyles(theme => ({
  textField: {
    fontSize: props => props.fontSize || '2em',
  },
}))


const Input = ({ autoFocus, fontSize, label, onChange }) => {

  const classes = useStyles({fontSize})

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
      InputProps={{
        classes: {
          input: classes.textField,
        },
      }}
    />
  )
}


export default Input
