import React from 'react'

import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/styles'

import Logo from './Logo'


const useStyles = makeStyles(theme => ({
  header: {
    color: '#fefefe',
    marginTop: theme.spacing(3),
  },
  logo: {
    display: 'inline-block',
    verticalAlign: 'middle',
    width: theme.spacing(12),
    height: theme.spacing(12),
    marginRight: theme.spacing(2),
  },
}))


const Header = () => {

  const classes = useStyles()

  return (
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
  )
}


export default Header
