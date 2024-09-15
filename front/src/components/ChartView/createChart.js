import * as d3 from 'd3'

import { sankey, sankeyLinkHorizontal } from 'd3-sankey';


export function createFlow(network_data) {
    let edges_dict = network_data.node_data.network_edges
    let nodes_dict = network_data.node_data.network_nodes
    console.log("createFlow", nodes_dict, edges_dict)
    const video_duration = network_data.node_data.video_duration
    console.log("createFlow video_duration", video_duration)

    const important_concepts = getImportantConcepts(nodes_dict).important_concepts
    const max_imp_value = getImportantConcepts(nodes_dict).max_imp_value

    const challenging_concepts = getChallengingConcepts(nodes_dict).challenging_concepts
    const max_clg_value = getChallengingConcepts(nodes_dict).max_clg_value

    console.log("createFlow important_concepts", important_concepts)

    const colorImportantScale = d3.scaleSequential()
        .domain([0, max_imp_value])
        .interpolator(d3.interpolateRgb("#FFF5E6", "#FF9E4A"));  
    
    const colorChallengingScale = d3.scaleSequential()
        .domain([max_clg_value, 0])  
        .interpolator(d3.interpolateRgb("#F3E5F5", "#AD8BC9"));  

    const y_concepts = Object.fromEntries(
        [...new Set([...Object.entries(important_concepts), ...Object.entries(challenging_concepts)])]
    );


    console.log("createFlow important_concepts challenging_concepts", important_concepts, challenging_concepts)
    const graph_nodes = Object.fromEntries(
        Object.entries(y_concepts).map(([, concept]) => [
            concept.id,
            {
                id: concept.id,
                name: concept.label,
                timestamp: concept.timestamp[0],
                vis: getVisFeature(concept)
            }
        ])
    );

    console.log("createFlow graph_nodes", graph_nodes)
    // 创建链接数组，并筛选只保留源节点和目标节点都存在的链接

    const graph_links = Object.values(
        Object.values(edges_dict).reduce((acc, edge) => {
            let start_node = graph_nodes[edge.from]
            let end_node = graph_nodes[edge.to]
            if (!start_node || ! end_node) {
                return acc;
            }
            if (parseFloat(end_node.timestamp) - parseFloat(start_node.timestamp) < 5) {
                return acc
            }
            if (edge.from === edge.to) {
                return acc;
            }
            if (!acc[edge.to] || acc[edge.to].start_node.timestamp < start_node.timestamp) {
                acc[edge.to] = {'start_node': start_node, 'end_node': end_node, 'title': edge.title};
            } 
            return acc;
        }, {})
    );

    console.log("createFlow graph_nodes", graph_nodes)
    console.log("createFlow graph_links", graph_links)

    const exampleGraph = {
        nodes: Object.values(graph_nodes).map(node => (
        {
            name: node.name,
            id: node.id,
            color: getFill(node.vis.type, node.vis.value, colorImportantScale, colorChallengingScale)
        })),
        links: graph_links.map(link => ({
            source: link.start_node.id,
            target: link.end_node.id,
            title: link.title,
            value: 1  
        }))
    };
    console.log("createFlow exampleGraph", exampleGraph)

    const x_positions = Object.fromEntries(
        Object.entries(graph_nodes).map(([id, node]) => {
            const normalizedTime = parseFloat(node.timestamp);
            return [id, normalizedTime];
        })
    );

    const alignedPositions = {};
    const sortedIds = Object.keys(x_positions).sort((a, b) => x_positions[a] - x_positions[b]);
    
    for (let i = 0; i < sortedIds.length; i++) {
        const currentId = sortedIds[i];
        if (i > 0) {
            const prevId = sortedIds[i-1];
            if (x_positions[currentId] > x_positions[prevId] && x_positions[currentId] - x_positions[prevId] < 10) {
                alignedPositions[currentId] = alignedPositions[prevId];
            } else {
                alignedPositions[currentId] = x_positions[currentId];
            }
        } else {
            alignedPositions[currentId] = x_positions[currentId];
        }
    }

    const nodeWidth = 15;
    const nodePadding = 8;
    const iterations = 90;
    const canva_width = 1000;
    const canva_height = 200;
    const w_scale = canva_width / video_duration;
    console.log("x_positions", x_positions, "scale", w_scale)

    const sankeyLayout = sankey()
        .iterations(iterations)
        .nodeWidth(nodeWidth)
        .nodePadding(nodePadding)
        .extent([[0, 0], [canva_width, canva_height]])
        .nodeId(d => d.id);

    // 创建一个深拷贝的图数据
    const graphCopy = JSON.parse(JSON.stringify(exampleGraph));

    // 确保链接使用正确的节点引用
    graphCopy.links = graphCopy.links.map(d => ({
        ...d,
        source: graphCopy.nodes.find(n => n.id === d.source) || d.source,
        target: graphCopy.nodes.find(n => n.id === d.target) || d.target
    }));

    // 应用布局
    var { nodes, links } = sankeyLayout(graphCopy);

    // 手动设置节点的 x 坐标
    // const xPositions = { "start": 0, "processA": 50, "processB": 100, "processC": 200, "end": 300 };

    nodes.forEach(node => {
        if (Math.abs(node.y0 - node.y1) < 1) {
            node.y0 = 0;
            node.y1 = node.y0 + 20;
        }
    });
    nodes.forEach(node => {
        const x = alignedPositions[node.id];
        if (x !== undefined) {
            node.x0 = x * w_scale;
            node.x1 = x * w_scale + nodeWidth;
        }
    });
    nodes.sort((a, b) => a.x0 - b.x0);  // 按x0排序
    for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
            const otherNode = nodes[j];
            if (otherNode.x0 >= node.x1) break;  // 如果后面的节点x0大于当前节点x1，不需要再比较

            // 检查是否重叠
            if (!(node.y1 <= otherNode.y0 || node.y0 >= otherNode.y1)) {
                // 重叠了，调整y坐标
                let height = otherNode.y1 - otherNode.y0 
                otherNode.y0 = node.y1 + 10;  // 设置一个小间隔
                otherNode.y1 = otherNode.y0 + height;
            }
        }
    }

    console.log("nodes_coor", nodes)

    // 重新应用布局以更新 y 坐标
    const result = sankeyLayout.update({ nodes, links });
    nodes = result.nodes;
    links = result.links;



    console.log("Nodes:", nodes);
    console.log("Links:", links);

    // 调用 drawSankey 函数并返回结果
    return drawSankey({ nodes, links }, canva_width, canva_height);

}

