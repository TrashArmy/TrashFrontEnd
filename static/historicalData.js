// https://bl.ocks.org/pstuffa/26363646c478b2028d36e7274cedefa6
function loadSVG(elementId, data) {
console.log("ELEMENT" + elementId)
// 2. Use the margin convention practice 
var margin = {top: 5, right: window.innerWidth*.15, bottom: 70, left: window.innerWidth*.15}
  , width = window.innerWidth - margin.left - margin.right // Use the window's width 
  , height = window.innerHeight/2 - margin.top - margin.bottom; // Use the window's height

//parse data to make it easy to use
var jsonData = JSON.parse(data);
for(var i = 0; i < jsonData.length; i++) {
    jsonData[i].date = new Date(jsonData[i].date);
    jsonData[i].fill = parseInt(jsonData[i].fill);
}
// console.log(jsonData)

//calculate min and max fill level on graph
var max = -1000000000000
var min = 10000000000
if (jsonData.length <= 1) {
    min = 0;
    max = 100;
} else {
    for(var i = 0; i < jsonData.length; i++) {
        if(jsonData[i].fill > max) {
            max = jsonData[i].fill;
        }
        if(jsonData[i].fill < min) {
            min = jsonData[i].fill;
        }
    }
}
// console.log("Min " + min)
// console.log("Max " + max)
//calculate min and max date on graph

var minDate = new Date();
var maxDate = new Date();
if(jsonData.length == 1) {
    minDate = jsonData[0].date;
    maxDate.setDate(maxDate.getDate() + 7)
} else if(jsonData.length == 0) {
    maxDate.setDate(maxDate.getDate() + 7)
} else {
    minDate = jsonData[0].date;
    maxDate = jsonData[jsonData.length-1].date;
}
// console.log("Min date " + minDate)
// console.log("Max date " + maxDate)

// 5. X scale will use the index of our data
var xScale = d3.scaleTime()
    .domain([minDate, maxDate]) // input 
    .range([0, width]); 


// 6. Y scale will use the randomly generate number 

var yScale = d3.scaleLinear()
    .domain([min, max]) // input 
    .range([height, 0]);  

// 7. d3's line generator
var line = d3.line()
    .x(function(d) { return xScale(d.date); }) // set the x values for the line generator
    .y(function(d) { return yScale(d.fill); }) // set the y values for the line generator 
    .curve(d3.curveMonotoneX) // apply smoothing to the line

// 1. Add the SVG to the page and employ #2
var svg = d3.select(elementId).append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


// 3. Call the x axis in a group tag
svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat("%m/%d\n%H:%M")))
    .selectAll("text")
    .attr("y", 0)
    .attr("x", 9)
    .attr("dy", ".35em")
    .attr("transform", "rotate(80)")
    .style("text-anchor", "start"); // Create an axis component with d3.axisBottom

svg.append("g")
  .attr("class", "x axis")
  .selectAll('.x .tick text') // select all the x tick texts
  .call(function(t){                
    t.each(function(d){ // for each one
      var self = d3.select(this);
      var s = self.text().split(' ');  // get the text and split it
      self.text(''); // clear it out
      self.append("tspan") // insert two tspans
        .attr("x", 0)
        .attr("dy",".8em")
        .text(s[0]);
      self.append("tspan")
        .attr("x", 0)
        .attr("dy",".8em")
        .text(s[1]);
    })
});
// 4. Call the y axis in a group tag
svg.append("g")
    .attr("class", "y axis")
    .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

// 9. Append the path, bind the data, and call the line generator 
svg.append("path")
    .datum(jsonData) // 10. Binds data to the line 
    .attr("class", "line") // Assign a class for styling 
    .attr("d", line); // 11. Calls the line generator 

//12. Appends a circle for each datapoint 
svg.selectAll(".dot")
    .data(jsonData)
    .enter().append("circle") // Uses the enter().append() method
    .attr("class", "dot") // Assign a class for styling
    .attr("cx", function(d) { return xScale(d.date) })
    .attr("cy", function(d) { return yScale(d.fill) })
    .attr("r", 5);
}