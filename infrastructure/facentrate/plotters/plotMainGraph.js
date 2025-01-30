const plotMainGraph = (data, events, barcodes, variance, sensor, height, width, startTime=null, endTime=null, day=null) => {
    const startTimeString = `${day}T${startTime}:00`;
    const start = new Date(startTimeString);
    const startTimeStamp = Math.floor(start.getTime() / 1000);

    const endTimeString = `${day}T${endTime}:00`;
    const end = new Date(endTimeString);
    const endTimeStamp = Math.floor(end.getTime() / 1000);

    const marginTop = 20;
    const marginRight = 50;
    const marginBottom = 45;
    const marginLeft = 40;

    const x = startTime && endTime ? 
        d3.scaleLinear().domain([startTimeStamp, endTimeStamp])
        .range([marginLeft, width - marginRight]) :
        d3.scaleLinear().domain(d3.extent(data, d=>d.acp_ts)).nice()
        .range([marginLeft, width - marginRight]);
  
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d=>d.crowdcount)]).nice()
        .range([height - marginBottom, marginTop]);

    const yCalibratedCo2 = d3.scaleLinear()
        .domain(d3.extent(sensor, s=>s.calibrated_co2)).nice()
        .range([height - marginBottom, marginTop]);

    const yVariance = d3.scaleLinear()
        .domain([0, d3.max(variance, v=>v.variance)]).nice()
        .range([height - marginBottom, marginTop + height/2]);
  
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height + 10])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black; background-color: white; margin:0 0.5vw 0.5vw 0")
        .attr("id", "chart")

    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks((width / 150)).tickFormat(d => d3.timeFormat("%H:%M:%S")(d * 1000)))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick text").style("font-size", "20px"));
    
    svg.append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(d3.axisLeft(y).ticks(d3.min([10, d3.max(data, d=>d.crowdcount)])).tickFormat(d3.format('d')))
    .call(g => g.select(".domain").remove())
    .call(g => g.selectAll(".tick line")
        .clone()
            .attr("x2", width - marginRight - marginLeft)
            .attr("stroke-opacity", d => d === 0 ? 1 : 0.1))
        .call(g => g.selectAll(".tick text")
            .style("font-size", "20px")
    );

    svg.append("g")
    .attr("transform", `translate(${width-marginRight},0)`)
    .call(d3.axisRight(yCalibratedCo2).ticks(5).tickFormat(d3.format('d')))
    .call(g => g.select(".domain").remove())
    .call(g => g.selectAll(".tick text")
            .style("font-size", "20px"))
    
    const crowdCountLine = d3.line()
    .x(d => x(d.acp_ts))
    .y(d => y(d.crowdcount));
    
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "orange")
        .attr("stroke-width", 5)
        .attr("opacity", 0.5)
        .attr("d", crowdCountLine);

    const calibratedCo2Line = d3.line()
        .x(s => x(s.acp_ts))
        .y(s => yCalibratedCo2(s.calibrated_co2));
        
    svg.append("path")
        .datum(sensor)
        .attr("fill", "none")
        .attr("stroke", "blue")
        .attr("stroke-width", 5)
        .attr("opacity", 0.3)
        .attr("d", calibratedCo2Line);

    svg.append("g")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.2)
        .selectAll()
        .data(sensor)
        .join("circle")
        .attr("cx", s => x(s.acp_ts))
        .attr("cy", s => yCalibratedCo2(s.calibrated_co2))
        .attr("r", 2.5);

    const varianceLine = d3.line()
        .x(d => x(d.acp_ts))
        .y(d => yVariance(d.variance));

    svg.append("path")
        .datum(variance)
        .attr("fill", "none")
        .attr("stroke", "blue")
        .attr("stroke-width", 5)
        .attr("opacity", 0.5)
        .attr("d", varianceLine);

    svg.append("g")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.2)
      .selectAll()
      .data(data)
      .join("circle")
        .attr("cx", d => x(d.acp_ts))
        .attr("cy", d => y(d.crowdcount))
        .attr("r", 2.5);

    svg.append("text")
    .attr("x", width / 2)
    .attr("y", height + 2)
    .attr("text-anchor", "middle")
    .attr("font-size", "25px")
    .text("ACP Timestamp (HH:MM:SS)");

    svg.append("text")
    .attr("x", -height / 2)
    .attr("y", 5)
    .attr("text-anchor", "middle")
    .attr("font-size", "25px")
    .attr("transform", "rotate(-90)")
    .text("Crowd Count");

    svg.append("text")
    .attr("x", width - 10)
    .attr("y", height/2)
    .attr("text-anchor", "middle")
    .attr("transform", `rotate(90, ${width - 5}, ${height/2})`)
    .attr("font-size", "20px")
    .text("Calibrated CO2 level");


    svg.append("g")
    .selectAll("line")
    .data(events)
    .join("line")
        .attr("x1", e => x(e.acp_ts))
        .attr("y1", marginTop)
        .attr("x2", e => x(e.acp_ts)) 
        .attr("y2", height - marginBottom)
    .attr("stroke", e=>e.event_type === "lectureUp" ? "green" : "red")
    .attr("stroke-opacity", 0.5)
    .attr("stroke-dasharray", "4,2")
    .attr("stroke-width", 7);

    svg.append("g")
    .attr("stroke", "black")
    .attr("stroke-opacity", 0.5)
    .selectAll("line")
    .data([data[data.length-1]])
    .join("line")
        .attr("x1", e => x(e.acp_ts))
        .attr("y1", height - marginBottom)
        .attr("x2", e => x(e.acp_ts)) 
        .attr("y2", e => y(e.crowdcount));

    svg.append("g")
    .attr("stroke", "black")
    .attr("stroke-opacity", 0.1)
    .selectAll()
    .data(barcodes)
    .join("rect")
        .attr("x", (b) => x(b.start_acp_ts))
        .attr("y", (height - marginBottom) - 150)
        .attr("width", (b) => x(b.end_acp_ts) - x(b.start_acp_ts))
        .attr("height", 150)
        .attr("fill-opacity", 0.5);
    
    svg.append("rect")
        .attr("width", width/15)
        .attr("height", height/5)
        .attr("transform", `translate(${width - width/17.5},${height/40})`)
        .attr("fill", "#eaeaea")
    svg.append("circle").attr("cx", width - width/20).attr("cy",height/20).attr("r", 6).style("fill", "green")
    svg.append("circle").attr("cx", width - width/20).attr("cy",2*height/20).attr("r", 6).style("fill", "red")
    svg.append("circle").attr("cx", width - width/20).attr("cy",3*height/20).attr("r", 6).style("fill", "blue")
    svg.append("circle").attr("cx", width - width/20).attr("cy",4*height/20).attr("r", 6).style("fill", "orange")
    svg.append("text").attr("x", width - width/20 + 15).attr("y", height/20).text("lecture up").style("font-size", "15px").attr("alignment-baseline","middle")
    svg.append("text").attr("x", width - width/20 + 15).attr("y", 2*height/20).text("lecture down").style("font-size", "15px").attr("alignment-baseline","middle")
    svg.append("text").attr("x", width - width/20 + 15).attr("y", 3*height/20).text("co2").style("font-size", "15px").attr("alignment-baseline","middle")
    svg.append("text").attr("x", width - width/20 + 15).attr("y", 4*height/20).text("crowd count").style("font-size", "15px").attr("alignment-baseline","middle")

    return svg.node();
}

export default plotMainGraph