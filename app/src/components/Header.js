import React from 'react'

import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import GetAppIcon from '@material-ui/icons/GetApp'
import RefreshIcon from '@material-ui/icons/Refresh'
import { makeStyles } from '@material-ui/styles'

import Logo from './Logo'


const useStyles = makeStyles(theme => ({
  header: {
    color: '#333',
    marginTop: theme.spacing(1),
  },
  logo: {
    display: 'inline-block',
    verticalAlign: 'middle',
    width: theme.spacing(12),
    height: theme.spacing(12),
    marginRight: theme.spacing(2),
  },
  button: {
    color: '#333',
    cursor: 'pointer',
    userSelect: 'none',
    display: 'inline-block',
    marginTop: theme.spacing(5),
    marginLeft: theme.spacing(10),
    '&:hover': {
      textDecoration: 'underline',
    },
    '& svg.MuiSvgIcon-root': {
      color: '#333',
      verticalAlign: 'bottom',
      marginLeft: theme.spacing(1),
    },
  },
}))


const Header = ({ subject, selected, download }) => {

  const classes = useStyles()

  const refresh = () => {
    window.location.reload()
  }

  return (
    <Grid container spacing={3} justify="space-between">
      <Grid item>
        <Typography
          component="h3"
          variant="h3"
          className={ classes.header }>
          <a href="https://github.com/usc-isi-i2/kgtk"
            title="Knowledge Graph Toolkit"
            rel="noopener noreferrer nofollow"
            target="_blank">
            <div className={ classes.logo }>
              <Logo/>
            </div>
          </a>
          Knowledge Graph Semantic Similarity
        </Typography>
      </Grid>
      <Grid item>
        {!!subject && (
          <Typography
            component="h5"
            variant="h5"
            onClick={refresh}
            className={classes.button}>
            Reset
            <RefreshIcon fontSize="large" />
          </Typography>
        )}
        {!!subject && !!selected.length && (
          <Typography
            component="h5"
            variant="h5"
            onClick={download}
            className={classes.button}>
            Download CSV
            <GetAppIcon fontSize="large" />
          </Typography>
        )}
      </Grid>
    </Grid>
  )
}


export default Header
