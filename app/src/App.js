import React from 'react'

import {
  withStyles,
  ThemeProvider,
  createMuiTheme,
} from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
import CssBaseline from '@material-ui/core/CssBaseline'

import Content from './components/Content'
import ArrowUp from './components/ArrowUp'


const styles = theme => ({
  '@global': {
    body: {
      background: 'linear-gradient(150deg, #708090, #002133)',
      backgroundAttachment: 'fixed',
      backgroundSize: '100% 150%',
      padding: theme.spacing(3, 1),
      height: '100vh',
    },
  },
})


const App = () => {

  const theme = createMuiTheme({
    overrides: {
      MuiTextField: {
        root: {
          color: '#fefefe',
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


export default withStyles(styles)(App)
