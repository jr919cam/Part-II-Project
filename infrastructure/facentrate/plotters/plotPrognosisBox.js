const plotPrognosisBox = (svg, metrics) => {
    svg.append("rect")
    .attr("y", 8)
    .attr("x", 38)
    .attr("width", 154)
    .attr("height", 104)
    .attr("fill", "black")
    .attr("rx", 10)
    .attr("ry", 10)

    svg.append("rect")
    .attr("y", 10)
    .attr("x", 40)
    .attr("width", 150)
    .attr("height", 100)
    .attr("stroke", "#7fff78")
    .attr("stroke-width", 2)
    .attr("fill", "white")
    .attr("rx", 10)
    .attr("ry", 10)


    Object.keys(metrics).map((metric, i) => {
        svg.append("text")
        .attr("x", 50)
        .attr("y", 30 + 20*i)
        .text(`${metric}: ${metrics[metric]}`)
    }) 
}

export default plotPrognosisBox