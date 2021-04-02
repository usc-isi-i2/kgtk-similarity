import React, { useRef } from 'react'

import TextField from '@material-ui/core/TextField'
import { makeStyles } from '@material-ui/styles'


const useStyles = makeStyles(theme => ({
  textFieldInput: {
    fontSize: props => props.fontSize || '2rem',
  },
  textFieldLabel: {
    fontSize: props => props.labelFontSize || '1.25rem',
  },
}))


const Input = ({ autoFocus, fontSize, label, labelFontSize, onChange }) => {

  const classes = useStyles({fontSize, labelFontSize})

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
          input: classes.textFieldInput,
        },
      }}
      InputLabelProps={{
        className: classes.textFieldLabel,
      }}
    />
  )
}


export default Input
