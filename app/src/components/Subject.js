import React, { useRef, useState } from 'react'

import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'

import Input from './Input'


const useStyles = makeStyles(theme => ({
  paper: {
    marginTop: theme.spacing(3),
    paddingTop: theme.spacing(6),
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(4),
    paddingBottom: theme.spacing(6),
    backgroundColor: 'rgba(254, 254, 254, 0.25)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    position: 'relative',
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(3),
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
  checkbox: {
    color: '#fefefe',
    position: 'absolute',
    top: theme.spacing(5),
    left: theme.spacing(0),
    transform: 'scale(1.5)',
    '& .Mui-checked': {
      color: 'limegreen',
    },
    '& .MuiCheckbox-colorSecondary.Mui-checked': {
      color: 'limegreen',
    },
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

  const renderResults = () => {
    return (
      <Typography component="h3" variant="h3">
        {JSON.stringify(results)}
      </Typography>
    )
  }

  const renderSubject = () => {
    return (
      <Typography component="h3" variant="h3">
        {JSON.stringify(subject)}
      </Typography>
    )
  }

  return (
    <React.Fragment>
      {subject ? renderSubject() : renderSearch()}
    </React.Fragment>
  )
}


export default Subject
