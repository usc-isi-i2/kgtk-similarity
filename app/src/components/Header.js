import React from 'react'

import GetAppIcon from '@material-ui/icons/GetApp'
import IconButton from '@material-ui/core/IconButton'
import Typography from '@material-ui/core/Typography'
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
    position: 'absolute',
    top: theme.spacing(6),
    right: theme.spacing(4),
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


const Header = () => {

  const classes = useStyles()

  return (
    <React.Fragment>
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
      <Typography
        component="h5"
        variant="h5"
        className={ classes.download }>
        Download CSV
        <GetAppIcon fontSize="large" />
      </Typography>
    </React.Fragment>
  )
}


export default Header