export function drawSankey(graph, canva_width, canva_height) {
    const svgWidth = canva_width;
    const svgHeight = canva_height;
    const chartPadding = 4;

    let svg = d3.create("svg")
        .attr("width", svgWidth + chartPadding * 2)
        .attr("height", svgHeight + chartPadding * 2);

    let g = svg.append("g")
        .attr("transform", `translate(${chartPadding},${chartPadding})`);

    let link = g.append("g")
        .attr("fill", "none")
        .attr("stroke-opacity", 0.2)
        .selectAll("g")
        .data(graph.links)
        .join("g");

    link.append("path")
        .attr("d", sankeyLinkHorizontal())
        .attr("stroke", "grey")
        .attr("stroke-width", d => Math.max(1, d.width));


    link.append("text")
        .attr("dy", -1)
        .attr("font-size", "10px")
        .attr("font-family", "Arial, sans-serif")
        .attr("fill", "black")
        .style("opacity", 0.01)
        .text(d => d.title)
        .each(function() {
            const linkPath = d3.select(this.parentNode).select("path").node();
            const pathLength = linkPath.getTotalLength();
            const midpoint = linkPath.getPointAtLength(pathLength / 2);
            d3.select(this)
                .attr("x", midpoint.x)
                .attr("y", midpoint.y - 10);
        });


    // link.append("title")
    //     .text(d => `${d.source.name} → ${d.target.name}\n${d.value}`);

    let node = g.append("g")
        .selectAll("g")
        .data(graph.nodes)
        .join("g");

    node.append("rect")
        .attr("x", d => d.x0)
        .attr("y", d => d.y0)
        .attr("height", d => d.y1 - d.y0)
        .attr("width", d => d.x1 - d.x0)
        .attr("fill", d => d.color)
        // .attr("stroke", "grey");

    node.append("text")
        .attr("x", d => d.x0 - d.name.length)
        .attr("y", d => d.y1+10)
        .attr("dy", "0.01em")
        .attr("text-anchor", "left")
        .attr("font-size", "6px")  // 设置字号
        .attr("font-family", "Arial, sans-serif")  // 设置字体
        .text(d => d.name);

    // node.append("title")
    //     .text(d => `${d.name}\n${d.value}`);

    function highlightNode(event, d) {
        // 降低所有元素的不透明度
        node.style("opacity", 0.1);
        link.style("opacity", 0.1);

        // 高亮当前节点
        d3.select(this).style("opacity", 1);

        // 高亮相关的链接和节点
        link.filter(l => l.source === d || l.target === d)
            .style("opacity", 1)
            .each(function(l) {
                node.filter(n => n === l.source || n === l.target)
                    .style("opacity", 1);
            });
    }

    function highlightLink(event, d) {
        // 降低所有元素的不透明度
        node.style("opacity", 0.3);
        link.style("opacity", 0.3);

        // 高亮当前链接
        d3.select(this).style("opacity", 1);
        d3.select(this).select("text").style("opacity", 1);

        // 高亮相关的节点
        node.filter(n => n === d.source || n === d.target)
            .style("opacity", 1);
            
    }

    function unhighlight() {
        // 恢复所有元素的不透明度
        node.style("opacity", 1);
        link.style("opacity", 1);
        link.select("text").style("opacity", 0);
    }
    node
        .on("mouseover", highlightNode)
        .on("mouseout", unhighlight);

    link
        .on("mouseover", highlightLink)
        .on("mouseout", unhighlight);

    console.log("svgnode", node, "svglink", link)

    const cleanup = () => {
        svg.selectAll("*").on("mouseover", null).on("mouseout", null);
        svg.remove();
        console.log("流程图清理完成");
    };

    return {
        node: svg.node(),
        cleanup: cleanup
    };
}
// function nodeColour(x) {
//   return d3.interpolateWarm(x/20);  // 假设x的最大值是350
// }

