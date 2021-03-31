import React, { useRef, useState } from 'react'

import Grid from '@material-ui/core/Grid'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'


import Input from './Input'


const useStyles = makeStyles(theme => ({
  wrapper: {
    marginTop: theme.spacing(6),
  },
  paper: {
    paddingTop: theme.spacing(3),
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
    paddingBottom: theme.spacing(3),
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


const TestNodes = ({ subject }) => {

  const classes = useStyles()

  const timeoutID = useRef(null)

  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  const renderHeader = () => {
    return (
      <Grid container spacing={3} className={classes.wrapper}>
        <Grid item xs={3}>
        </Grid>
        <Grid item xs={8}>
          <Paper component="div"
            className={classes.paper} square>
            <Grid container spacing={3}>
              <Grid item xs={4}>
                <Typography component="h5" variant="h5" style={{ textAlign: 'center' }}>
                  ComplEx
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography component="h5" variant="h5" style={{ textAlign: 'center' }}>
                  TransE
                </Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography component="h5" variant="h5" style={{ textAlign: 'center' }}>
                  Text
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        <Grid item xs={1}>
        </Grid>
      </Grid>
    )
  }

  const renderResults = () => {
    return results.map(result => {JSON.stringify(result)})
  }

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
      <Grid container spacing={3} className={classes.wrapper}>
        <Grid item xs={3}>
        </Grid>
        <Grid item xs={8}>
          <form className={ classes.form } noValidate
            onSubmit={event => handleSubmit(event)}>
            <Grid container spacing={ 3 }>
              <Grid item xs={ 12 }>
                <Paper component="div" className={ classes.paper } square>
                  <Grid container spacing={ 3 }>
                    <Grid item xs={ 12 }>
                      <Input autoFocus={ true } label={'search to compare q-nodes'}
                        onChange={query => handleOnChange(query)}/>
                    </Grid>
                  </Grid>
                </Paper>
                {renderResults()}
              </Grid>
            </Grid>
          </form>
        </Grid>
        <Grid item xs={1}>
        </Grid>
      </Grid>
    )
  }

  return (
    <React.Fragment>
      {renderHeader()}
      {renderResults()}
      {renderSearch()}
    </React.Fragment>
  )
}


export default TestNodes
