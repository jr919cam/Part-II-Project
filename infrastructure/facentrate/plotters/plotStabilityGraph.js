const plotStabilityGraph = (wholeRoomStability, height, width, startTime=null, endTime=null, day=null) => {
    const startTimeString = `2024-01-${day}T${startTime}:00`;
    const start = new Date(startTimeString);
    const startTimeStamp = Math.floor(start.getTime() / 1000);

    const endTimeString = `2024-01-${day}T${endTime}:00`;
    const end = new Date(endTimeString);
    const endTimeStamp = Math.floor(end.getTime() / 1000);

    const marginTop = 20;
    const marginRight = 30;
    const marginBottom = 45;
    const marginLeft = 40;

    const x = startTime && endTime ? 
        d3.scaleLinear().domain([startTimeStamp, endTimeStamp])
        .range([marginLeft, width - marginRight]) :
        d3.scaleLinear().domain(d3.extent(wholeRoomStability.seatsOccupiedDiffCount, s=>s.acp_ts)).nice()
        .range([marginLeft, width - marginRight]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(wholeRoomStability.seatsOccupiedDiffCount, s=>s.value)]).nice()
        .range([marginTop, height-marginBottom]);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height+5])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black;")
        .attr("id", "stabilityChart")

    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks((width / 150)).tickFormat(d => d3.timeFormat("%H:%M:%S")(d * 1000)))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick text").style("font-size", "16px"));

    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y).ticks(3))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line"))
        .call(g => g.selectAll(".tick text").style("font-size", "0px"));

    const seatsOccupiedDiffLine = d3.line()
        .x(d => x(d.acp_ts))
        .y(d => y(d.value));

    svg.append("path")
        .datum(wholeRoomStability.seatsOccupiedDiffCount)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 2)
        .attr("opacity", 0.8)
        .attr("d", seatsOccupiedDiffLine);
    
    svg.append("text")
        .attr("x", -height / 2)
        .attr("y", 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "25px")
        .attr("transform", "rotate(-90)")
        .text("Room Stability");

    return svg.node();
}

export default plotStabilityGraph