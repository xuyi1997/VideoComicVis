<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable no-unused-vars -->
<template>
  <div class="m-video" :style="`width: 100%;aspect-ratio: 16 / 9;`">
    <video
      id="playVideo"
      ref="veo"
      :style="`object-fit: cover; width: 100%; height: 100%, aspect-ratio: 16 / 9;`"
      :src="videoUrl"
      :poster="videoCover"
      :autoplay="autoplay"
      :controls="!originPlay&&controls"
      :loop="loop"
      :muted="autoplay || muted"
      :preload="preload"
      @click.prevent.once="onPlay">
    </video>
  </div>
</template>
<script>
export default {
  name: 'VideoPlay',
  props: {
    seekTarget:{
      type: Number,
      default: 0
    },
    width: { // 视频播放器宽度
      type: Number,
      default: 800
    },
    height: { // 视频播放器高度
      type: Number,
      default: 650
    },
    videoUrl: { // 视频文件url，必传，支持网络地址 https 和相对地址 require('@/assets/files/Bao.mp4')
      type: String,
      required: true,
      default: null
    },
    videoCover: { // 视频封面url，支持网络地址 https 和相对地址 require('@/assets/images/Bao.jpg')
      type: String,
      default: null
    },
    autoplay: { // 视频就绪后是否马上播放
      type: Boolean,
      default: false
    },
    controls: { // 是否向用户显示控件，比如进度条，全屏
      type: Boolean,
      default: true
    },
    loop: { // 视频播放完成后，是否循环播放
      type: Boolean,
      default: false,
    },
    muted: { // 是否静音
      type: Boolean,
      default: false
    },
    preload: { // 是否在页面加载后载入视频，如果设置了autoplay属性，则preload将被忽略；
      type: String,
      default: 'auto' // auto:一旦页面加载，则开始加载视频; metadata:当页面加载后仅加载视频的元数据 none:页面加载后不应加载视频
    },
    showPlay: { // 播放暂停时是否显示播放器中间的暂停图标
      type: Boolean,
      default: true
    },
    playWidth: { // 中间播放暂停按钮的边长
      type: Number,
      default: 96
    },
    zoom: { // video的poster默认图片和视频内容缩放规则
      type: String,
      default: 'cover' // none:(默认)保存原有内容，不进行缩放; fill:不保持原有比例，内容拉伸填充整个内容容器; contain:保存原有比例，内容以包含方式缩放; cover:保存原有比例，内容以覆盖方式缩放
    }
  },
  data () {
    return {
      originPlay: true,
      vplay: false
    }
  },
  mounted () {
    if (this.showPlay) {
      this.$refs.veo.addEventListener('pause', this.onPause)
      this.$refs.veo.addEventListener('playing', this.onPlaying);
      this.$refs.veo.addEventListener('timeupdate', this.timeupdate)
    }
    if (this.autoplay) {
      this.vplay = true
      this.originPlay = false
    }
  },
  watch:{
    videoUrl(newUrl) {
      console.log("[VideoPlay] videoUrl changed to:", newUrl);
    },
    seekTarget(val) {
        console.log("video player seek to ", val)
        this.$refs.veo.currentTime = val;
    }
  },
  methods: {
    onPlay () {
      if (!this.autoplay) {
        this.vplay = true
        this.originPlay = false
        this.$refs.veo.play()
      } else {
        this.$refs.veo.pause()
      }
    },
    onClickPause () {
      if (this.$refs.veo.paused) {
        this.$emit("video-player-pause", this.$refs.veo.currentTime);
      }
    },
    onPause () {
      this.vplay = false
    },
    onPlaying () {
      this.vplay = true
    },
    timeupdate(){
      let time = this.$refs.veo.currentTime
      console.log("emit video-player-time-update", time)
      this.$emit("video-player-time-update", time);
    }
  }
}
</script>
<style>
.m-video {
  position: relative;
  cursor: pointer;
  width: 100%; /* 让宽度自适应 */
  max-width: 100%; /* 确保最大宽度为 100% */
  }
  .u-play {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    margin: auto;
    fill: none;
    color: #FFF;
    pointer-events: none;
    opacity: 0.7;
    transition: opacity .3s;
  }
  .u-play {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    margin: auto;
    fill: none;
    color: #FFF;
    pointer-events: none;
    opacity: 0.7;
    transition: opacity .3s;
  }

.el-row {
  margin-bottom: 20px;
}
.el-row:last-child {
  margin-bottom: 0;
}
.el-col {
  border-radius: 4px;
}

.grid-content {
  border-radius: 4px;
  min-height: 36px;
}


.m-video {
  position: relative;
  cursor: pointer;
  width: 100%;
  max-width: 100%;
  border-radius: 15px; /* 设置圆角 */
  overflow: hidden; /* 确保内容不会超出圆角 */
}

video {
  border-radius: 15px; /* 为视频元素也设置圆角 */
}
</style>
