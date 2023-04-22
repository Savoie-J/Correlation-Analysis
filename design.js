function onEdit(e) {
  var sheet = e.range.getSheet();
  if (sheet.getName() !== "Display") return;
  if (e.range.getA1Notation() !== "C1" && e.range.getA1Notation() !== "D1") return;
  changeSeriesColor();
}

function changeSeriesColor() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = "Display"; // Replace with the name of your sheet
  var sheet = ss.getSheetByName(sheetName);
  var chart = sheet.getCharts()[0];
  
  // Get color of cell C1
  var color1 = sheet.getRange("C1").getBackground();
  //Logger.log("Color of C1: " + color1);
  
  // Get color of cell D1
  var color2 = sheet.getRange("D1").getBackground();
  //Logger.log("Color of D1: " + color2);
  
  // Set options for both series with their respective colors
  var options = {
    'series': {
      0: { 'color': color1 },
      1: { 'color': color2 }
    },
    'minorGridlines': { 'color': 'transparent' }
  };
  
  // Modify and update the chart with new series colors
  chart = chart.modify()
               .setOption('series', options.series)
               .setOption('minorGridlines', options.minorGridlines)
               .build();
  sheet.updateChart(chart);
}

function onOpen() {
  PropertiesService.getScriptProperties().setProperty("sheetName", JSON.stringify(SpreadsheetApp.getActiveSpreadsheet().getSheets().map(s => s.getSheetName())));
}

function installedOnChange(e) {
  const lock = LockService.getDocumentLock();
  if (lock.tryLock(350000)) {
    try {
      if (!e || e.changeType !== "INSERT_GRID") return;
      const sheetNames = JSON.parse(PropertiesService.getScriptProperties().getProperty("sheetName"));
      e.source.getSheets().forEach(s => {
        if (!sheetNames.includes(s.getSheetName())) e.source.deleteSheet(s);
      });
    } catch (e) {
      throw new Error(JSON.stringify(e));
    } finally {
      lock.releaseLock();
    }
  } else {
    throw new Error("timeout");
  }
}