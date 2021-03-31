import React from 'react'

import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import { makeStyles } from '@material-ui/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(6),
    paddingTop: theme.spacing(6),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(6),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#fefefe',
  },
  cancel: {
    color: '#ccc',
    position: 'absolute',
    top: theme.spacing(7),
    right: theme.spacing(5),
    transform: 'scale(2)',
    cursor: 'pointer',
    transition: 'all 350ms ease',
    '&:hover': {
      color: '#fefefe',
    },
  },
}))


const TestNodes = ({ subject }) => {

  const classes = useStyles()

  return (
    <Paper component="div" square>
      <Grid container spacing={ 3 }>
        <Grid item xs={ 12 }>
        </Grid>
      </Grid>
    </Paper>
  )
}


export default TestNodes
