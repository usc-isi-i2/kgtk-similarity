import React, { useEffect, useRef, useState } from 'react'

import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import SortIcon from '@material-ui/icons/Sort'
import CancelIcon from '@material-ui/icons/Cancel'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'


import Input from './Input'


const useStyles = makeStyles(theme => ({
  headerWrapper: {
    marginTop: theme.spacing(3),
  },
  wrapper: {
    marginTop: theme.spacing(1),
  },
  paper: {
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
  cancel: {
    color: 'rgba(255, 255, 255, 0.35)',
    transform: 'scale(2)',
    cursor: 'pointer',
    transition: 'all 350ms ease',
    '&:hover': {
      color: 'rgba(255, 255, 255, 0.5)',
    },
  },
  header: {
    fontWeight: 'bolder',
    userSelect: 'none',
    cursor: 'pointer',
    color: '#333',
    '&:hover': {
      color: 'rgba(0, 255, 0, 0.5)',
      transition: 'all 250ms ease',
      transform: 'scale(1.1)',
    },
    '&:hover > svg.MuiSvgIcon-root': {
      transition: 'all 250ms ease',
      color: 'rgba(0, 255, 0, 0.5) !important',
    },
  },
  sortIcon: {
    marginLeft: theme.spacing(3),
    verticalAlign: 'bottom',
    cursor: 'pointer',
    color: '#333',
  },
  result: {
    position: 'relative',
    marginTop: theme.spacing(1),
  },
  link: {
    width: '90%',
    display: 'inline-block',
    padding: theme.spacing(1),
    marginLeft: theme.spacing(5),
    color: '#333',
    transition: '0.2s background ease',
    '&:hover': {
      color: '#111',
      background: 'rgba(253, 214, 0, 0.25)',
      textDecoration: 'none',
      cursor: 'pointer',
    },
  },
  index: {
    color: '#333',
    position: 'absolute',
    top: theme.spacing(2.5),
    left: theme.spacing(1),
  },
  label: {
    color: '#333',
    textDecoration: 'underline',
  },
  description: {
    color: '#333',
    textDecoration: 'none',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis',
  },
  progressBar: {
    backgroundColor: 'rgba(0, 255, 0, 0.35)',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '0%',
    height: '100%',
    transition: 'width 250ms ease',
  },
  score: {
    width: '100%',
    cursor: 'pointer',
    textAlign: 'center',
    fontWeight: 'bolder',
    zIndex: '15',
  },
  placeholder: {
    width: '100%',
    textAlign: 'center',
  },
}))


const TestNodes = ({ types, subject, selected, setSelected }) => {

  const classes = useStyles()

  const timeoutID = useRef(null)

  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [sortType, setSortType] = useState(types[0])

  useEffect(() => {
    setSelected([
      ...selected.sort((q1, q2) => {
        return q2.similarity[sortType.value] - q1.similarity[sortType.value]
      })
    ])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sortType])

  useEffect(() => {
    // fetch similarities for this qnode and update
    selected.forEach(alt => {
      types.forEach(type => {
        if ( !alt.similarity[type.value] ) {
          let url = `/similarity_api?q1=${subject.qnode}`
          url += `&q2=${alt.qnode}`
          url += `&embedding_type=${type.value}`
          return fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          })
          .then((response) => response.json())
          .then((results) => {
            if ( 'error' in results || !results.similarity ) {
              alt.similarity[type.value] = '--'
            } else {
              alt.similarity[type.value] = Math.abs(results.similarity)
            }
            setSelected([
              ...[
                ...selected.filter(item => item.qnode !== alt.qnode),
                alt,
              ].sort((q1, q2) => (
                q2.similarity[sortType.value] - q1.similarity[sortType.value]
              ))
            ])
          })
        }
      })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subject.qnode, sortType.value, selected])

  const renderHeader = () => {
    return (
      <Grid container spacing={1} className={classes.headerWrapper}>
        <Grid item xs={4}>
        </Grid>
        <Grid item xs={7}>
          <Grid container spacing={1}>
            {types.map(type => (
              <Grid item xs={12 / types.length} key={type.value}>
                <Paper component="div" style={{ alignItems: 'center' }}
                  className={classes.paper} square>
                  <Typography component="h5" variant="h5"
                    onClick={() => setSortType(type)}
                    className={classes.header}>
                    {type.label}
                    <SortIcon fontSize="large" className={classes.sortIcon}
                      style={{ color: !!selected.length && sortType === type ? 'rgba(0, 255, 0, 0.5)' : '#333' }} />
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid item xs={1}>
        </Grid>
      </Grid>
    )
  }

  const renderSelected = () => {
    return selected.map(selected => (
      <Grid container spacing={1}
        className={classes.wrapper} key={selected.qnode}>
        <Grid item xs={4}>
          <Link
            href={`https://ringgaard.com/kb/${selected.qnode}`}
            target="_blank"
            className={ classes.link }>
            <Typography
              component="h5"
              variant="h5"
              className={ classes.label }>
              { selected.label[0] } ({ selected.qnode })
            </Typography>
            <Typography
              component="p"
              variant="body1"
              className={ classes.description }>
              {!!selected.description[0] ? selected.description[0] : 'No Description'}
            </Typography>
          </Link>
        </Grid>
        <Grid item xs={7}>
          <Grid container spacing={1}>
            {types.map(type => (
              <Grid item xs={12 / types.length} key={type.value}>
                <Paper component="div"
                  className={classes.paper} square>
                  <div className={classes.progressBar}
                    style={{
                      width: `${Math.round(selected.similarity[type.value] * 100)}%`,
                      backgroundColor: `rgba(${255 - (255 * (Math.round(selected.similarity[type.value] * 100) / 100))}, ${255 * (Math.round(selected.similarity[type.value] * 100) / 100)}, 0, ${1 - (0.35 * (Math.round(selected.similarity[type.value] * 100) / 100))})`,
                  }}></div>
                  {!!selected.similarity[type.value] &&
                    selected.similarity[type.value] !== '--' ? (
                    <React.Fragment>
                      <Typography component="h5" variant="h5"
                        className={classes.score}
                        title={selected.similarity[type.value]}>
                        {selected.similarity[type.value].toFixed(3)}
                      </Typography>
                    </React.Fragment>
                  ) : (
                    <Typography component="h5" variant="h5"
                      className={classes.placeholder}>
                      --
                    </Typography>
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Grid>
        <Grid item xs={1} style={{ textAlign: "center" }}>
          <IconButton className={classes.cancel}
            onClick={event => removeSelected(selected)}>
            <CancelIcon fontSize="large" />
          </IconButton>
        </Grid>
      </Grid>
    ))
  }

  const submitQuery = query => {
    // Construct the url with correct parameters
    let url = `https://kgtk.isi.edu/api`
    if ( query ) {
      url += `?q=${query}&type=ngram&extra_info=true&language=en&item=qnode`
      return fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((response) => response.json())
      .then((results) => {
        setResults([
          ...results.filter(q1 => !selected.find(q2 => q1.qnode === q2.qnode))
        ])
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
      <Grid container spacing={1} className={classes.wrapper}>
        <Grid item xs={4}>
        </Grid>
        <Grid item xs={7}>
          <form className={ classes.form } noValidate
            onSubmit={event => handleSubmit(event)}>
            <Grid container spacing={1}>
              <Grid item xs={12}>
                <Paper component="div" className={ classes.paper } square>
                  <Grid container spacing={1}>
                    <Grid item xs={12}>
                      <Input
                        fontSize='1.5em'
                        labelFontSize='1.25em'
                        autoFocus={ true }
                        label={'search to compare q-nodes'}
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

  const addSelected = result => {
    result.similarity = {}
    setSelected([
      ...selected.filter(item => item.qnode !== result.qnode),
      result,
    ])
    setResults([
      ...results.filter(item => item.qnode !== result.qnode),
    ])
  }

  const removeSelected = result => {
    setSelected([
      ...selected.filter(item => item.qnode !== result.qnode),
    ])
    setResults([
      result,
      ...results,
    ])
  }

  const renderResults = () => {
    return results.map((result, i) => (
      <Grid key={i} container spacing={1} className={classes.result}>
        <Grid item xs={12}>
          <Typography
            component="h5"
            variant="h5"
            className={ classes.index }>
            { i + 1 }.
          </Typography>
          <Link
            onClick={event => addSelected(result)}
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
      </Grid>
    ))
  }

  return (
    <React.Fragment>
      {renderHeader()}
      {renderSelected()}
      {renderSearch()}
    </React.Fragment>
  )
}


export default TestNodes
