import React from 'react'

import Paper from '@material-ui/core/Paper'
import CancelIcon from '@material-ui/icons/Cancel'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
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
    color: 'rgba(255, 255, 255, 0.35)',
    position: 'absolute',
    top: theme.spacing(7),
    right: theme.spacing(5),
    transform: 'scale(2)',
    cursor: 'pointer',
    transition: 'all 350ms ease',
    '&:hover': {
      color: 'rgba(255, 255, 255, 0.5)',
    },
  },
}))


const Subject = ({ subject, setSubject }) => {

  const classes = useStyles()

  return (
    <Paper component="div" className={ classes.paper } square>
      <Typography component="h4" variant="h4">
        <b>{ subject.label[0] } ({ subject.qnode })</b>
      </Typography>
      <Typography component="h5" variant="h5">
        { subject.description[0] }
      </Typography>
      <IconButton className={classes.cancel}
        onClick={event => setSubject(null)}>
        <CancelIcon fontSize="large" />
      </IconButton>
    </Paper>
  )
}


export default Subject
