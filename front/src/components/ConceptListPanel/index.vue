<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable no-unused-vars -->

<template>
    <div class="conceptListPanel" style="width:100%;">
        <div class="panelHead">{{ panelHead }}</div>
        <div class='conceptButton' v-for="(value, index) in keywords" :key="index"
        :class="{ 'highlight': hightlightConcepts.includes(value) }" 
        @click="handleConceptClick(value)">
            {{ value }}
            <span class="close-icon" @click.stop="handleConceptDeleteClick(value)">
                <i class="fa fa-times"></i> 
            </span>
        </div>
    </div>
  </template>
    
  <script>

  export default {
    name: 'ConceptListPanel',
    props: {panelHead: {
        type: String,
        required: true,
        default: null
    },
    conceptList: {
        type: Object,
        default: () => ({}), // 默认值为空对象
    },
    hightlightConcepts: {
        type: Array,
        default: () => ([]), // 默认值为空对象
    }},
    data() {
        return {
            selectedConcept: ""
        };
    },
    watch: {
    },
    methods: {
        handleConceptClick(value) {
            this.$emit('click-concept-list-item', value);
        },
        handleConceptDeleteClick(value) {
            this.$emit('click-concept-list-delete-item', value);
        }
    },
    created() {
    },
    computed: {
        keywords() {
            var l = Object.values(this.conceptList)
            return l;
        }
    },
  } 
  </script>
  
  <style>@import './index.css';</style>