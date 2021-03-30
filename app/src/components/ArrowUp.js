import React from 'react'
import Zoom from '@material-ui/core/Zoom'
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward'
import useScrollTrigger from '@material-ui/core/useScrollTrigger'
import { withStyles } from '@material-ui/core/styles'


const styles = theme => ({
  root: {
    position: 'fixed',
    color: 'white',
    cursor: 'pointer',
    fontSize: theme.spacing(1),
    bottom: theme.spacing(1),
    right: theme.spacing(1),
    '@media (min-width:1000px)': {
      fontSize: theme.spacing(2),
      bottom: theme.spacing(2),
      right: theme.spacing(2),
    },
    '@media (min-width:1200px)': {
      fontSize: theme.spacing(5),
      bottom: theme.spacing(5),
      right: theme.spacing(5),
    },
  },
})


const HideArrow = props => {
  const { children, classes } = props

  const trigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 100,
  })

  const handleClick = event => {
    const anchor = (event.target.ownerDocument || document).querySelector('#top')

    if (anchor) {
      anchor.scrollIntoView()
    }
  }

  return (
    <Zoom in={trigger}>
      <div onClick={handleClick} role="presentation" className={classes.root}>
        {children}
      </div>
    </Zoom>
  )
}


const ArrowUp = props => {

  return (
    <HideArrow {...props}>
      <ArrowUpwardIcon fontSize={'large'} />
    </HideArrow>
  )
}


export default withStyles(styles)(ArrowUp)
