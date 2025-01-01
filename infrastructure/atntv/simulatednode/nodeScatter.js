export const createChart = (data, events) => {
    const width = 928;
    const height = 600;
    const marginTop = 20;
    const marginRight = 30;
    const marginBottom = 30;
    const marginLeft = 40;
  
    const x = d3.scaleLinear()
        .domain(d3.extent(data, d => d.acp_ts)).nice()
        .range([marginLeft, width - marginRight]);
  
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d=>d.crowdcount)]).nice()
        .range([height - marginBottom, marginTop]);
  
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height + 10])
        .attr("style", "max-width: 100%; height: auto; border:1px solid black;")
        .attr("id", "chart")
  
    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks(width / 80).tickFormat(d=>d3.timeFormat("%H:%M:%S")(d*1000)))
        .call(g => g.select(".domain").remove());
  
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y).ticks(d3.min([50, d3.max(data, d=>d.crowdcount)])).tickFormat(d3.format('d')))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line")
          .clone()
            .attr("x2", width - marginRight - marginLeft)
            .attr("stroke-opacity", d => d === 0 ? 1 : 0.1))
    
    const line = d3.line()
    .x(d => x(d.acp_ts))
    .y(d => y(d.crowdcount));
    
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "orange")
        .attr("stroke-width", 5)
        .attr("opacity", 0.5)
        .attr("d", line);

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
    .attr("y", height + 5)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .text("ACP Timestamp (HH:MM:SS)");

    svg.append("text")
    .attr("x", -height / 2)
    .attr("y", 15)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("transform", "rotate(-90)")
    .text("Crowd Count");

    svg.append("g")
    .attr("stroke", "red")
    .attr("stroke-opacity", 0.5)
    .attr("stroke-dasharray", "4,2")
    .selectAll("line")
    .data(events)
    .join("line")
        .attr("x1", e => x(e.acp_ts))
        .attr("y1", marginTop)
        .attr("x2", e => x(e.acp_ts)) 
        .attr("y2", height - marginBottom);
  
    return svg.node();
}