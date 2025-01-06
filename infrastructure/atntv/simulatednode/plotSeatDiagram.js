const mapSeatToPixel = {
    "MA1": [10,390],
    "MA2": [30,390],
    "MA3": [50,390]
}

const plotSeatDiagram = (seats) => {
    const width = 400;
    const height = 400;

    const svg = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

    svg.append("image")
            .attr("href", "infrastructure/gridExample.jpg")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", width)
            .attr("height", height);

    svg.selectAll("circle")
        .data(seats)
        .enter()
        .append("circle")
        .attr("cx", s => mapSeatToPixel[s][0])
        .attr("cy", s => mapSeatToPixel[s][1])
        .attr("r", 5)
        .attr("fill", "red");

    return svg.node()
}

export default plotSeatDiagram