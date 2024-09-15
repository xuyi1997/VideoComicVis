<template>
  <div class="home-page">
    <!-- <div id="0" class="left-panel"> -->
      <div id="1" class="top-left-panel">
        <ControlPanel 
          :taskList="taskList"
          :importanceAlgorithmsNameList="importanceAlgorithmsNameList"
          :challengeAlgorithmsNameList="challengeAlgorithmsNameList"
          :conceptNumPercent="conceptNumPercent"
          @selected-video-task="handleTask" 
          @selected-importance-alg="handleSelectImportanceAlgCommand"
          @selected-challenge-alg="handleSelectChallengeAlgCommand"
          @update-concept-num-percent="handleSliderConceptNumChange">
          </ControlPanel>
      </div>

      <div id="2" :class="['panel', 'transition-panel', {'bottom-left-panel': mode === 'default'}, {'right-panel': mode !== 'default'}]">
        <ConceptMap  
            :smallMode="mode === 'default'"
            :conceptMapData="taskData.conceptData"
            :numberPercent="conceptMapNodesPercent"
            :cameraNodeID="cameraNodeID"
            @click-concept-map-node="handleConceptMapNodeClick"
            @change-concept-map-full-screen-mode="handleConceptMapFullScreenModeChange"
          />
      </div>

      <div id="3" :class="['panel', 'transition-panel', {'right-panel': mode === 'default'}, {'right-panel-video': mode === 'default'}, {'bottom-left-panel': mode !== 'default'}]">
        <VideoWithTimeLine
              :conceptTimeTableData="conceptTimeTableData"
              :targetTimeStamp="targetTimeStamp"
              :videoUrl="taskData.videoPath"
              @video-tick="updateVideoPlayerTime"
              @seek-event="handleSeekEvent"
              @hover-concept-label="handleConceptHoverEvent"
              @video-player-pause="handleVideoPlayerPause"
          />
      </div>
      <ComicTipView v-if="hoveredConcept !== null" 
      :conceptEvent="hoveredConcept"
      class="comic-tip-overlay"
      />

      <!-- <div id="2" :class="'bottom-left-panel'">
        <ConceptMap  v-if="mode === 'default'"
            :conceptMapData="taskData.conceptData"
            @click-concept-map-node="handleConceptMapNodeClick"
          />
          <VideoWithTimeLine v-else
              :conceptTimeTableData="conceptTimeTableData"
              :targetTimeStamp="targetTimeStamp"
              :videoUrl="taskData.videoPath"
              @video-tick="updateVideoPlayerTime"
              @seek-event="handleSeekEvent"
              @hover-concept-label="handleConceptHoverEvent"
          />
      </div> -->


    <!-- </div>
      <div id="3" :class="['right-panel', {'right-panel-video': mode === 'default'}]">
        <VideoWithTimeLine v-if="mode === 'default'"
              :conceptTimeTableData="conceptTimeTableData"
              :targetTimeStamp="targetTimeStamp"
              :videoUrl="taskData.videoPath"
              @video-tick="updateVideoPlayerTime"
              @seek-event="handleSeekEvent"
              @hover-concept-label="handleConceptHoverEvent"
          />
          <ConceptMap  v-else
            :conceptMapData="taskData.conceptData"
            @click-concept-map-node="handleConceptMapNodeClick"
          />
      </div> -->
    </div>
</template>


<script>
import axios from 'axios'
// import VideoPlay from '@/components/VideoPlay/index.vue'
import ConceptMap from '@/components/ConceptMap/index.vue'
import ControlPanel from '@/components/ControlPanel/index.vue'
// import ConceptTimeLine from '@/components/TimeLine/index.vue'
// import SVGComicView from '@/components/SVGComicView/index.vue'
// import { mapActions } from 'vuex'
import VideoWithTimeLine from '@/components/VideoWithTimeLine/index.vue'
import ComicTipView from '@/components/ComicTipView/index.vue'

