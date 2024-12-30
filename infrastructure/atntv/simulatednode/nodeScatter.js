export const createChart = (data) => {
    console.log("building chart")
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
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;")
        .attr("id", "chart");
  
    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks(width / 80))
        .call(g => g.select(".domain").remove());
  
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y).ticks(d3.max(data, d=>d.crowdcount) - 1).tickFormat(d3.format('d')))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line")
          .clone()
            .attr("x2", width - marginRight - marginLeft)
            .attr("stroke-opacity", d => d === 0 ? 1 : 0.1))
    svg.append("g")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.2)
      .selectAll()
      .data(data)
      .join("circle")
        .attr("cx", d => x(d.acp_ts))
        .attr("cy", d => y(d.crowdcount))
        .attr("r", 2.5);
  
    return svg.node();
}