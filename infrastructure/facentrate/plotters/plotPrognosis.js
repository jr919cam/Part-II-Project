// Intended to be called within other D3.js filess

const plotPrognosis = (svg, xDomainToRange, yDomainToRange, means, sds, grads, lectureBounds) => {
  console.log(lectureBounds)
  lectureBounds.map(([startTs, endTs], i) => {
    const startTsX = xDomainToRange(startTs)
    const endTsX = xDomainToRange(endTs)
    const topY = yDomainToRange(means[i] + sds[i])
    const bottomY = yDomainToRange(means[i] - sds[i])

    const points = `${startTsX},${topY}, ${endTsX},${topY - grads[i] * (endTs - startTs)}, ${endTsX},${bottomY - grads[i] * (endTs - startTs)}, ${startTsX},${bottomY }`

    svg.append("polygon")
      .attr("points", points)
      .attr("fill", "yellow")
      .attr("opacity", 0.25)

      svg.append("line")
      .attr("x1", startTsX)
      .attr("y1", bottomY)
      .attr("x2", endTsX)
      .attr("y2", bottomY - grads[i] * (endTs - startTs))
      .attr("stroke", "orange")
      .attr("stroke-width", 1);

    svg.append("line")
      .attr("x1", startTsX)
      .attr("y1", topY)
      .attr("x2", endTsX)
      .attr("y2", topY - grads[i] * (endTs - startTs))
      .attr("stroke", "orange")
      .attr("stroke-width", 1);

    svg.append("line")
      .attr("x1", startTsX)
      .attr("y1", (topY+bottomY)/2)
      .attr("x2", endTsX)
      .attr("y2", (topY+bottomY)/2 - grads[i] * (endTs - startTs))
      .attr("stroke", "orange")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "4 4"); 
  })
}
    
export default plotPrognosis