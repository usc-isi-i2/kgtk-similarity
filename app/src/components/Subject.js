import React from 'react'

import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import CancelIcon from '@material-ui/icons/Cancel'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(2),
    paddingTop: theme.spacing(2),
    paddingLeft: theme.spacing(2),
    paddingRight: theme.spacing(2),
    paddingBottom: theme.spacing(2),
    backgroundColor: 'white',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'start',
    position: 'relative',
    color: '#333',
  },
  link: {
    width: '90%',
    display: 'inline-block',
    padding: theme.spacing(1),
    marginLeft: theme.spacing(1),
    color: '#333',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
      textDecoration: 'none',
      cursor: 'pointer',
    },
  },
  label: {
    color: '#333',
    textDecoration: 'underline',
  },
  description: {
    color: '#333',
    textDecoration: 'none',
    marginTop: theme.spacing(1),
  },
  cancel: {
    color: 'rgba(0, 0, 0, 0.2)',
    position: 'absolute',
    top: theme.spacing(4.5),
    right: theme.spacing(4),
    transform: 'scale(2)',
    cursor: 'pointer',
    transition: 'all 350ms ease',
    '&:hover': {
      color: 'rgba(0, 0, 0, 0.35)',
    },
  },
}))


const Subject = ({ subject, setSubject }) => {

  const classes = useStyles()

  return (
    <Paper component="div" className={ classes.paper } square>
      <Link
        href={`https://kgtk.isi.edu/browser/${subject.qnode}`}
        target="_blank"
        className={classes.link}>
        <Typography component="h4" variant="h4" className={classes.label}>
          <b>{ subject.label[0] } ({ subject.qnode })</b>
        </Typography>
        <Typography component="h5" variant="h5" className={classes.description}>
          { subject.description[0] }
        </Typography>
      </Link>
      <IconButton className={classes.cancel}
        onClick={event => setSubject(null)}>
        <CancelIcon fontSize="large" />
      </IconButton>
    </Paper>
  )
}


export default Subject
