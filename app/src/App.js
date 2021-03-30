import React from 'react'
import Container from '@material-ui/core/Container'
import CssBaseline from '@material-ui/core/CssBaseline'
import Grid from '@material-ui/core/Grid'
import Link from '@material-ui/core/Link'
import Paper from '@material-ui/core/Paper'
import Checkbox from '@material-ui/core/Checkbox'
import Typography from '@material-ui/core/Typography'
import {
  withStyles,
  createMuiTheme,
  responsiveFontSizes,
  ThemeProvider,
} from '@material-ui/core/styles'

import Logo from './components/Logo'
import Input from './components/Input'
import ArrowUp from './components/ArrowUp'


let theme = createMuiTheme()
theme = responsiveFontSizes(theme)


const styles = theme => ({
  '@global': {
    body: {
      background: 'linear-gradient(150deg, #708090, #002133)',
      backgroundAttachment: 'fixed',
      backgroundSize: '100% 150%',
      padding: theme.spacing(3, 1),
      height: '100vh',
    },
  },
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
})


const CustomCheckbox = withStyles({
  root: {
    color: '#fefefe',
    '&$checked': {
      color: 'limegreen',
    },
  },
  checked: {},
})((props) => <Checkbox color="default" {...props} />)


class App extends React.Component {

  constructor (props) {
    super(props)

    this.state = {
      query: '',
      results: [{"qnode": "Q10494269", "description": ["legal term; property consisting of land and the buildings on it"], "label": ["real estate"], "alias": ["land", "realty", "immovable property", "estate", "Dog", "holding", "real property", "property"], "pagerank": 5.684795967898808e-06, "statements": 69, "score": 79.29563}, {"qnode": "Q144", "description": ["domestic animal"], "label": ["dog"], "alias": ["canis familiaris", "canis lupus familiaris", "domestic dog", "dogs"], "pagerank": 5.460435596169821e-06, "statements": 239, "score": 76.16609}, {"qnode": "Q620749", "description": ["principle laid down as inconvertibly true in an ideology or belief system"], "label": ["dogma"], "alias": ["Dogma de fe", "Dogm\u00e1tico", "Dogmas", "Dogmatico"], "pagerank": 1.7346822078508524e-05, "statements": 97, "score": 1.9800247}, {"qnode": "Q1637371", "description": ["heraldic animal"], "label": ["hound"], "alias": ["dog"], "pagerank": 4.408307123201928e-08, "statements": 250, "score": 0.61490244}, {"qnode": "Q38774", "description": ["functional type of dog"], "label": ["hunting dog"], "alias": ["perro cazador", "perros de caza", "perros cazadores"], "pagerank": 3.8470524396394785e-06, "statements": 65, "score": 0.38637075}, {"qnode": "Q990", "description": ["Polish television series"], "label": ["Czterej pancerni i pies"], "alias": ["Four tank-men and a dog"], "pagerank": 5.807815356995845e-06, "statements": 109, "score": 0.36442786}, {"qnode": "Q1968664", "description": ["sport"], "label": ["sled dog racing"], "alias": ["dog sled racing", "sled dog sport", "dogsled racing"], "pagerank": 2.8236281418056866e-06, "statements": 107, "score": 0.30540335}, {"qnode": "Q34969", "description": ["American author, printer, political theorist, politician, postmaster, scientist, inventor, civic activist, statesman, diplomat, Founding Father, and a therapist (1706-1790)"], "label": ["Benjamin Franklin"], "alias": ["The First American", "Silence Dogood", "Ben Franklin", "Franklin"], "pagerank": 6.359405766087189e-06, "statements": 287, "score": 0.2682084}, {"qnode": "Q39367", "description": ["group of closely related and visibly similar domestic dogs"], "label": ["dog breed"], "alias": ["razas de perros", "raza de perros", "raza canina"], "pagerank": 2.2389915806690015e-06, "statements": 47, "score": 0.23923656}, {"qnode": "Q32730", "description": ["Indo-Aryan language spoken in India and Pakistan"], "label": ["Dogri"], "alias": ["Pahari language", "Dogri (macrolanguage)"], "pagerank": 2.346068665909055e-06, "statements": 132, "score": 0.20443295}, {"qnode": "Q755126", "description": ["sign of Chinese zodiac"], "label": ["Dog"], "alias": ["signo del perro"], "pagerank": 1.2932565162460371e-08, "statements": 33, "score": 0.18039274}, {"qnode": "Q5583349", "description": ["language family"], "label": ["Dogri\u2013Kangri languages"], "alias": ["Kangri-Dogri languages"], "pagerank": 2.0587817966082934e-06, "statements": 115, "score": 0.17484382}, {"qnode": "Q9884", "description": ["fourth letter of the Latin alphabet"], "label": ["D"], "alias": ["\u02c8di\u02d0", "d dog", "Delta", "dee", "d"], "pagerank": 1.7108038698108955e-06, "statements": 88, "score": 0.15762143}, {"qnode": "Q20979", "description": ["Northern Athabaskan language spoken by the First Nations T\u0142\u0131\u0328ch\u01eb people of the Canadian territory Northwest Territories"], "label": ["Dogrib"], "alias": ["ISO 639:dgr", "Tlicho language", "Tlicho Yatii language", "Dogrib language", "T\u0142\u0131\u0328ch\u01eb language", "Tlicho Yatii"], "pagerank": 2.1727209247925493e-06, "statements": 131, "score": 0.12888442}, {"qnode": "Q47072", "description": ["explanation of the flow of genetic information within a biological system"], "label": ["Central dogma of molecular biology"], "alias": ["Dogma central de la biologia", "Dogma central de la biologia molecular", "Dogma central de la biolog\u00eda", "Dogma central"], "pagerank": 1.5339340849584434e-06, "statements": 97, "score": 0.10199154}, {"qnode": "Q5608416", "description": ["Sternwheeler"], "label": ["Greyhound (ship, 1890)"], "alias": ["Pup", "Hound", "Dog"], "pagerank": 6.663586331354574e-09, "statements": 96, "score": 0.092948504}, {"qnode": "Q1211818", "description": ["fictional character in Half-Life"], "label": ["Dog"], "alias": [], "pagerank": 6.444451403437476e-09, "statements": 77, "score": 0.08989185}, {"qnode": "Q98446930", "description": ["U.S. nuclear test"], "label": ["Dog"], "alias": ["26"], "pagerank": 5.9095112210393705e-09, "statements": 24, "score": 0.08243012}, {"qnode": "Q30307328", "description": ["dog in mythology"], "label": ["mythological dog"], "alias": ["legendary dog", "mythical dog"], "pagerank": 7.300556973915422e-07, "statements": 42, "score": 0.07612376}, {"qnode": "Q101128251", "description": [], "label": ["dog"], "alias": [], "pagerank": 5.44224754996459e-09, "statements": 16, "score": 0.07591239}],
    }
  }

