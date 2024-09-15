import * as d3 from 'd3'
import * as d3Slider from 'd3-simple-slider'  // 导入d3-simple-slider

const COLORS = {
    ROW_BACKGROUND: "rgba(200, 200, 200, 0.2)",
    ROW_BACKGROUND_ACTIVE: "rgba(200, 200, 200, 0.6)",
    TEXT: "black",
    HEATMAP_DEFAULT: "rgba(130,194,255, 0.4)",
    HEATMAP_ACTIVE: "rgba(130,194,255, 1.0)",
    SLIDER_TRACK: "#BADA55",
    SLIDER_TRACK_INSET: "#BADA55",
    SLIDER_TRACK_OVERLAY: "#E0E0E0",
    SLIDER_HANDLE: "#AC4",
    SLIDER_HANDLE_HOVER: "#8B3",
    SLIDER_HANDLE_ACTIVE: "#6A2"
};

export function getValue(concept, time) {
    console.log("getValue", concept, time)
    let value = -1;
    const start = time;
    const end = time + 30;
    for (let ts of Object.values(concept.timestamp)) {
        if (ts >= start && ts <= end) {
            value = 1
        }
    }
    return value
}


// 添加格式化秒数的函数
function formatSeconds(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}
// function getNode (d, label) {
//     return Object.values(d).find(node => node.label === label)[0];
// }
// function tempLog (n) {
//     console.log("tempLog", n)
//     return true
// }
function getHeatRectColor (tsList, start, end, currentTick) {
    if (isMentionedInTime(tsList, start, end)) {
        if (currentTick >= start && currentTick <= end) {
            return COLORS.HEATMAP_ACTIVE
        } else {
            return COLORS.HEATMAP_DEFAULT
        }
    }
    return "none"
}
function isMentionedInTime (nodeTimeStamps, start, end) {
    for (let ts of Object.values(nodeTimeStamps)) {
        let tv = parseFloat(ts)
        if (tv >= start && tv <= end) {
            return true
        }
    }
    return false
}


