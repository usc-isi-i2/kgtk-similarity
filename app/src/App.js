import React from 'react'

import {
  ThemeProvider,
  createMuiTheme,
} from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
import CssBaseline from '@material-ui/core/CssBaseline'

import Content from './components/Content'
import ArrowUp from './components/ArrowUp'


const App = () => {

  const theme = createMuiTheme({
    overrides: {
      MuiCssBaseline: {
        '@global': {
          html: {
            WebkitFontSmoothing: 'auto',
          },
          body: {
            background: '#fefefe',
            color: '#333',
          },
        },
      },
      MuiTextField: {
        root: {
          color: '#333',
          '& .MuiFormLabel-root': {
            '@media (min-width:600px)': {
              opacity: 0.85,
            },
            color: '#333',
          },
          '& .MuiInput-input': {
            color: '#333',
            transition: 'background 0.3s ease',
          },
          '&.small .MuiInput-input': {
            '@media (min-width:600px)': {
              fontSize: '1.5rem'
            }
          },
          '& label.Mui-focused': {
            color: '#333',
          },
          '&:hover .MuiInput-input': {
            background: 'rgba(255, 255, 255, 0.1)',
          },
          '&:hover .MuiInput-underline:before': {
            borderBottomColor: '#333',
            borderBottom: '3px solid',
          },
          '& .MuiInput-underline:before': {
            borderBottomColor: '#333',
          },
          '& .MuiInput-underline:after': {
            borderBottomColor: '#333',
          },
          '& .MuiInputLabel-shrink': {
            transform: 'translate(0px, -10px)',
          },
        },
      },
    },
  })

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="xl">
        <div id="top"/>
        <CssBaseline/>
        <Content />
        <ArrowUp />
      </Container>
    </ThemeProvider>
  )
}


export default App
