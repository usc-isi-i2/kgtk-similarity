import React from 'react'

import {
  withStyles,
  ThemeProvider,
  createMuiTheme,
} from '@material-ui/core/styles'
import Container from '@material-ui/core/Container'
import CssBaseline from '@material-ui/core/CssBaseline'

import Title from './components/Title'
import Subject from './components/Subject'
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

  const theme = createMuiTheme()

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="xl">
        <div id="top"/>
        <CssBaseline/>
        <Title title="Knowledge Graph Semantic Similarity" />
        <Subject />
        <ArrowUp/>
      </Container>
    </ThemeProvider>
  )
}


export default withStyles(styles)(App)