export function getVisFeature(concept) {
    let type = "";
    let value = -1;

    if (concept.is_important === "True") {
        const score = parseFloat(concept.features.importance_score.graph)
        value = score;
        type = "important"
    } else {
        const score = parseFloat(concept.features.challenging_rank.unfamiliar)
        type = "challenging"
        value = score;
    }
    return {type, value}
}

export function calculateVisFeature(concept, time) {
    let type = "";
    let value = -1;
    const start = time;
    const end = time + 30;
    for (let ts of Object.values(concept.timestamp)) {
        if (ts >= start && ts <= end) {
            const ret = getVisFeature(concept)
            type = ret.type
            value = ret.value
        }
    }
    console.log("calculateValue", concept.label, time, type, value);
    return {'type': type, 'value': value};
}

export function getImportantConcepts(dict) {

    const important_concepts = Object.fromEntries(
        Object.entries(dict).filter(([, item]) => 
            item.is_important === "True"
        )
    );

    const max_imp_value = d3.max(Object.values(important_concepts), concept => {
        if (concept.is_important === "True") {
            return parseFloat(concept.features.importance_score.graph);
        }
    });
    return { important_concepts, max_imp_value };
}


export function getChallengingConcepts(dict) {

    const challenging_concepts = Object.fromEntries(
        Object.entries(dict).filter(([, item]) => 
            item.is_challenging === "True"
        )
    );

    const max_clg_value = d3.max(Object.values(challenging_concepts), concept => {
        if (concept.is_challenging === "True") {
            return parseFloat(concept.features.challenging_rank.unfamiliar);
        }
    });

    return { challenging_concepts, max_clg_value };
}
export function getMaxImpScore() {

}

