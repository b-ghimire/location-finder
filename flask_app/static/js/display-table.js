function displayTable(data, columns, marginLeft, panelID) {

    // removing old table, if it exists
    d3.select(panelID)
      .selectAll("table")
      .remove();

    var table = d3.select(panelID).append("table")
            .attr("style", marginLeft);

    thead = table.append("thead");
    tbody = table.append("tbody");

    // append the header row
    thead.append("tr")
        .selectAll("th")
        .data(columns)
        .enter()
        .append("th")
            .text(function(column) { return column; });

    // create a row for each object in the data
    var rows = tbody.selectAll("tr")
        .data(data)
        .enter()
        .append("tr");

    // create a cell in each row for each column
    var cells = rows.selectAll("td")
        .data(function(row) {
            return columns.map(function(column) {
                return {column: column, value: row[column]};
            });
        })
        .enter()
        .append("td")
        .attr("style", "font-family: Courier")
        .attr("style", "font-size: 1em")
            .html(function(d) { return d.value; });

    return table;
}
