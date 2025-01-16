const plotMainGraph = (data, events, barcodes, variance, piePercent, height, width, startTime, endTime, day) => {
    const radius = Math.min(width, height) / 8;
    const piePercentObjArr = [{value: piePercent}, {value: 100 - piePercent}];

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

    const x = d3.scaleLinear()
        .domain([startTimeStamp, endTimeStamp])
        .range([marginLeft, width - marginRight]);
  
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d=>d.crowdcount)]).nice()
        .range([height - marginBottom, marginTop]);

    const yVariance = d3.scaleLinear()
        .domain([0, d3.max(variance, v=>v.variance)]).nice()
        .range([height - marginBottom, marginTop + height/2]);
  
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height + 10])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black;")
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

    svg.append("g")
    .attr("stroke", "red")
    .attr("stroke-opacity", 0.5)
    .attr("stroke-dasharray", "4,2")
    .attr("stroke-width", 4)
    .selectAll("line")
    .data(events)
    .join("line")
        .attr("x1", e => x(e.acp_ts))
        .attr("y1", marginTop)
        .attr("x2", e => x(e.acp_ts)) 
        .attr("y2", height - marginBottom);

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
    
    const pieGroup = svg.append("g")
    .attr("transform", `translate(${width - radius - 10}, ${radius + 10})`);

    const pie = d3.pie().value(d => d.value);
    const arc = d3.arc()
        .innerRadius(0)
        .outerRadius(radius);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const arcs = pieGroup.selectAll("arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc");
    
    arcs.append("path")
        .attr("d", arc)
        .attr("fill", (d, i) => color(i));
    
    arcs.append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("text-anchor", "middle")
        .text(d => d.data.label);
  
    return svg.node();
}

export default plotMainGraph