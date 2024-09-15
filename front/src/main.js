import Vue from 'vue'
import App from './App'
import router from './router'
import Element from 'element-ui'
import VueSlider from 'vue-slider-component' 
import 'element-ui/lib/theme-chalk/index.css';
import 'font-awesome/css/font-awesome.min.css';
import 'vue-slider-component/theme/default.css'

import axios from "axios";
import store from './store' 

axios.defaults.headers.post['Content-Type'] = 'application/json';
Vue.prototype.$axios = axios;
Vue.config.productionTip = false
Vue.use(Element)
Vue.component('VueSlider', VueSlider)
/* eslint-disable no-new */
new Vue({
  render: h => h(App),
  router,
  store, 
  beforeCreate(){
    Vue.prototype.$bus = this;
  }
}).$mount('#app')