<template>
    <div>
      <div class="concept-menu-overlay" @click="$emit('close')"></div>
      <div class="concept-menu" :style="menuStyle">
        <el-row>
          <el-col>
            <el-row>    
              <button class="concept-menu-btn" @click="$emit('show-comic', concept)">Show Comic</button>
            </el-row>

            <el-row>    
              <button v-if="isShowSeekButton" class="concept-menu-btn" @click="$emit('seek', concept)">Seek Video</button>
            </el-row>
          </el-col>
        </el-row>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ConceptMenu',
    props: {
      position: {
        type: Object,
        required: true
      },
      concept: {
        type: Object,
        required: true
      },
      isShowSeekButton: {
        type: Boolean,
        required: true
      }
    },
    computed: {
      menuStyle() {
      return {
        position: 'fixed',
        left: `${this.position.x}px`,
        bottom: `${window.innerHeight - this.position.y}px`,
        zIndex: 1000
      }
    }
    }
  }
  </script>
  <style scoped>
  .concept-menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 999;
  }
  .concept-menu {
    position: fixed;
    z-index: 1000;
    height: fit-content;
    background-color: white;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    margin-bottom: 2px;
    margin-top: 2px;
  }
  .el-row {
    margin-bottom: 0px;
    margin-top: 2px;
}
  .concept-menu-btn {
    height: 30px;
    height: fit-content;
    display: block;
    background-color: transparent;
    color: #333;
    border: none;
    text-align: left;
    cursor: pointer;
    transition: background-color 0.2s ease;
    font-size: 12px;
  }
  
  .concept-menu-btn:hover {
    background-color: lightblue;
  }
  
  .el-row:not(:last-child) {
    border-bottom: 1px solid #e0e0e0;
  }
  

  </style>