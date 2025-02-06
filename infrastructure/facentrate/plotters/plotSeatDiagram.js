const plotSeatDiagram = (seats, seatsHistory) => {
    const width = 600;
    const height = 600;

    const mHorizontalSeatGap = width/31.9
    const mVerticalSeatGap = height/17.45
    const mColumnStart = height/1.41
    const mRowStart = width/3.39

    const lColumnStart = height/1.347
    const lRowStart = width/33
    const lHorizontalSeatGap = width/34.5
    const lVerticalSeatGap = height/17.35
    const lVerticalOffset = height/200

    const rColumnStart = height/1.35
    const rRowStart = width/1.03
    const rHorizontalSeatGap = width/35
    const rVerticalSeatGap = height/17.45
    const rVerticalOffset = height/200
    
    const mapSeatToPixel = {}
    for(let i = 1; i <= 14 ; i++) {
        for(let j = 1; j <= 12; j++) {
            if (j <=9 ) {
                mapSeatToPixel[`M${String.fromCharCode(64 + j)}${i}`] = [mRowStart + mHorizontalSeatGap * (i-1), mColumnStart - mVerticalSeatGap * (j-1)]
            }
            if (i <= 6) {
                mapSeatToPixel[`L${String.fromCharCode(64 + j)}${i}`] = [lRowStart + lHorizontalSeatGap * (i-1), lColumnStart - lVerticalSeatGap * (j-1) - lVerticalOffset * (i-1)]
                if (j <=11 ) {
                    mapSeatToPixel[`R${String.fromCharCode(64 + j)}${7-i}`] = [rRowStart - rHorizontalSeatGap * (i-1), rColumnStart - rVerticalSeatGap * (j-1) - rVerticalOffset * (i-1)]
                }
            }
        }
    }

    const svg = d3.select("body")
            .append("svg")
            .attr("viewBox", [0, 0, width, height + 10])
            .attr("style", "max-width: 100%; height: auto; background-color: white;")
            .attr("id", "seatDiagram");

    svg.append("image")
            .attr("href", "infrastructure/LT1_seating_uncompressed.png")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", width)
            .attr("height", height);

    svg.selectAll(".seatHistoryCircle")
        .data(seatsHistory)
        .enter()
        .append("circle")
        .attr("cx", s => mapSeatToPixel[s][0])
        .attr("cy", s => mapSeatToPixel[s][1])
        .attr("r", 8)
        .attr("fill", "orange")
        .attr("opacity", 0.4);
    
    svg.selectAll(".seatCircle")
        .data(seats)
        .enter()
        .append("circle")
        .attr("cx", s => mapSeatToPixel[s][0])
        .attr("cy", s => mapSeatToPixel[s][1])
        .attr("r", 4)
        .attr("fill", "red");

    svg.append("rect")
        .attr("width", width/3)
        .attr("height", height/10)
        .attr("transform", `translate(${width - 5*width/17.5},${height/40})`)
        .attr("fill", "#eaeaea")
    svg.append("circle").attr("cx", width - 5*width/20).attr("cy",height/20).attr("r", 6).style("fill", "red")
    svg.append("circle").attr("cx", width - 5*width/20).attr("cy",2*height/20).attr("r", 6).style("fill", "orange")
    svg.append("text").attr("x", width - 5*width/20 + 15).attr("y", height/20).text("seat occupied").style("font-size", "15px").attr("alignment-baseline","middle")
    svg.append("text").attr("x", width - 5*width/20 + 15).attr("y", 2*height/20).text("seat was occupied").style("font-size", "15px").attr("alignment-baseline","middle")

    return svg.node()
}

export default plotSeatDiagram