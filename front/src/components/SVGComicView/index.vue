<template>
    <div class="svg-comic-view">
      <object :data="currentSvgUrl" type="image/svg+xml" class="svg-object">
      </object>
      <div class="navigation-buttons">
        <button @click="previousPage" class="nav-button">&lt;</button>
        <button @click="nextPage" class="nav-button">&gt;</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'SVGComicView',
    props: {
      comicPath: {
        type: Object,
        required: true
      }
    },
    data() {
      return {
        currentIndex: 0
      }
    },
    methods: {
      previousPage() {
        this.currentIndex = (this.currentIndex - 1 + this.svgList.length) % this.svgList.length
      },
      nextPage() {
        this.currentIndex = (this.currentIndex + 1) % this.svgList.length
      },
      resetIndex() {
        this.currentIndex = 0
      }
    },
    computed: {
      svgList() {
        const list = []
        if (this.comicPath.diagram_comic) {
          list.push(this.comicPath.diagram_comic)
        }
        if (this.comicPath.dialogue_comic) {
            list.push(...Object.values(this.comicPath.dialogue_comic))
        }
        return list
      },
      currentSvgUrl() {
        return this.svgList[this.currentIndex] || ''
      }
    },
    watch: {
      comicPath: {
        handler() {
          this.resetIndex()
        },
        deep: true
      }
    }
  }
  </script>
  
  <style scoped>

.navigation-buttons {
  position: absolute;
  bottom: 10px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.nav-button {
  background-color: rgba(255, 255, 255, 0.7);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-button:hover {
  background-color: rgba(255, 255, 255, 0.9);
}
  .svg-comic-view {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .svg-object {
    max-width: 100%;
    max-height: 100%;
  }
  </style>