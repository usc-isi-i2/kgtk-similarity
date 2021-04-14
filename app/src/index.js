import React from 'react'
import ReactDOM from 'react-dom'
import App from './App'
import reportWebVitals from './reportWebVitals'


ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
)


const sendToGoogleAnalytics = ({name, delta, value, id}) => {
  // Assumes the global `gtag()` function exists, see:
  // https://developers.google.com/analytics/devguides/collection/ga4
  window.gtag('event', name, {
    // Use the metric delta as the event's value parameter.
    value: delta,
    // Everything below is a custom event parameter.
    web_vitals_metric_id: id, // Needed to aggregate events.
    web_vitals_metric_value: value, // Optional
    // Any additional params or metadata (e.g. debug information) can be
    // set here as well, within the following limitations:
    // https://support.google.com/analytics/answer/9267744
  })
}


reportWebVitals(sendToGoogleAnalytics)
