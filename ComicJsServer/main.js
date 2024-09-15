const fs = require('fs');
const { JSDOM } = require('jsdom');
const rough = require('roughjs/bundled/rough.cjs');

function parseSvg(inputSVGPath, outputSVGPath, markerWidth=16, markerHeight=12) {
  const svgContent = fs.readFileSync(inputSVGPath, 'utf8');
  const dom = new JSDOM(svgContent);
  const document = dom.window.document;
  
  const svg = document.querySelector('svg');

  // 添加 defs 元素
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
  style.textContent = `
    @font-face {
      font-family: "Virgil";
      src: url("https://excalidraw.com/Virgil.woff2");
    }
  `;
  defs.appendChild(style);


  const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
  marker.setAttribute('id', 'markerArrow');
  marker.setAttribute('markerWidth', markerWidth);
  marker.setAttribute('markerHeight', markerHeight);
  marker.setAttribute('refX', markerWidth);
  marker.setAttribute('refY', markerHeight / 2);
  marker.setAttribute('orient', 'auto');

  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', `M${markerWidth},${markerHeight/2} L0,0 M${markerWidth},${markerHeight/2} L0,${markerHeight}`);
  path.setAttribute('stroke', 'black');
  path.setAttribute('fill', 'none');

  marker.appendChild(path);
  defs.appendChild(marker);
  
  // 将 defs 插入到 svg 的第一个子元素之前
  svg.insertBefore(defs, svg.firstChild);


  
  
  
  if (!svg) {
    return
  }
  
  const rc = rough.svg(svg);
  
  modifyElement(svg, rc);
  
  fs.writeFileSync(outputSVGPath, svg.outerHTML);
}

function modifyElement(element, rc) {
  if (element.tagName.toLowerCase() === 'polygon') {
    replacePolygon(element, rc);
  } else if (element.tagName.toLowerCase() === 'text') {
    replaceTextFont(element);
  } else if (element.tagName.toLowerCase() === 'path') {
    replacePath(element, rc);
  } else {
    for (let child of Array.from(element.children)) {
      modifyElement(child, rc);
    }
  }
}
function replaceTextFont(textElement) {
  textElement.setAttribute('font-family', "Virgil, Segoe UI Emoji");
}
function replacePath(pathEle, rc) {
  pathStr = pathEle.getAttribute('d')
  const strokeAttr = pathEle.getAttribute('stroke')
  const strokeWidthAttr = pathEle.getAttribute('stroke-width')
  const fillAttr = pathEle.getAttribute('fill')

  const rcPath = rc.path(pathStr);

  const tempContainer = pathEle.ownerDocument.createElement('div');
  tempContainer.innerHTML = rcPath.outerHTML;
  tempElement = tempContainer.firstChild.firstChild
  tempElement.setAttribute('stroke', strokeAttr)
  tempElement.setAttribute('stroke-width', strokeWidthAttr)
  tempElement.setAttribute('fill', fillAttr)
  tempElement.setAttribute('marker-end',"url(#markerArrow)")

  pathEle.parentNode.replaceChild(tempElement, pathEle);
}
function replacePolygon(polygonElement, rc) {
  const points = convertPointsToList(polygonElement.getAttribute('points'));
  const strokeAttr = polygonElement.getAttribute('stroke')
  const fillAttr = polygonElement.getAttribute('fill')
  var arg = {}
  if (fillAttr == 'black')
    arg = {'fill': 'black'}
  const roughPolygon = rc.polygon(points, arg);
  
  // 创建一个临时容器来保存 Rough.js 生成的内容
  const tempContainer = polygonElement.ownerDocument.createElement('div');
  tempContainer.innerHTML = roughPolygon.outerHTML;
  tempElement = tempContainer.firstChild.firstChild
  tempElement.setAttribute('stroke', strokeAttr)
  tempElement.setAttribute('fill', fillAttr)
  console.log(tempElement.outerHTML)
  // 替换原始的 polygon 元素
  polygonElement.parentNode.replaceChild(tempElement, polygonElement);
}

function convertPointsToList(pointsString) {
  if (!pointsString) return [];
  
  return pointsString.trim().split(/\s+/).map(pair => {
    const [x, y] = pair.split(',').map(Number);
    return [x, y];
  });
}

const inputSVGPath = process.argv[2];
const outputSVGPath = process.argv[3];
parseSvg(inputSVGPath, outputSVGPath);