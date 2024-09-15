<template>
    <div class="chart-container" ref="chartContainer">
      <!-- D3图表将在这里渲染 -->
    </div>
  </template>
  
  <script>
    import { createChart } from './createChart'

export default {
    name: 'ConceptTimeTabel',
    props: {
      chartData: {
        type: Object,
        required: true,
        default: () => ({}),
      },
      tick: {
        type: Number,
        default: 0
      }
    },
    mounted() {
        window.addEventListener('resize', this.handleResize)
        this.resizeObserver = new ResizeObserver(this.handleResize);
        if (this.$el.parentElement) {
            this.resizeObserver.observe(this.$el.parentElement);
        }
    },
    data() {
        return {
            chart: null,
            duration: 0,
            sliderVal: 0
        }
    },
    watch: {
        chartData: {
            handler(newValue) {
                console.log("getNewChartData duration", newValue.videoDuration)
                if (newValue) {
                    this.updateChart()
                } 
            },
            deep: true
        },
        tick: {
            handler(newValue) {
                if (newValue) {
                    this.updateSlider(newValue)
                }
            }
        }
    },
    methods: {
        handleResize() {
        const element = this.$refs.chartContainer
        if (element && this.chart) {
            // 重新创建图表
            this.cleanup()
            element.removeChild(this.chart.node)
            this.chart = null
            this.updateChart(true)
        }
        },
        findParent(element) {
            let currentElement = element;
            while (currentElement && currentElement !== document.body) {
                if ( currentElement.className == "videoWithTimeLine") {
                    return currentElement 
                }
                currentElement = currentElement.parentElement;
            }
            return currentElement 
        },
        updateChart(isKeepTime = false) {
            console.log('updateChart----createChart', this.chart, this.duration, this.chartData.videoDuration)
            const element = this.$refs.chartContainer
            if (!element) {
                console.error('Chart container not found')
                return
            }
            const parent = this.findParent(element)
            const width = element.getBoundingClientRect().width
            const height = parent.getBoundingClientRect().height
            if (!this.chart || this.duration != this.chartData.videoDuration) {
                while (element.firstChild) {
                    element.removeChild(element.firstChild)
                }
                this.duration = this.chartData.videoDuration

                let initialSliderVal = 0
                if (isKeepTime && this.sliderVal > 0) {
                    initialSliderVal = this.sliderVal
                } 
                this.chart = createChart(width, height, this.chartData.concepts, this.duration, initialSliderVal, this.handleSeekTo, this.handleConceptHoverEvent)
                this.cleanup = this.chart.cleanup
                element.appendChild(this.chart.node)
            } else {
                this.chart.updateData(this.chartData.concepts)
            }
        },
        handleConceptHoverEvent(label, event, is_hover) {
            this.$emit("hover-concept-label", {label, event, is_hover});
        },
        handleSeekTo(newValue, item=null) {
            this.$emit("event-seekto-time", {'time':newValue, 'concept':item});
            this.sliderVal = newValue
        },
        updateSlider(val) {
            if (!this.chart) {
                return
            }
            this.sliderVal = val
            this.chart.updateSliderPosition(val)
        },
        beforeUnmount() {
            window.removeEventListener('resize', this.handleResize)

            if (this.cleanup) {
                this.cleanup()
            }
            if (this.chart && this.chart.parentNode) {
                this.chart.parentNode.removeChild(this.chart)
            }
        }
    }
}
    </script>

    <style scoped>
    .chart-container {
    width: 100%;
    height: 100%;
    }
    </style>