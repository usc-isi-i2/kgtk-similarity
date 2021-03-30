import React from 'react'
import { Button } from '@material-ui/core/'
import { withStyles } from '@material-ui/core/styles'


const styles = theme => ({
  root: {
    boxShadow: '0px 3px 5px -1px rgba(0,0,0,0.2), 0px 6px 10px 0px rgba(0,0,0,0.14), 0px 1px 18px 0px rgba(0,0,0,0.12)',
    background: 'linear-gradient(150deg, #EC6A5A, #A662D6)',
    backgroundSize: '100% 150%',
    border: 0,
    borderRadius: 3,
    color: 'white',
    fontSize: theme.spacing(3.5),
    marginTop: theme.spacing(3),
    padding: theme.spacing(3, 12),
    transition: 'all 0.15s ease',
    opacity: 0.8,
    '&:hover': {
      opacity: 1,
    },
  },
})


class Submit extends React.Component {

  render() {
    const { classes, disabled } = this.props
    return (
      <Button type="submit" disabled={disabled} className={classes.root}>
        Submit
      </Button>
    )
  }
}


export default withStyles(styles)(Submit)