export function createChart(containerWidth, refH, initialChartData, duration, initialSliderVal, handleSeekTo, handleConceptHoverEvent) {
    let chartData = initialChartData;
    let videoDuration = duration
    
    const itemHeight = (refH - containerWidth * 9 / 16) / 11
    console.log("itemHeight", itemHeight)
    const margin = {top: itemHeight / 2, right: 0.06 * containerWidth + 15, bottom: 20, left: 0.06 * containerWidth + 15};
    const sliderOffset = 0;
    const contentWidth = containerWidth - margin.left - margin.right - sliderOffset;
    const contentHeight = 7 * itemHeight
    const sliderWidth = contentWidth + sliderOffset
    const sliderHeight = 20
    const containerHeight = margin.top + contentHeight + 2 * margin.bottom + sliderHeight

    const timeIntervals = d3.range(0, videoDuration+1, 30);
    let x = d3.scaleBand()
                .domain(timeIntervals)
                .range([0, contentWidth])
                .padding(0)
    let y = d3.scaleBand()

    const slider = d3Slider.sliderBottom()
        .min(0)
        .max(videoDuration)
        .width(sliderWidth)
        .tickFormat(formatSeconds)
        .ticks(5)
        .displayValue(false)
        .handle(
            d3.symbol()
                .type(d3.symbolCircle)
                .size(200)
        )
        .value(initialSliderVal)
        .on('drag', (val) => {
            handleSeekTo(val)
        });

    let svg = d3.create("svg")
        .attr("width", containerWidth)
        .attr("height", containerHeight);
    let g = svg.append("g")
        .attr("transform", `translate(${margin.left + sliderOffset/2},${0})`);


    function initChart() {
        g.append("g")
            .attr("transform", `translate(${0},${ margin.top + contentHeight +  margin.bottom})`)
            .attr("class", "slider")
            .call(slider);
        
        svg.selectAll('.slider .track, .slider .track-inset, .slider .track-overlay')
            .attr('stroke-width', sliderHeight)
            .attr('stroke-linecap', 'round');

        svg.select('.slider .track')
            .attr('stroke', '#BADA55');  // 移除原始轨道的颜色

        svg.select('.slider .track-inset')
            .attr('stroke', '#BADA55')  // 左侧（已滑过部分）设置为橙色

        svg.select('.slider .track-overlay')
            .attr('stroke', '#E0E0E0')  // 右侧（未滑过部分）设置为浅灰色

        svg.selectAll('.slider .handle')
            .attr('fill', '#AC4')
            .attr('class', 'slider-handle')
            .attr('stroke', '#AC4')
            
        updateChart(0);
    }
    function updateChart(transitionDuration = 350) {
        const concepts = chartData
        console.log("updateChart",JSON.stringify(concepts))
        console.log("updateChart timeIntervals",  timeIntervals)
        const items = Object.values(concepts).map(node => node.label);
    

        console.log("updateChart items",  items)
        const data = d3.cross(Object.entries(concepts), timeIntervals).map(([[, node], time]) => {
            return {
                item: node.label,
                time: time,
                timeStamps: node.timestamp
            };
        });

        console.log("updateChart chartData",JSON.stringify(data))

        x.domain(timeIntervals)
            .range([0, contentWidth])
            .padding(0)

        y.domain(items)
            .range([containerHeight - 2 * margin.bottom - sliderHeight, containerHeight - 2 * margin.bottom - sliderHeight - items.length * itemHeight])
            .padding(0.2);

        const rows = g.selectAll(".row")
            .data(items, d => d)
            .join(
                enter => {
                    const row = enter.append("g")
                        .attr("class", "row")
                        .attr("transform", d => `translate(0, ${y(d)})`);
                    
                    row.append("rect")
                        .attr("class", "row-background")
                        .attr("x", -margin.left)
                        .attr("y", 0)
                        .attr("rx", y.bandwidth() / 2)
                        .attr("ry", y.bandwidth() / 2)
                        .attr("width", contentWidth + margin.left + margin.right)
                        .attr("height", y.bandwidth())
                        .attr("fill", COLORS.ROW_BACKGROUND)
                        .attr("opacity", 0.5);
                    
                    let hoverTimer;

                    row.append("image")
                        .attr("class", "row-icon")
                        .attr("x", -margin.left + 4)
                        .attr("y", y.bandwidth() / 2 - 8)  // 假设图标大小为16x16
                        .attr("width", 16)
                        .attr("height", 16)
                        .attr("href", `/assets/noun-magnifier-1829967.svg`)
                        .style("cursor", "pointer")
                        .on("mouseover", function(event, d) {
                            hoverTimer = setTimeout(() => {
                                handleConceptHoverEvent(d, event, true);
                            }, 1000);
                            console.log("on mouseover", event, d, hoverTimer)
                        })
                        .on("mouseout", function(event,d) {
                            handleConceptHoverEvent(d, event, false)
                        });

                    row.append("text")
                        .attr("class", "row-label")
                        .attr("x", -margin.left + 20)
                        .attr("y", y.bandwidth() / 2)
                        .attr("dy", "0.35em")
                        .text(d => d)
                        .attr("fill", "black")
                        .style("font-size", itemHeight > 20 ? 14 : 10)
                        .style("font-weight", "bold")
                        .style("text-anchor", "start")
                        .style("cursor", "pointer")
                        .on("mouseover", function(event, d) {
                            d3.select(this.parentNode).select(".row-background").attr("fill", COLORS.ROW_BACKGROUND_ACTIVE);
                            console.log("on mouseover", event, d)
                        })
                        .on("mouseout", function(event,d) {
                            d3.select(this.parentNode).select(".row-background").attr("fill", COLORS.ROW_BACKGROUND);
                            console.log("on mouseout", event, d)
                        });
                    
                    return row;
                },

                update => update,
                exit => exit.transition().duration(150)
                .style("opacity", 0)  // 淡出要移除的行
                .remove()
            )
            

        rows.transition().duration(transitionDuration)
        .attr("transform", d => `translate(0, ${y(d)})`)
        .style("opacity", 1);  // 确保所有行都可见

        rows.selectAll("rect.heatmap")
            .data(d => data.filter(item => item.item === d))
            .join(
                enter => enter.append("rect")
                .attr("class", d => `heatmap ${isMentionedInTime(d.timeStamps, d.time, d.time + 30) ? 'interactive' : ''}`)
                    .attr("x", d => x(d.time))
                    .attr("y", 0)
                    .attr("width", x.bandwidth())
                    .attr("height", y.bandwidth())
                    .attr("fill", d => getHeatRectColor(d.timeStamps, d.time, d.time + 30, slider.value())),
                update => update.transition().duration(transitionDuration)
                .attr("class", d => `heatmap ${isMentionedInTime(d.timeStamps, d.time, d.time + 30) ? 'interactive' : ''}`)
                    .attr("x", d => x(d.time))
                    .attr("y", 0)
                    .attr("width", x.bandwidth())
                    .attr("height", y.bandwidth())
                    .attr("interactive", d => isMentionedInTime(d.timeStamps, d.time, d.time + 30))
                    .attr("fill", d => getHeatRectColor(d.timeStamps, d.time, d.time + 30, slider.value())),
            )
            .on("click", function(event, d) {
                if (d3.select(this).classed('interactive')) {
                    handleSeekTo(d.time, d.item);
                }
            });

        
        // rows.selectAll("rect.heatmap").lower();

    
        g.selectAll(".row-background").lower();
        g.selectAll(".row-label").raise();

    }
    function updateData(newChartData) {
        chartData = newChartData;
        updateChart();
    }

    
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .slider-handle {
            transition: fill 0.2s ease;
            outline: none; /* 移除默认的焦点轮廓 */
            cursor: pointer; 
        }
        .slider-handle:hover {
            fill: #8B3 !important;
        }
        .slider-handle:active {
            fill: #6A2 !important;
        }
        /* 移除滑块被按住时的蓝色边框 */
        .slider-handle:focus {
            outline: none;
        }
        .heatmap.interactive:hover {
            fill: ${COLORS.HEATMAP_ACTIVE} !important;
        }
    `;

    // 将样式元素添加到文档头部
    document.head.appendChild(styleElement);

    initChart();
    // 清理函数
    const cleanup = () => {
        console.log("Chart cleanup");
    };

    return {
        node: svg.node(),
        cleanup: cleanup,
        updateSliderPosition:  (time) => {
            console.log("updateSliderPosition", time)
            if (time < 0 || time > videoDuration) {
              return;
            }
            slider.value(time);

            g.selectAll(".row").each(function() {
                d3.select(this).selectAll("rect.heatmap")
                    .attr("fill", d => {
                        return getHeatRectColor(d.timeStamps, d.time, d.time + 30, time)
                    });
            });
        },
        updateData
    };
}