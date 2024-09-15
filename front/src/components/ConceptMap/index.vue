<template>
    <div class="conceptMap">
        <div id="viz1" ref="viz1" class="concept-map-container" style="width:100%;height:100%"></div>
        <button @click="toggleFullscreen" class="fullscreen-button">
            <img :src="currentFullscreenIcon" alt="fullScreen" class="fullscreen-icon">
        </button>
    </div>
</template>
 
<script>
// import NeoVis from 'neovis.js';

import * as vis from 'vis-network'

export default {
    name: 'ConceptMap',
    components: {},
    props: {
        conceptMapData: {
            type: Object,
            default: () => ({}), // 默认值为空对象
        },
        numberPercent: {
            type: Number,
            default: 1.0
        },
        smallMode: {
            type: Boolean,
            default: true
        },
        cameraNodeID: {
            type: String,
            default: "", 
        }
    },
    computed: {
        currentFullscreenIcon() {
        return this.isFullscreen ? this.fullscreenIconActive : this.fullscreenIconInactive;
        }
    },
    data() {
        return {
            isFullscreen: false,
            fullscreenIconInactive: '/assets/noun-expand-4763815.svg',
            fullscreenIconActive: '/assets/noun-collapse-4763799.svg',
            visNetwork: null,
            drawData: null
        }
    },
    watch: {
        cameraNodeID: {
            handler(val) {
                console.log("[ConceptMap] cameraNodeID change", val)
                this.cameraMove()
            }
        },
        smallMode: {
            handler(mode) {
                console.log("[ConceptMap] window mode change", mode)
                this.drawVis(this.conceptMapData)
            }

        },
        numberPercent: {
            handler(numberPercent) {
                console.log("[ConceptMap] num change", numberPercent)
                this.drawVis(this.conceptMapData)
            }
        },
        conceptMapData: {
            handler(newMap) {
                console.log("[ConceptMap] watch conceptMapData change", newMap)
                if (Object.keys(newMap.nodes).length === 0) {
                    // 如果 newMap 为空，则清空界面
                    console.log("[ConceptMap] clear", newMap)
                    this.clearVis();
                } else {
                    this.drawVis(newMap)
                }
            },
            immediate: true, // Run immediately on component creation
        }
    },
    mounted() { 
        // this.draw()
        if (this.conceptMapData) {
            this.drawVis(this.conceptMapData)
        }
     }, //渲染
    methods: {
        toggleFullscreen () {
            this.isFullscreen = !this.isFullscreen;
            this.$emit('change-concept-map-full-screen-mode', this.isFullscreen);
        },
        sortNodes(dict) {
            let edgesList = Object.values(dict.edges)

            let nodeDegrees = {};
            edgesList.forEach(edge => {
                nodeDegrees[edge.from] = (nodeDegrees[edge.from] || 0) + 1;
                nodeDegrees[edge.to] = (nodeDegrees[edge.to] || 0) + 1;
            });
            let sortedNodes = Object.values(dict.nodes).sort((a, b) => {
                return (nodeDegrees[b.id] || 0) - (nodeDegrees[a.id] || 0);
            });
            return sortedNodes
        },
        filterLeafNodes(dict) {
            const nonLeaf = Object.fromEntries(
                Object.entries( dict.nodes).filter(([, node]) => 
                node.degree > 1
                )
            );
            const edges = Object.fromEntries(
                Object.entries(dict.edges).filter(([, edge]) => 
                nonLeaf[edge.from] && nonLeaf[edge.to]
                )
            );
            let nodeDegrees = {};
            Object.values(edges).forEach(edge => {
                nodeDegrees[edge.from] = (nodeDegrees[edge.from] || 0) + 1;
                nodeDegrees[edge.to] = (nodeDegrees[edge.to] || 0) + 1;
            });

            const nodes = Object.fromEntries(
                Object.entries(nonLeaf).filter(([, node]) => 
                nodeDegrees[node.id] > 0
                )
            );
            return {'nodes': nodes, 'edges': edges}
        },
        getImportantConcepts(dict) {
            console.log("getImportantConcepts", dict)

            const important_concepts = Object.fromEntries(
                Object.entries(dict).filter(([, item]) => 
                    item.is_important === "True"
                )
            );
            return important_concepts
            // const max_imp_value = Math.max(Object.values(important_concepts), concept => {
            //     if (concept.is_important === "True") {
            //         return parseFloat(concept.features.importance_score.graph);
            //     }
            // });
            // return { important_concepts, max_imp_value };
        },

        drawVis(map_data) {
            if (!map_data) {
                return
            }
            // const filteredNodes = this.getImportantConcepts(map_data.nodes)
            const filteredData = this.smallMode ? this.filterLeafNodes(map_data) : map_data
            console.log("[ConceptMap] filteredData", filteredData)

            let num = Object.values(filteredData.nodes).length
            let targetNum = Math.round(this.numberPercent * num)

            this.drawData = filteredData
            if (targetNum != num) {
                const sortedNodes = this.sortNodes(filteredData).slice(0, targetNum);
                console.log("[ConceptMap] sortedNodes", sortedNodes)

                const finalNodes = sortedNodes.reduce((acc, node) => {
                    acc[node.id] = node;
                    return acc;
                }, {});
                console.log("[ConceptMap] finalNodes", finalNodes)

                const finalEdges = Object.fromEntries(
                    Object.entries(map_data.edges).filter(([, edge]) => 
                    finalNodes[edge.from] && finalNodes[edge.to]
                    )
                );

                this.drawData = {
                    "nodes": finalNodes,
                    "edges": finalEdges
                }
            }

            var data = {
                "nodes": Object.values(this.drawData.nodes),
                "edges": Object.values(this.drawData.edges)
            }
            const container = document.getElementById('viz1');
            var options = {
                nodes: {
                shape: "dot",
                borderWidth: 0,
                },
                layout: {
                    randomSeed: 1,
                },
                interaction: {
                    hover: true
                }
            };
            this.network = new vis.Network(container, data, options);

            // 保存原始标签
            for (let edgeId in this.network.body.edges) {
                let edge = this.network.body.edges[edgeId];
                console.log("[ConceptMap]edge:", edge);
                edge.options.originalLabel = edge.title;
                edge.options.label = undefined;  // 初始时隐藏所有标签
            }

            this.network.on("click", (params) => {
                if (params.nodes.length > 0) {
                    let nodeId = params.nodes[0]; // Get the clicked node ID
                    let clickedNode = map_data.nodes[nodeId]; // Get the clicked node data
                    console.log("[ConceptMap] Node clicked:", clickedNode);
                    this.handleNodeClick(clickedNode);
                    // Add additional actions here (e.g., display node details, trigger events, etc.)
                }
            });

            this.network.on("hoverNode", (params) => {
                this.fadeOtherNodes(params.node);
            });

            this.network.on("blurNode", () => {
                this.resetNodesOpacity();
            });

            this.network.on("hoverEdge", (params) => {
                this.showEdgeLabel(params.edge);
            });

            this.network.on("blurEdge", () => {
                this.hideEdgeLabel();
            });

            this.network.once("afterDrawing", () => {
                this.cameraMove()
            });
            console.log("[ConceptMap]", this.network)
        },
        cameraMove() {
            let targetNode = this.cameraNodeID
            console.log("targetNode",  targetNode);
            if (!targetNode || !this.drawData.nodes[targetNode]){
                let sortNodes = this.sortNodes(this.drawData)
                targetNode = sortNodes[0].id
            }
            const nodePosition = this.network.getPosition(targetNode);
            console.log("nodePosition",  this.drawData);

            if (nodePosition) {
                // 如果找到了节点 A 的位置，移动到该位置
                this.network.moveTo({
                    position: {x: nodePosition.x, y: nodePosition.y},
                    scale: 0.5, // 可以根据需要调整缩放级别
                    offset: {x: 0, y: 0},
                    animation: {
                        duration: 1000,
                        easingFunction: 'easeInOutQuad'
                    }
                });
            }
        },
        clearVis() {
            if (this.network) {
                this.network.destroy(); // 销毁现有网络实例
            }
            // 清空容器
            this.$nextTick(() => {
                const container = this.$refs.viz1;
                if (container) {
                container.innerHTML = ''; // 清空 DOM 内容
                }
            });
        },
        handleNodeClick(node) {
            this.$emit('click-concept-map-node', node);
        },
        fadeOtherNodes(nodeId) {
            const allNodes = this.network.body.nodes;
            const allEdges = this.network.body.edges; 
            const connectedNodes = this.network.getConnectedNodes(nodeId);
            const connectedEdges = this.network.getConnectedEdges(nodeId);


            // 降低非连接节点的透明度
            for (let id in allNodes) {
                if (id !== nodeId && !connectedNodes.includes(id)) {
                    allNodes[id].options.opacity = 0.1;
                } else {
                    allNodes[id].options.opacity = 1;
                }
            }

            // 降低非连接边的透明度
            for (let edgeId in allEdges) {
                if (!connectedEdges.includes(edgeId)) {
                    allEdges[edgeId].options.opacity = 0.1;
                    allEdges[edgeId].options.label = undefined;
                } else {
                    allEdges[edgeId].options.opacity = 1;
                    // 显示连接边的标签
                    if (allEdges[edgeId].options.originalLabel) {
                        allEdges[edgeId].options.label = allEdges[edgeId].options.originalLabel;
                    }
                }
            }
            // 保持悬停节点的完全不透明
            allNodes[nodeId].options.opacity = 1;

            this.network.redraw();
        },

        resetNodesOpacity() {
            const allNodes = this.network.body.nodes;
            const allEdges = this.network.body.edges;

            // 重置所有节点和边的透明度
            for (let nodeId in allNodes) {
                allNodes[nodeId].options.opacity = 1;
            }

            for (let edgeId in allEdges) {
                allEdges[edgeId].options.opacity = 1;
                allEdges[edgeId].options.label = undefined;
            }

            this.network.redraw();
        },

        showEdgeLabel(edgeId) {
            const edge = this.network.body.edges[edgeId];
            if (edge && edge.options.originalLabel) {
                edge.options.label = edge.options.originalLabel;
                this.network.redraw();
            }
        },

        hideEdgeLabel() {
            for (let edgeId in this.network.body.edges) {
                this.network.body.edges[edgeId].options.label = undefined;
            }
            this.network.redraw();
        }

        // draw() {
        //     var viz;
        //     console.log("draw viz");
        //     var config = {
        //         containerId: "viz1",
        //         neo4j: {
        //             serverUrl: "bolt://localhost:7687",
        //             serverUser: "neo4j",
        //             serverPassword: "12345678",
        //         },
        //         visConfig: {
        //             nodes: {
        //                 shape: 'dot'
        //             }
        //         },
        //         labels: {
        //             concept: {
        //                 label: "name",
        //                 value: "score" 
        //             }
        //         },
        //         initialCypher: "MATCH (n:concept)-[r]->(m:concept) RETURN n,r,m"
        //     };
            
        //     viz = new NeoVis(config);
        //     viz.render();
        //     viz.registerOnEvent('clickNode', (e) => {
		// 		this.handleNodeClick(e);
		// 	});
        //     console.log(viz);
        // },
    },
}
</script>


  
<style>@import './index.css';</style>