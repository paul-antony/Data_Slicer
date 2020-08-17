function dr(options) {

    var data = options.data,
        container = options.container;

    console.log("jack");
    // var element = d3.select(container).node();

    // var width = element.getBoundingClientRect().width;
    // var height = Math.round((1 / 5) * width);

    // var margin = { top: Math.round(width * 0.009), right: Math.round(width * 0.009), bottom: Math.round(width * 0.009), left: Math.round(width * 0.009) };

    var width = 940,
        height = 200;

        var margin = { top: 20, right: 20, bottom: 20, left: 20 };

    var svg = d3.select(container).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var x = d3.scale.linear()
        .domain([0, d3.min([1, d3.max(data, function(d) { return d.x; })])])
        .range([0, width]);


    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");


    var y = d3.scale.linear()
        .domain([0, d3.max(data, function(d) { return d.y; })])
        .range([height / 2, 0]);



    var area = d3.svg.area()
        .x(function(d) { return x(d.x); })
        .y0(function(d) { return y(-d.y); })
        .y1(function(d) { return y(d.y); })
        .interpolate('basis');



    svg.append("path")
        .datum(data)
        .attr("fill", "#cce5df")
        .attr("stroke", "#69b3a2")
        .attr("stroke-width", 1.5)
        .attr("class", "area")
        .attr("d", area);


    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height / 2 + ")")
        .call(xAxis);


}