import React, { useRef } from 'react'

import TextField from '@material-ui/core/TextField'
import { withStyles } from '@material-ui/core/styles'


const CustomTextField = withStyles({
  root: {
    '& .MuiFormLabel-root': {
      '@media (min-width:600px)': {
        fontSize: '1.25rem',
        opacity: 0.85,
      },
      color: '#fefefe',
    },
    '&.small .MuiFormLabel-root': {
      '@media (min-width:600px)': {
        fontSize: '1rem',
      }
    },
    '& .MuiInput-input': {
      '@media (min-width:600px)': {
        fontSize: '2rem',
      },
      color: '#fefefe',
      transition: 'background 0.3s ease',
    },
    '&.small .MuiInput-input': {
      '@media (min-width:600px)': {
        fontSize: '1.5rem'
      }
    },
    '& label.Mui-focused': {
      color: '#fefefe',
    },
    '&:hover .MuiInput-input': {
      background: 'rgba(255, 255, 255, 0.1)',
    },
    '&:hover .MuiInput-underline:before': {
      borderBottomColor: '#fefefe',
      borderBottom: '3px solid',
    },
    '& .MuiInput-underline:before': {
      borderBottomColor: '#fefefe',
    },
    '& .MuiInput-underline:after': {
      borderBottomColor: '#fefefe',
    },
    '& .MuiInputLabel-shrink': {
      transform: 'translate(0px, -10px)',
    },
  },
})(TextField)


const Input = ({ autoFocus, label, onChange }) => {

  const inputElement = useRef(null)

  const handleOnChange = event => {
    onChange(event.target.value)
  }

  return (
    <CustomTextField
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
