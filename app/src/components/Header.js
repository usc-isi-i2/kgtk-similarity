import React from 'react'

import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import GetAppIcon from '@material-ui/icons/GetApp'
import { makeStyles } from '@material-ui/styles'

import Logo from './Logo'


const useStyles = makeStyles(theme => ({
  header: {
    color: '#fefefe',
    marginTop: theme.spacing(1),
  },
  logo: {
    display: 'inline-block',
    verticalAlign: 'middle',
    width: theme.spacing(12),
    height: theme.spacing(12),
    marginRight: theme.spacing(2),
  },
  download: {
    color: '#fefefe',
    cursor: 'pointer',
    userSelect: 'none',
    marginTop: theme.spacing(5),
    '&:hover': {
      textDecoration: 'underline',
    },
    '& svg.MuiSvgIcon-root': {
      color: '#fefefe',
      verticalAlign: 'bottom',
      marginLeft: theme.spacing(2),
    },
  },
}))


const Header = ({ subject, selected, download }) => {

  const classes = useStyles()

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
      {!!subject && !!selected.length && (
        <Typography
          component="h5"
          variant="h5"
          onClick={download}
          className={ classes.download }>
          Download CSV
          <GetAppIcon fontSize="large" />
        </Typography>
      )}
      </Grid>
    </Grid>
  )
}


export default Header
