<template>
    <div class="control-panel">
      <div class="panel-head">Contol Panel</div>
      
      <div class="panel-row">
        <span class="item-label">Select Video</span>

        <el-dropdown @command="handleSelectCourseCommand">
            <span class="el-dropdown-link">
            {{ selectedVideoTask || 'Select a course' }}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template v-slot:dropdown>
            <el-dropdown-menu>
                <el-dropdown-item v-for="item in videoTasks" :key="item" :command="item">{{ item }}</el-dropdown-item>
            </el-dropdown-menu>
            </template>
        </el-dropdown>
      </div>
  
      <div class="panel-row">
        <span class="item-label">Importance Criteria</span>
        <el-dropdown @command="handleSelectImportanceAlgCommand">
            <span class="el-dropdown-link">
            {{ selectedImpAlg }}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template v-slot:dropdown>
            <el-dropdown-menu>
                <el-dropdown-item v-for="item in importanceAlgorithmsNameList" :key="item" :command="item">{{ item }}</el-dropdown-item>
            </el-dropdown-menu>
            </template>
        </el-dropdown>
      </div>
  
      <div class="panel-row">
        <span class="item-label">Challenge Criteria</span>
        <el-dropdown @command="handleSelectChallengeAlgCommand">
            <span class="el-dropdown-link">
            {{ selectedChaAlg }}<i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <template v-slot:dropdown>
            <el-dropdown-menu>
                <el-dropdown-item v-for="item in challengeAlgorithmsNameList" :key="item" :command="item">{{ item }}</el-dropdown-item>
            </el-dropdown-menu>
            </template>
        </el-dropdown>
      </div>
  
      <div class="panel-row">
        <span class="item-label">Concept Number</span>
        <el-slider
          v-model="sliderConceptNumPercent"
          @input="handleSliderConceptNumChange"
          :min="1"
          :max="100"
          :show-tooltip="false"
          class="custom-slider">
        </el-slider>
      </div>
    </div>
  </template>
  

  <script>
  export default {
    name: 'ControlPanel',
    props: {taskList: {
        type: Object,
        default: () => ({}), // 默认值为空对象
    }, importanceAlgorithmsNameList:{
        type: Array,
        default: () => [],
    },
    challengeAlgorithmsNameList:{
        type: Array,
        default: () => [],
    },
    conceptNumPercent:{
        type: Number,
        default: 1.0,
    },
},
    data() {
        return {
            selectedImpAlg: this.importanceAlgorithmsNameList[0],
            selectedChaAlg: this.challengeAlgorithmsNameList[0],
            sliderConceptNumPercent: this.conceptNumPercent * 100,
            selectedVideoTask: '  '
        };
    },
    watch: {
        taskList: {
            handler(newList) {
                const keys = Object.keys(newList);
                if (keys.length > 0) {
                    this.selectedVideoTask = keys[0]; // Set to the first value in taskList
                } else {
                    this.selectedVideoTask = ''; // Clear if the list is empty
                }
            },
            immediate: true, // Run immediately on component creation
        }
    },
    methods: {
        handleSelectCourseCommand(command) {
            this.selectedVideoTask = command
            console.log("[VideoComicVis] emitSelectedVideoTask", this.selectedVideoTask)
            this.$emit('selected-video-task', this.selectedVideoTask);
        },
        handleSelectImportanceAlgCommand(command) {
            this.selectedImpAlg = command
            this.$emit('selected-importance-alg', this.selectedImpAlg);
        },
        handleSelectChallengeAlgCommand(command) {
            this.selectedChaAlg = command
            this.$emit('selected-challenge-alg', this.selectedChaAlg);
        },
        handleSliderConceptNumChange(newValue) {
            this.sliderConceptNumPercent = newValue
            this.$emit('update-concept-num-percent', newValue);
        }
    },
    created() {
    },
    computed: {
        videoTasks() {
            return Object.keys(this.taskList);
        }
    },
  } 
  </script>


  
<style>
@import './index.css';
</style>
