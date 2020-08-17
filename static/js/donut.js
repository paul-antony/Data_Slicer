function donut(options) {


    var data = options.data,
        container = options.container;


    var width = 400,
        height = 350,
        margin = 20;

    var radius = Math.min(width, height) / 2 - margin

    var color = d3.interpolateHsl("red", "blue")

    var svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var arc = d3.svg.arc()
        .outerRadius(radius)
        .innerRadius(radius * 0.35);

    var pie = d3.layout.pie()
        .sort(null)
        .value(function (d) { return d.value; });

    var g = svg.selectAll(".fan")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "fan")

    g.append("path")
        .attr("d", arc)
        .attr("fill", function (d) { return color(d.data.color); })
        .attr("stroke", "black")
        .style("stroke-width", "1px")
        .style("opacity", 0.9)

    g.append("text")
        .attr("transform", function (d) { return "translate(" + arc.centroid(d) + ")"; })
        .style("text-anchor", "middle")
        .text(function (d) { return d.data.legend; });

}
