import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    conceptFeature: null
  },
  mutations: {
    setConceptFeature(state, data) {
      state.conceptFeature = data
    }
  },
  actions: {
    updateConceptFeature({ commit }, data) {
        console.log("updateConceptFeature", data)
      commit('setConceptFeature', data)
    }
  },
  getters: {
    getConceptFeature: state => state.conceptFeature
  }
})