  handleOnChange (query) {
    this.setState({ query }, () => {
      if ( !query ) {
        this.setState({results: []})
      } else {
        clearTimeout(this.timeoutID)
        this.timeoutID = setTimeout(() => {
          this.submitQuery()
        }, 500)
      }
    })
  }

  submitQuery() {
    const { query } = this.state

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
        this.setState({ results })
      })
    }
  }

  submit(event) {
    event.preventDefault()
    this.submitQuery()
  }

  renderTitle() {
    const { classes } = this.props
    return (
      <Typography
        component="h3"
        variant="h3"
        className={ classes.header }>
        <a href="https://github.com/usc-isi-i2/kgtk" title="Knowledge Graph Toolkit" rel="noopener noreferrer nofollow" target="_blank">
          <div className={ classes.logo }>
            <Logo/>
          </div>
        </a>
        Knowledge Graph Semantic Similarity
      </Typography>
    )
  }

  renderResults() {
    const { classes } = this.props
    const { results, selected } = this.state
    return results.map((result, i) => (
      <Grid item xs={ 12 } key={ i } className={ classes.result }>
        <Typography
          component="h5"
          variant="h5"
          className={ classes.index }>
          { i + 1 }.
        </Typography>
        <CustomCheckbox
          className={classes.checkbox}
          checked={selected}
          disableRipple={true}
          onChange={() => this.setState({selected: !selected})}
        />
        <Link
          href={`https://ringgaard.com/kb/${result.qnode}`}
          target="_blank"
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

  render() {
    const { classes } = this.props
    return (
      <ThemeProvider theme={ theme }>
        <Container maxWidth="xl">
          <div id="top"/>
          <CssBaseline/>
          {this.renderTitle()}
          <form className={ classes.form } noValidate
            onSubmit={ this.submit.bind(this) }>
            <Grid container spacing={ 3 }>
              <Grid item xs={ 12 }>
                <Paper component="div" className={ classes.paper } square>
                  <Grid container spacing={ 3 }>
                    <Grid item xs={ 12 }>
                      <Input autoFocus={ true } label={'Search'}
                        onChange={ this.handleOnChange.bind(this) }/>
                    </Grid>
                  </Grid>
                </Paper>
                {this.renderResults()}
              </Grid>
            </Grid>
          </form>
          <ArrowUp/>
        </Container>
      </ThemeProvider>
    )
  }
}


export default withStyles(styles)(App)
