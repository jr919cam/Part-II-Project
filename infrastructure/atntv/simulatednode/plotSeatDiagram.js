const plotSeatDiagram = (seats) => {
    const width = 928;
    const height = 928;

    const mHorizontalSeatGap = width/31.9
    const mVerticalSeatGap = height/17.45
    const mColumnStart = height/1.41
    const mRowStart = width/3.39

    const lColumnStart = height/1.347
    const lRowStart = width/33
    const lHorizontalSeatGap = width/34.5
    const lVerticalSeatGap = height/17.4
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
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height + 10])
            .attr("style", "max-width: 100%; height: auto; border:1px solid black;")
            .attr("id", "seatDiagram");

    svg.append("image")
            .attr("href", "infrastructure/LT1_seating_uncompressed.png")
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
        .attr("r", 6)
        .attr("fill", "red");

    return svg.node()
}

export default plotSeatDiagram