import { boot } from 'quasar/wrappers'
import axios from 'axios'


// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const context = process.env.CONTEXT

let baseURL;
if (context === 'development') {
  baseURL = "http://127.0.0.1:5030/api";
}
else if (context === 'preprod') {
  baseURL = "https://preprod.predictops.fr/api";
}
else if (context === 'production') {
  baseURL = "https://dashboard.predictops.fr/api"; // Production URL
}

const api = axios.create({ baseURL: baseURL, withCredentials: true })

// if(process.env.NODE_ENV == "development") {
//   const api = axios.create({ baseURL: 'http://127.0.0.1:5025/pompiers/api', withCredentials: true })
// }
// else {
//   const api = axios.create({ baseURL: 'https://dashboard.predictops.fr/pompiers/api', withCredentials: true })
// }


export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
  if (context != 'development') {
    app.config.warnHandler = (msg, instance, trace) => {
    }
  }
})




export { api }

