export const createChart = () => {
    const width = 928;
    const height = 600;
    const marginTop = 20;
    const marginRight = 30;
    const marginBottom = 30;
    const marginLeft = 40;
  
    const x = d3.scaleUtc()
        .domain(d3.extent(data, d => d.date))
        .range([marginLeft, width - marginRight]);
  
    const y = d3.scaleLinear()
        .domain(d3.extent(data, d => d.value)).nice()
        .range([height - marginBottom, marginTop]);
  
    const max = d3.max(data, d => Math.abs(d.value));
  
    // Create a symmetric diverging color scale.
    const color = d3.scaleSequential()
        .domain([max, -max])
        .interpolator(d3.interpolateRdBu);
  
    const svg = d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", [0, 0, width, height])
        .attr("style", "max-width: 100%; height: auto;");
  
    svg.append("g")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(d3.axisBottom(x).ticks(width / 80))
        .call(g => g.select(".domain").remove());
  
    svg.append("g")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y).ticks(null, "+"))
        .call(g => g.select(".domain").remove())
        .call(g => g.selectAll(".tick line")
          .clone()
            .attr("x2", width - marginRight - marginLeft)
            .attr("stroke-opacity", d => d === 0 ? 1 : 0.1))
        .call(g => g.append("text")
            .attr("fill", "#000")
            .attr("x", 5)
            .attr("y", marginTop)
            .attr("dy", "0.32em")
            .attr("text-anchor", "start")
            .attr("font-weight", "bold")
            .text("Anomaly (°C)"));
  
    svg.append("g")
        .attr("stroke", "#000")
        .attr("stroke-opacity", 0.2)
      .selectAll()
      .data(data)
      .join("circle")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.value))
        .attr("fill", d => color(d.value))
        .attr("r", 2.5);
  
    return svg.node();
}