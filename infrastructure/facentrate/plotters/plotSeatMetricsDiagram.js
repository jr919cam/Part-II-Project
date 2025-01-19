function plotSeatMetricsDiagram(piePercent, concentrationEdges) {
    const width = 600;
    const height = 300;

    const concentrationEdgesPercent = Math.pow(Math.E, -concentrationEdges/10)

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height + 10])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black;")
        .attr("id", "seatMetricsDiagram")

    // avg occupancy
    svg.append("rect")
        .attr("width", width/10)
        .attr("height", 3*height/4)
        .attr("transform", `translate(${width/10},${height/5})`)
        .attr("stroke", "black")
        .attr("stroke-width", "2")
        .attr("fill", "white");

    // stability
    svg.append("rect")
        .attr("width", width/10)
        .attr("height", 3*height/4)
        .attr("transform", `translate(${4*width/10},${height/5})`)
        .attr("stroke", "black")
        .attr("stroke-width", "2")
        .attr("fill", "white");

    const yScale = d3.scaleLinear()
        .domain([0, 1])
        .range([3*height/4, 0]);

    
    const avgOccupancyBarHeight = 3*height/4 - yScale(piePercent ?? 0);
    const stabilityBarHeight = 3*height/4 - yScale(concentrationEdgesPercent ?? 0);

    svg.append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("width", width/10)
        .attr("fill", "orange")
        .attr("stroke", "black")
        .attr("stroke-width", "2")
        .attr("transform", `translate(${width/10},${height/5})`)
        .attr("y", yScale(piePercent ?? 0))
        .attr("height", avgOccupancyBarHeight);

    svg.append("rect")
        .attr("class", "bar")
        .attr("x", 0)
        .attr("width", width/10)
        .attr("fill", "blue")
        .attr("stroke", "black")
        .attr("stroke-width", "2")
        .attr("transform", `translate(${4*width/10},${height/5})`)
        .attr("y", yScale(concentrationEdgesPercent ?? 0))
        .attr("height", stabilityBarHeight);

    const yAxis = d3.axisLeft(yScale).ticks(5).tickFormat(d => +d*100 + "%");
    svg.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(${width/10},${height/5})`)
        .call(yAxis);
    
    svg.append("text")
        .attr("x", 2.15*width/10)
        .attr("y", 1.1*height/2)
        .attr("text-anchor", "middle")
        .attr("font-size", "20px")
        .attr("transform", ` rotate(90, ${2.15*width/10}, ${1.1*height/2})`)
        .text("mean seat occupancy");
    
    svg.append("g")
        .attr("class", "axis")
        .attr("transform", `translate(${4*width/10},${height/5})`)
        .call(yAxis);

        svg.append("text")
        .attr("x", 5.15*width/10)
        .attr("y", 1.1*height/2)
        .attr("text-anchor", "middle")
        .attr("font-size", "25px")
        .attr("transform", ` rotate(90, ${5.15*width/10}, ${1.1*height/2})`)
        .text("seat stability");

    return svg.node()
}

export default plotSeatMetricsDiagram