<template>
    <div class="chart-container" ref="chartContainer">
      <!-- D3图表将在这里渲染 -->
    </div>
  </template>
  
  <script>
    import { createChart } from './createChart'

    export default {
    name: 'ChartView',
    props: {
      chartData: {
        type: Object,
        required: true
      }
    },
    data() {
        return {
        chart: null
        }
    },
    watch: {
      chartData: {
        handler() {
          this.initChart()
        },
        deep: true
      }
    },
    methods: {
    initChart() {
            const element = this.$refs.chartContainer
            const width = element.clientWidth
            const { node, cleanup } = createChart(width, this.charData)
            // const { node, cleanup } = createFlow(response.data)
            this.chart = node
            this.cleanup = cleanup
            element.appendChild(this.chart)
        }
    },
    beforeUnmount() {
        if (this.cleanup) {
        this.cleanup()
        }
        if (this.chart && this.chart.parentNode) {
        this.chart.parentNode.removeChild(this.chart)
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