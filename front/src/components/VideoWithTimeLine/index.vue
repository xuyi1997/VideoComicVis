<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable no-unused-vars -->

<template>
    <div class="videoWithTimeLine">
        <el-row>
        <el-col>
        <el-row>
            <div id="videoPlay" class="panel-up">
            <VideoPlay
                :seekTarget="seekTarget"
                :videoUrl="videoUrl"
                @video-player-time-update="videoPlayerTick"
                @video-player-pause="videoPlayerPause"
                />
            </div>
        </el-row>
        <el-row>
            <div id="timeLine" class="panel-down">
                <ConceptTimeTabel
                :chartData="chartData"
                :tick="tick"
                @event-seekto-time="seekTo"
                @hover-concept-label="handleConceptHoverEvent"/>
            </div>
        </el-row>
        </el-col>
        </el-row>
    </div>
  </template>


<script>
import VideoPlay from '@/components/VideoPlay/index.vue'
import ConceptTimeTabel from '@/components/ConceptTimeTabel/index.vue'

export default {
  name: 'VideoWithTimeLine',
  components: {
    VideoPlay,
    ConceptTimeTabel
  },
  props: {
    conceptTimeTableData: {
        type: Object,
        default: null
    },
    targetTimeStamp:{
      type: Number,
      default: 0
    },
    videoUrl: { // 视频文件url，必传，支持网络地址 https 和相对地址 require('@/assets/files/Bao.mp4')
      type: String,
      required: true,
      default: null
    },
    },
  data() {
    return {
        chartData: {},
        tick:0.0,
        seekTarget:-1
    }
  },
  watch: {
    conceptTimeTableData: {
            handler(newData) {
                console.log("conceptTimeTableData update", newData)
                this.chartData = newData;
            },
            immediate: true, // Run immediately on component creation
    },
    targetTimeStamp: {
            handler(newVal) {
                if (newVal >= 0) {
                    this.seekTarget = newVal
                }
            }
        }
    },
  methods: {
    videoPlayerTick(time) {
        if (time) {
            this.$emit("video-tick", time);
            this.tick = time
        }
    },
    seekTo(val) {
        console.log("seek-event", val)
        this.seekTarget = val.time
        this.$emit("seek-event", val);
    },
    videoPlayerPause(val) {
        this.$emit("video-player-pause", val);
    },
    handleConceptHoverEvent(val) {
        this.$emit("hover-concept-label", val);
        
    }
  }
}
</script>

  
<style>@import './index.css';</style>