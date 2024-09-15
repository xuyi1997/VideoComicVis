<template>
    <div class="m-timeline-wrap">
      <div class="m-time-dot">
        <div
          :class="['m-dot-box', {'active': isActive(item)}]"
          v-for="(item, index) in timelineData"
          :key="index"
          @mouseenter="hoveredIndex = index"
          @mouseleave="handleMouseLeave(index)">
          <div class="m-dot" @click="onClickTimeLine(item)">
          </div>
          <div class="concept-container" v-if="isActive(item) || hoveredIndex === index || item.showConcepts">
            <div v-for="(concept, conceptIndex) in item.concepts" :key="conceptIndex" :class="[
            'concept-timeline-button',
            { 'important': concept['is_important'] == 'True', 'challenging': concept['is_important'] == 'False' && concept['is_challenging'] == 'True' }
            ]" 
            @click="onConceptClick(concept, $event, index)">
              {{ concept.label }}
            </div>
          </div>
        </div>
      </div>
      <div class="concept-menu" v-if="showMenu">
        <ConceptMenu 
          :position="menuPosition" 
          :concept="selectedConcept"
          :isShowSeekButton=false
          :time="selectedConcept"
          @seek="onSeek"
          @show-comic="onShowComic"
          @close="closeMenu" />
      </div>
    </div>
  </template>
  
  <script>
  import ConceptMenu from '../ConceptMenu/index.vue'
  
  export default {
    name: 'ConceptTimeLine',
    components: {
      ConceptMenu
    },
    props: {
      interval: {
        type: Number,
        default: 60
      },
      timelineData: {
        type: Array,
        required: true,
        default: () => []
      },
      currentVideoTime: {
        type: Number,
        default: 0
      }
    },
    data() {
      return {
        hoveredIndex: null,
        showMenu: false,
        menuPosition: { x: 0, y: 0 },
        selectedConcept: null,
        menuStyle: {},
        activeConceptIndex: null
      }
    },
    mounted() {
        window.addEventListener('click', this.handleGlobalClick);
    },
    beforeUnmount() {  // 将 beforeDestroy 改为 beforeUnmount
        window.removeEventListener('click', this.handleGlobalClick);
    },
    methods: { 
      onConceptClick(concept, event, index) {
        event.stopPropagation();
        
        this.selectedConcept = concept;
        this.menuPosition = {
          x: event.clientX,
          y: event.clientY
        };
        console.log("[TimeLine] onConceptClick", concept, this.menuPosition);
        this.menuStyle = {
          position: 'fixed',
          left: `${this.menuPosition.x}px`,
          top: `${this.menuPosition.y}px`,
          zIndex: 1000
        }
        this.showMenu = true;
        this.activeConceptIndex = index;
        this.$set(this.timelineData[index], 'showConcepts', true);
      },
      handleMouseLeave(index) {
        this.hoveredIndex = null;
        if (this.activeConceptIndex !== index) {
          this.hoveredIndex = null;
          this.$set(this.timelineData[index], 'showConcepts', false);
        }
      },
      closeMenu() {
        this.showMenu = false;
        this.resetActiveConcept();
      },
      resetActiveConcept() {
        if (this.activeConceptIndex !== null) {
          this.$set(this.timelineData[this.activeConceptIndex], 'showConcepts', false);
          this.activeConceptIndex = null;
        }
      },
      handleGlobalClick(event) {
        if (!this.$el.contains(event.target)) {
          this.closeMenu();
          this.resetActiveConcept();
        }
      },
      onShowComic(concept) {
        console.log("[TimeLine] onShowComic", concept);
        this.$emit('click-concept-show-comic', concept);
        this.closeMenu();
      },
      onSeek(concept) {
        this.$emit('click-concept-seek-video', concept);
        this.closeMenu();
      },
      isActive(item) {
        if (item.time <= this.currentVideoTime && item.time + this.interval > this.currentVideoTime)
          return true;
        return false;
      },
      onClickTimeLine(item) {
        this.$emit('click-time-line', item.time);
      }
    }
  }
  </script>
  
  <style>@import './index.css';</style>