export function getFill(type, value, colorImportantScale, colorChallengingScale) {
    if (type === "important") {
        return colorImportantScale(value);
    } else if (type === "challenging") {
        return colorChallengingScale(value);
    } else {
        return "white";
    }
}
export function createChart(containerWidth, node_data) {

    const conceptFeatureDict = node_data.network_nodes
    const video_duration = node_data.video_duration
    console.log("video_duration", video_duration)
    console.log("createChart", conceptFeatureDict)


    const { important_concepts, max_imp_value } = getImportantConcepts(conceptFeatureDict);

    const { challenging_concepts, max_clg_value } = getImportantConcepts(conceptFeatureDict);


    const y_concepts = Object.fromEntries(
        [...new Set([...Object.entries(important_concepts), ...Object.entries(challenging_concepts)])]
    );

    const sortedConcepts = Object.values(y_concepts)
    .filter(value => value && value.label) // 过滤掉无效的条目
    .sort((aValue, bValue) => {
        if (aValue.label && bValue.label) {
            return aValue.label.localeCompare(bValue.label, undefined, {sensitivity: 'base'});
        }
        return 0; // 如果标签不存在，保持原有顺序
    });

    console.log("sortedConcepts", sortedConcepts)

    console.log("important_concepts", important_concepts)

    // 创建时间轴数据 (每30秒一个间隔)
    const timeIntervals = d3.range(0, video_duration + 1, 30);

    // 使用important_concepts的label作为items数据
    const items = Object.values(sortedConcepts).map(concept => concept.label);


    const margin = { top: 40, right: 40, bottom: 60, left: 150 };
    const width = 25 * timeIntervals.length;
    const height = 13 * sortedConcepts.length;

    // 生成数据
    const data = d3.cross(Object.entries(y_concepts), timeIntervals).map(([[, concept], time]) => {
        const feature = calculateVisFeature(concept, time);
        return {
            item: concept.label,
            time: time,
            type: feature.type,
            value: feature.value
        };
    });
    const x = d3.scaleLinear()
        .domain([0, d3.max(timeIntervals)])
        .range([0, width]);

    const y = d3.scaleBand()
        .domain(items)
        .range([height, 0])
        .padding(0.1);

    const colorImportantScale = d3.scaleSequential()
        .domain([0, max_imp_value])
        .interpolator(d3.interpolateRgb("#FFF5E6", "#FF9E4A"));  // 从浅橙色到 #FF9E4A
    
    const colorChallengingScale = d3.scaleSequential()
        .domain([max_clg_value, 0])  // 反转域，使得0对应最深的颜色
        .interpolator(d3.interpolateRgb("#F3E5F5", "#AD8BC9"));  // 从浅紫色到 #AD8BC9

    
    // const color = d3.scaleSequential(d3.interpolateBlues)
    //     .domain([0, d3.max(data, d => d.value)]);

    // 创建SVG
    const svg = d3.create("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);

    const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // 绘制热图矩形
    g.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", d => x(d.time))
        .attr("y", d => y(d.item))
        .attr("width", width / (timeIntervals.length - 1))
        .attr("height", y.bandwidth())
        .attr("fill", d => getFill(d.type, d.value, colorImportantScale, colorChallengingScale))
    .append("title")
        .append("title")
        .text(d => `Item: ${d.item}\nTime: ${formatSeconds(d.time)}\\Value: ${d.value}`);

    // 添加x轴
    g.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .tickValues(timeIntervals)  // 使用timeIntervals作为刻度值
            .tickFormat(d => formatSeconds(d)))
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    // 添加y轴
    g.append("g")
        .call(d3.axisLeft(y));


    // 清理函数
    const cleanup = () => {
        console.log("Chart cleanup");
    };

    return {
        node: svg.node(),
        cleanup: cleanup
    };
}

// 添加格式化秒数的函数
function formatSeconds(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}