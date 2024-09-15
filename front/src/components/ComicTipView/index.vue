<template>
    <div class="comic-container" ref="comicContainer">
      <!-- D3图表将在这里渲染 -->
    </div>
</template>


<script>
import * as d3 from 'd3';

export default {
name: 'ComicTipView',
props: {
    conceptEvent: {
        type: Object,
        required: true,
        default: () => ({}),
    }
},
  mounted() {
    this.createFloatingWindow();
  },
data() {
    return {
    }
},
watch: {
},
methods: {
    createFloatingWindow() {
        if (!this.conceptEvent) {
            return
        }
        
        let concept = this.conceptEvent['concept']
        let event = this.conceptEvent['event']
        let comicDict = this.conceptEvent['comicDict']
        if (!concept || !event ||!comicDict || (!comicDict['diagram'] && !comicDict['dialogues'])) {
            console.log("Can not find Comic", concept, event, comicDict)
            return
        }

        const container = this.$refs.comicContainer
        const containerRect = container.getBoundingClientRect()

        let x = event.clientX
        let y = event.clientY

        console.log("createFloatingWindow", concept, event, container, containerRect, x, y, comicDict)

        const initialWidth = 400;
        const initialHeight = 400;
        
        let svg = d3.create("svg")
            .attr("width", containerRect.width)
            .attr("height", containerRect.height)
            .style('position', 'absolute')
            .style('top', '0')
            .style('left', '0')
            .style('opacity', '0');

        let startPointX = x - initialWidth
        let startPointY = y - 60 - initialHeight
        let g = svg.append("g")
            .attr("transform", `translate(${startPointX},${startPointY})`);

        let rect = g.append('rect')
            .attr('width', initialWidth)
            .attr('height', initialHeight)
            .attr('rx', 10)
            .attr('ry', 10)

        let comic = comicDict['dialogues']['0']
        if (comic) {
            
            const fo = g.append('foreignObject')
                .attr('width', initialWidth)
                .attr('height', initialHeight);

            const comicObj = fo.append('xhtml:div')
                .style('width', '100%')
                .style('height', '100%')
                .style('display', 'flex')
                .style('align-items', 'center')
                .style('justify-content', 'center')
                .append('xhtml:object')
                .attr('data', comic)
                .attr('type', 'image/svg+xml')
                .attr('class', 'svg-object')
                .style('max-width', '100%')
                .style('max-height', '100%')
                .style('object-fit', 'contain');

            comicObj.on('load', function() {
                const svgDoc = this.contentDocument;
                if (svgDoc) {
                    console.log("svgDoc", svgDoc)
                    const svgElement = svgDoc.documentElement;
                    const svgWidth = svgElement.width.baseVal.value;
                    const svgHeight = svgElement.height.baseVal.value;
                    const aspectRatio = svgWidth / svgHeight;
                    let newWidth, newHeight;
                    if (svgWidth < svgHeight) {
                        newWidth = initialWidth;
                        newHeight = initialWidth / aspectRatio;
                    } else {
                        newHeight = initialHeight;
                        newWidth = newHeight * aspectRatio;
                    }
        
                    // 根据SVG尺寸调整父图层
                    fo.attr('width', newWidth)
                      .attr('height', newHeight);
                    
                    rect.attr('width', newWidth)
                        .attr('height', newHeight)
                        .attr('fill', 'rgba(234, 224, 200, 0.8)');
                    svg.style('opacity', '0.8');
                    
                    // 调整g元素的位置，确保图像不会超出容器
                    // const newX = Math.max(0, Math.min(startPointX, containerRect.width - svgWidth));
                    // const newY = Math.max(0, Math.min(startPointY, containerRect.height - svgHeight));
                    // g.attr('transform', `translate(${newX},${newY})`);
                }
            });
        }

        container.appendChild(svg.node())
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