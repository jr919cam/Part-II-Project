const plotPrognosisBox = (svg, x, metrics) => {
    const textWidth = d3.max(Object.keys(metrics), metric => {
        return metrics[metric].length  + metric.length
    }) * 10

    const rect = svg.append("rect")
    .attr("y", 10)
    .attr("x", x + 10)
    .attr("width", textWidth)
    .attr("height", 100)
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .attr("fill", "white")
    .attr("opacity", 0.5)
    .on("mouseover", function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr("opacity", 1);
      })
    .on("mouseout", function() {
    d3.select(this)
        .transition()
        .duration(200)
        .attr("opacity", 0.5);
    })
    .attr("rx", 10)
    .attr("ry", 10)

    Object.keys(metrics).map((metric, i) => {
        svg.append("text")
        .attr("x", x + 15)
        .attr("y", 30 + 20*i)
        .text(`${metric}: ${metrics[metric]}`)
    }) 
}

export default plotPrognosisBox