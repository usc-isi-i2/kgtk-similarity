import React, { useRef, useState } from 'react'

import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import CancelIcon from '@material-ui/icons/Cancel'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'

import Input from './Input'


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
  form: {
    width: '100%', // Fix IE 11 issue.
  },
  result: {
    position: 'relative',
    marginTop: theme.spacing(3),
  },
  link: {
    width: '97%',
    display: 'inline-block',
    padding: theme.spacing(1),
    marginLeft: theme.spacing(5),
    color: '#fefefe',
    transition: '0.2s background ease',
    '&:hover': {
      background: 'rgba(255, 255, 255, 0.1)',
      textDecoration: 'none',
      cursor: 'pointer',
    },
  },
  index: {
    color: '#fefefe',
    position: 'absolute',
    top: theme.spacing(1),
    left: theme.spacing(1),
  },
  label: {
    color: '#fefefe',
    textDecoration: 'underline',
  },
  description: {
    color: '#fefefe',
    textDecoration: 'none',
    marginTop: theme.spacing(1),
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


const Subject = ({ title }) => {

  const classes = useStyles()

  const timeoutID = useRef(null)

  const [query, setQuery] = useState('')
  const [subject, setSubject] = useState()
  const [results, setResults] = useState([])

  const submitQuery = query => {
    // Construct the url with correct parameters
    let url = `https://kgtk.isi.edu/api/`
    if ( query ) {
      url += `${query}?type=ngram&extra_info=true&language=en&item=qnode`
      return fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((response) => response.json())
      .then((results) => {
        setResults(results)
      })
    }
  }

  const handleSubmit = event => {
    event.preventDefault()
    submitQuery(query)
  }

  const handleOnChange = query => {
    setQuery(query)
    if ( !query ) {
      setResults([])
    } else {
      clearTimeout(timeoutID.current)
      timeoutID.current = setTimeout(() => {
        submitQuery(query)
      }, 500)
    }
  }

  const renderSearch = () => {
    if ( !subject ) {
      return (
        <form className={ classes.form } noValidate
          onSubmit={event => handleSubmit(event)}>
          <Grid container spacing={ 3 }>
            <Grid item xs={ 12 }>
              <Paper component="div" className={ classes.paper } square>
                <Grid container spacing={ 3 }>
                  <Grid item xs={ 12 }>
                    <Input autoFocus={ true } label={'Search'}
                      onChange={query => handleOnChange(query)}/>
                  </Grid>
                </Grid>
              </Paper>
              {renderResults()}
            </Grid>
          </Grid>
        </form>
      )
    }
  }

  const renderResults = () => {
    return results.map((result, i) => (
      <Grid item xs={ 12 } key={ i } className={ classes.result }>
        <Typography
          component="h5"
          variant="h5"
          className={ classes.index }>
          { i + 1 }.
        </Typography>
        <Link
          onClick={event => setSubject(result)}
          className={ classes.link }>
          <Typography
            component="h5"
            variant="h5"
            className={ classes.label }>
            { result.label[0] } ({ result.qnode })
          </Typography>
          <Typography
            component="p"
            variant="body1"
            className={ classes.description }>
            <b>Description:</b> { !!result.description[0] ? result.description[0] : 'No Description'}
          </Typography>
          { !!result.alias.length ? (
            <Typography
              component="p"
              variant="body1"
              className={ classes.description }>
              <b>Alias:</b> { result.alias.join(', ') }
            </Typography>
          ) : null }
        </Link>
      </Grid>
    ))
  }

  const renderSubject = () => {
    if ( subject ) {
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
  }

  return (
    <React.Fragment>
      {renderSearch()}
      {renderSubject()}
    </React.Fragment>
  )
}


export default Subject