// import ConceptsListPanel from '@/components/ConceptListPanel/index.vue'

export default {
  name: 'HomePage',
  components: {
    ControlPanel,
    ComicTipView,
    // ConceptTimeLine,
    // ConceptsListPanel,
    // VideoPlay,
    ConceptMap,
    VideoWithTimeLine
    // SVGComicView
  },
  data() {
    return {
      /*preset*/
      updateTimeInterval: 1.0, //s
      importanceAlgorithms: ['graph', 'tfidf', 'frequency'],
      challengeAlgorithms: ['unfamiliar', 'ambiguity'],
      /*control*/
      mode: 'default',
      taskList: {"default": "value"},
      importanceAlgorithmsNameList: ['Graph centrality', 'TF-IDF', 'Frequency'],
      challengeAlgorithmsNameList: ['Unfamiliarity', 'Ambiguity'],
      selectedImpAlg: 'graph',
      selectedChaAlg: 'unfamiliar',
      conceptNumPercent: 1.0,
      /*real-time*/
      cameraNodeID: "",
      conceptMapNodesPercent: 1.0,
      targetTimeStamp: 0, //seek video 
      videoTick: -1,//record video playback time
      currentTick: -1, //current video playback time
      conceptTimeTableData: {
        concepts: {},
        videoDuration: -1
      }, //update real-time concepts for current time stamp
      hoveredConcept: null,
      /*database from backend*/
      taskData: {
        taskName: "",
        videoPath: "",
        videoDuration: 0,
        conceptData: {
          nodes: {},
          edges: {}
        },
        comicDataBase: {},
        sortImportantConcepts: {},
        
      }
    };
  }, 
  computed: {
  },
  watch: {
    selectedImpAlg() {
      this.updateData(true);
    },
    selectedChaAlg() {
      this.updateData(true);
    }
  },
  mounted() {
    this.fetchTasks()
  },
  methods: {
    handleConceptMapFullScreenModeChange(val) {
      if (val) {
        this.mode = 'conceptMapFull'
      } else {
        this.mode = 'default'
      }
    },
    fetchTasks() {
      const path = 'http://127.0.0.1:5000/api/fetchTasks'
      axios.get(path)
        .then(response => {
          this.taskList = response.data.response
          this.handleTask(Object.keys(this.taskList)[0])
        })
        .catch(error => {
          console.log(error)
        })
    },
    handleTask(taskName) {
      ///@todo: wait sync to query concepts and features
      console.log("[VideoComicVis] handleTask", taskName);
      this.taskData.taskName = taskName;
      if (this.taskList[taskName]) {
        const videoFile = this.taskList[taskName].video_file;
        if (videoFile) {
          console.log("[VideoComicVis] video file", videoFile);
          this.taskData.videoPath = `/assets/task/${taskName}/${videoFile}`;
        } else {
          console.error("[VideoComicVis]File not Exist:", videoFile);
        }
      }
      this.updateData();
    },
    updateCacheFeatures () {
      this.taskData.sortImportantConcepts = Object.values(this.taskData.conceptData.nodes)
        .sort((a, b) => {
          const graphA = parseFloat(a.features.importance_score[this.selectedImpAlg]);
          const graphB = parseFloat(b.features.importance_score[this.selectedImpAlg]);
          return graphB - graphA;  // 降序排列
        })
        .reduce((acc, concept, index) => {
          acc[(index + 1).toString()] = concept
          return acc;
        }, {});
    },
    isMentionedInTime (node, start, end) {
      for (let ts of Object.values(node.timestamp)) {
        if (ts >= start && ts <= end) {
          console.log("[VideoComicVis] realTimeCandidates isMentionedInTime:", node, start, end);
          return true
        }
      }
      return false
    },
    updateRealTimeConcepts () {
      // init: show 5 most important concepts
      var conceptsInTimeTable = {}
      const oldConceptsInTimeTable = this.conceptTimeTableData.concepts
      console.log("oldConceptsInTimeTable:", JSON.stringify(oldConceptsInTimeTable));
      let isNeedUpdate = false

      if (Object.keys(oldConceptsInTimeTable).length === 0) {
        conceptsInTimeTable = Object.values(this.taskData.sortImportantConcepts).slice(0, 5)
        isNeedUpdate = true
      } else {
        conceptsInTimeTable = { ...oldConceptsInTimeTable };
        if (this.videoTick > 0) {
          const node_candidates = Object.fromEntries(
              Object.entries(this.taskData.sortImportantConcepts)
                .slice(0, this.timelineDynamicNodesNum)
            );
          console.log("node_candidates", node_candidates)
          const start = this.videoTick
          const end = start + this.updateTimeInterval
          const realTimeCandidates = Object.fromEntries(
              Object.entries(node_candidates).filter(([, node]) => 
                  this.isMentionedInTime(node, start, end)
              )
          );
          const oldLabels = Object.values(oldConceptsInTimeTable)
            .map(concept => concept.label);
          const nonMatchingConcepts = Object.fromEntries(
              Object.entries(realTimeCandidates).filter(([, node]) => 
                !oldLabels || !oldLabels.includes(node.label)
              )
          );

          const newConcepts = Object.values(nonMatchingConcepts)
          .sort((a, b) => {
            const graphA = parseFloat(a.features.importance_score[this.selectedImpAlg]);
            const graphB = parseFloat(b.features.importance_score[this.selectedImpAlg]);
            return graphB - graphA;  // 降序排列
          })
          .slice(0, 2);
          if (newConcepts.length > 0){

            let conceptsArray = Object.values(conceptsInTimeTable);
      
            const fixedConcepts = conceptsArray.slice(0, 5);
            let dynamicConcepts = conceptsArray.slice(5);
            const totalConceptsAfterAdd = fixedConcepts.length + dynamicConcepts.length + newConcepts.length;

            if (totalConceptsAfterAdd > 7) {
              // 如果总数超过7,移除多余的旧概念
              const numToRemove = totalConceptsAfterAdd - 7;
              dynamicConcepts.splice(0, numToRemove);
            }
  
            dynamicConcepts = [...dynamicConcepts, ...newConcepts];
            conceptsArray = [...fixedConcepts, ...dynamicConcepts];
            conceptsInTimeTable = conceptsArray.reduce((acc, concept, index) => {
              acc[(index + 1).toString()] = concept;
              return acc;
            }, {});
            isNeedUpdate = true
            console.log("[VideoComicVis] newConcepts:", newConcepts);
          }

        }
      }
      if (isNeedUpdate) {
        this.$set(this.conceptTimeTableData, 'concepts', conceptsInTimeTable);
        this.$set(this.conceptTimeTableData, 'videoDuration', this.taskData.videoDuration);
        console.log("[VideoComicVis] updateRealTimeConcepts old:", oldConceptsInTimeTable, "new", conceptsInTimeTable);
      }
    },
    updateData (isInTask = false) {
      if (!this.taskData.taskName) {
        console.error('No task selected')
        return
      }
      console.log("[VideoComicVis] updateData", this.taskData.taskName);
      this.clearData(isInTask)
      const formData = new FormData()
      formData.append('task_name', this.taskData.taskName)
      formData.append('imp_alg', this.selectedImpAlg)
      formData.append('cha_alg', this.selectedChaAlg)
      const path = 'http://127.0.0.1:5000/api/prepareConcpetMapAndFeatures'
      axios.post(path, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(response => {
        const network_nodes = response.data.network_nodes
        const network_edges = response.data.network_edges
        this.taskData.videoDuration = response.data.video_duration
        this.taskData.comicDataBase = response.data.comic_path_dict

        this.$set(this.taskData, 'conceptData', {
          nodes: network_nodes,
          edges: network_edges
        });

        console.log("[VideoComicVis] getData", this.taskData);
        this.updateCacheFeatures();
        this.updateRealTimeConcepts();
        let allNodesNum = Object.values(this.taskData.conceptData.nodes).length
        this.timelineDynamicNodesNum = Math.round(allNodesNum * 0.5)
      })
      .catch(error => {
        console.error('Error uploading video:', error)
      })
    },
    clearData(isInTask = false) {
      console.log("[VideoComicVis] clear data")
      this.$set(this.taskData, 'conceptData', {
        nodes: {},
        edges: {}
      });
      this.$set(this.taskData, 'comicDataBase', {});
      let dur = isInTask? this.conceptTimeTableData.videoDuration : -1
      
      this.conceptTimeTableData = {
        concepts: {},
        videoDuration: dur
      };
      this.currentTick = -1;
    },
    handleConceptHoverEvent(val) {
      let event = val.event
      let label = val.label
      let isHover = val.is_hover
      console.log("handleConceptHoverEvent", event, label, isHover)
      if (!isHover) {
        this.showComicTip = false
        this.hoveredConcept = null
        return
      }
      // {label, event, is_hover}
      if (!this.hoveredConcept || this.hoveredConcept.label != label) {
        let findConcept = Object.values(this.taskData.conceptData.nodes).find(node => node.label === label) || null;
        let comicDict = this.taskData.comicDataBase[label];
        this.hoveredConcept = {'concept': findConcept, 'event': event, 'comicDict': comicDict}
        console.log("handleConceptHoverEvent", this.hoveredConcept)
      }
    },
    handleSeekEvent(val) {
      this.videoTick = val.time
      this.updateRealTimeConcepts()
      if (val.concept) {
        console.log("handleSeekEvent click concept", val.concept)
        let nodeId = this.getNodeId(val.concept)
        if (parseFloat(nodeId) > 0) {
          this.cameraNodeID = nodeId
        }
      }
    },
    handleVideoPlayerPause(time) {
      console.log("handleVideoPlayerPause", this.conceptTimeTableData, time)
    },
    updateVideoPlayerTime(time) {
      this.currentTick = time; // 更新当前时间
      if (time - this.videoTick < this.updateTimeInterval) {
        return;
      }
      this.videoTick = time
      console.log("[VideoComicVis] updateVideoPlayerTime: ", time);
      this.updateRealTimeConcepts()
    },
    handleConceptMapNodeClick(node) {
      console.log("[VideoComicVis] handleConceptMapNodeClick: ", node);
    },
    handleSliderConceptNumChange(newValue) {
      let allNodesNum = Object.values(this.taskData.conceptData.nodes).length
      console.log("[VideoComicVis] handleSliderConceptNumChange", newValue, allNodesNum);
      this.conceptMapNodesPercent = newValue * 0.01
      this.timelineDynamicNodesNum = allNodesNum * 0.5 * newValue * 0.01
    },
    handleSelectImportanceAlgCommand(newValue) {
      console.log("[VideoComicVis] handleSelectImportanceAlgCommand", newValue);
      let index = this.importanceAlgorithmsNameList.indexOf(newValue);
      this.selectedImpAlg = this.importanceAlgorithms[index]
    },
    handleSelectChallengeAlgCommand(newValue) {
      console.log("[VideoComicVis] handleSelectChallengeAlgCommand", newValue);
      let index = this.challengeAlgorithmsNameList.indexOf(newValue);
      this.selectedChaAlg = this.challengeAlgorithms[index]
    },
    seekVideo(time) {
        console.log("[VideoComicVis] video play seek to: ", time);
        this.videoTick = parseFloat(time);
    },
    getNodeObj(key) {
      return this.taskData.conceptData.nodes[key]
    },
    getNodeId(label) {
      for (const [, node] of Object.entries(this.taskData.conceptData.nodes)) {
        if (node.label === label) {
          return node.id;
        }
      }
      return -1;
    },

  }
}
</script>

<style>
@import './index.css';
</style>
