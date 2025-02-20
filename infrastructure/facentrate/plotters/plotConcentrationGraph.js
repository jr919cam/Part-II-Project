const plotConcentrationGraph = (concentration, height, width, startTime=null, endTime=null, day=null) => {
    const startTimeString = `${day}T${startTime}:00`;
    const start = new Date(startTimeString);
    const startTimeStamp = Math.floor(start.getTime() / 1000);

    const endTimeString = `${day}T${endTime}:00`;
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
        .domain([1, 0]).nice()
        .range([marginTop, height-marginBottom]);

    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height+5])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black; background-color: white; margin: 0.5vw 0.5vw 0 0")
        .attr("id", "concentrationChart")

    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks((width / 150)).tickFormat(d => d3.timeFormat("%H:%M:%S")(d * 1000)))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick text").style("font-size", "16px"));

    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y).ticks(5))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line"))
        .call(g => g.selectAll(".tick text").style("font-size", "16px"))
        .call(g => g.selectAll(".tick line")
            .clone()
                .attr("x2", width - marginRight - marginLeft)
                .attr("stroke-opacity", 0.1))
            .call(g => g.selectAll(".tick text")
                .style("font-size", "15px")
        );

    const concentrationLine = d3.line()
        .x(c => x(c.acp_ts))
        .y(c => y(c.value));

    const sdArea = d3.area()
        .x(c => x(c.acp_ts))
        .y0(c => y(c.value - c.sd))
        .y1(c => y(c.value + c.sd));

    svg.append("path")
        .datum(concentration)
        .attr("class", "area")
        .attr("fill", "lightblue")
        .attr("opacity", 0.5)
        .attr("d", sdArea);

    // svg.append("path")
    //     .datum(concentration)
    //     .attr("class", "line")
    //     .attr("d", concentrationLine);

    svg.append("path")
        .datum(concentration)
        .attr("fill", "none")
        .attr("stroke", "black")
        .attr("stroke-width", 5)
        .attr("opacity", 0.5)
        .attr("d", concentrationLine);

    svg.append("text")
        .attr("x", -height / 2)
        .attr("y", 5)
        .attr("text-anchor", "middle")
        .attr("font-size", "20px")
        .attr("transform", "rotate(-90)")
        .text("Concentration");

    return svg.node();
}

export default plotConcentrationGraph;