var username = VMStorage.username;
var password = VMStorage.password;
var authURL = "https://qualysapi.qg2.apps.qualys.eu/api/2.0/fo/session/";
var authURLReport = "https://qualysapi.qg2.apps.qualys.eu/api/2.0/fo/report/";
// Save the CSV content to an existing spreadsheet and create a new sheet; Sheet listed below = Copy of BMI Server Top Vulns
var spreadsheet = SpreadsheetApp.openByUrl("PLACEHOLDER URL");

function startSession() {
  var options = {
    "method": "POST",
    "payload": {
      "action": "login",
      "username": username,
      "password": password
    },
    "headers": {
      "X-Requested-With": "Google Apps Script",
      "Content-Type": "application/x-www-form-urlencoded"
    },
    "muteHttpExceptions": true
  }

  // Creating a bunch of stand-in variables
  // Response + contents isolated + headers isolated + cookies isolated + a placeholder for sessionID
  var response = UrlFetchApp.fetch(authURL, options);
  var responseContent = response.getContentText();
  var responseHeaders = response.getAllHeaders();
  var responseCookies = responseHeaders["Set-Cookie"];
  var responseID;

  // Isolate out the sessionID from the cookies in the response header
  if (responseCookies != null) {
    for (var i = 0; i < responseCookies.length; i++) {
      var cookie = responseCookies[i];
      if (cookie.indexOf("QualysSession=") != -1) {
        responseID = "QualysSession=" + cookie.substring(cookie.indexOf('=') + 1, cookie.indexOf(';'));
        break;
      }
    }
  }

  // Print out response code to see if the request was successful or not
  // Does not necessarily mean auth succeeded, check the responseContent values
  if (response.getResponseCode() === 200) {
  Logger.log("HTTP 200 - Qualys Authentication Successful");
  } 
  else {
    Logger.log("Authentication failed. Response code: " + response.getResponseCode());
  }

  // For troubleshooting
  Logger.log(responseContent);
  Logger.log(responseHeaders);
  Logger.log("Session ID: " + responseID);

  return responseID;
}

function killSession(sessionID) {
  // Difference: providing sessionID in header instead of user/pass in payload
  var options = {
    "method": "POST",
    "payload": {
      "action": "logout"
    },
    "headers": {
      "X-Requested-With": "Google Apps Script",
      "Content-Type": "application/x-www-form-urlencoded",
      "Cookie": sessionID
    },
    "muteHttpExceptions": true
  }

  var response = UrlFetchApp.fetch(authURL, options);
  var responseContent = response.getContentText();
  var responseHeaders = response.getAllHeaders();

  if (response.getResponseCode() === 200) {
  Logger.log("HTTP 200 - Logout successful.");
  } 
  else {
    Logger.log("Logout failed. Response code: " + response.getResponseCode());
  }

  Logger.log(responseContent);
  Logger.log(responseHeaders);

  return;
}

function listReport(sessionID) {
  var options = {
    "method": "POST",
    "payload": {
      "action": "list"
    },
    "headers": {
      "X-Requested-With": "Google Apps Script",
      "Content-Type": "application/x-www-form-urlencoded",
      "Cookie": sessionID
    },
    "muteHttpExceptions": true
  }

  var response = UrlFetchApp.fetch(authURLReport, options);
  var responseContent = response.getContentText();

  var regexTitle = /<TITLE><!\[CDATA\[(.*?)\]\]><\/TITLE>/g;
  var reportNames = [];
  var match;
  while ((match = regexTitle.exec(responseContent)) !== null) {
    reportNames.push(match[1]);
  }

  var regexID = /<ID>(\d{7,9})<\/ID>/g;
  var reportIds = [];
  var returnReport;
  var match2;
  while ((match2 = regexID.exec(responseContent)) !== null) {
    reportIds.push(match2[1]);
  }

  Logger.log("List of available reports:\n");
  for (var i = 0; i < reportNames.length; i++) {
    var report = reportNames[i];
    var reportId = reportIds[i];
    if (report === "REPORT NAME HERE") {
      returnReport = reportId;
      break;
    }
  }

  return returnReport;
}

function downloadReport(sessionID, targetReport) {

  options = {
    "method": "POST",
    "headers": {
      "X-Requested-With": "Google Apps Script",
      "Content-Type": "application/x-www-form-urlencoded",
      "Cookie": sessionID
    },
    "payload": {
      "action": "fetch",
      "id": targetReport
    },
    "muteHttpExceptions": true
  }

  response = UrlFetchApp.fetch(authURLReport, options);
  var csvContent = response.getContentText();

  var today = new Date();
  var month = today.getMonth() + 1; // add 1 to get the month value from 1 to 12
  var day = today.getDate();
  var year = today.getFullYear().toString().substr(-2); // get the last two digits of the year

  var sheetName = "Vulnerability Details (" + month + "/" + day + "/" + year + ")";
  var returnName = month + "/" + day + "/" + year;
  var sheet = spreadsheet.insertSheet(3);
  sheet.setName(sheetName);

  // Parse the CSV data and set it to the sheet
  var data = Utilities.parseCsv(csvContent);
  sheet.getRange(1, 1, data.length, data[0].length).setValues(data);

  Logger.log(returnName);
  return returnName;
}

function updateCheckpointColumnsChild(sheetName, updateText) {
  // Get the last column of the sheet
  var overviewSheet = spreadsheet.getSheetByName(sheetName);
  var lastColumn = overviewSheet.getLastColumn();

  // Calculate the column index of the leading column, which is 4 columns to the left of the last column
  var leadingColumnIndex = lastColumn - 3;

  // Insert a new column to the left of the leading column
  overviewSheet.insertColumnBefore(leadingColumnIndex);

  // Increment leading column index and last column index by 1 since we just inserted a new row
  lastColumn = lastColumn + 1;
  leadingColumnIndex = leadingColumnIndex + 1;

  // Copy values from the leading column to the newly inserted column
  var rangeToCopy = overviewSheet.getRange(1, leadingColumnIndex, overviewSheet.getLastRow(), 1);
  var destinationRange = overviewSheet.getRange(1, leadingColumnIndex - 1);
  rangeToCopy.copyTo(destinationRange, {contentsOnly:true});

  // Clear the sheet's conditional format rules
  overviewSheet.clearConditionalFormatRules();

  // New range from row 3
  var newColumnRange = overviewSheet.getRange(3, leadingColumnIndex, overviewSheet.getLastRow(), 1);

  // Recreate new rules w/ updated ranges
  var progressFormula1 = "=INDIRECT(ADDRESS(ROW(), COLUMN()-1))>INDIRECT(ADDRESS(ROW(), COLUMN()))"; //greater than
  var progressFormula2 = "=INDIRECT(ADDRESS(ROW(), COLUMN()-1))<INDIRECT(ADDRESS(ROW(), COLUMN()))"; //less than
  var progressFormula3 = "=AND(ISNUMBER(INDIRECT(ADDRESS(ROW(), COLUMN()-1))), ISNUMBER(INDIRECT(ADDRESS(ROW(), COLUMN()))), INDIRECT(ADDRESS(ROW(), COLUMN()-1))=0, INDIRECT(ADDRESS(ROW(), COLUMN()))=0)"; //equal to zero

  // Create new rules with the formula and set its formatting
  var rule1 = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(progressFormula1)
    .setBackground("#d9ead3")
    .setRanges([newColumnRange])
    .build();

  var rule2 = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(progressFormula2)
    .setBackground("#f4cccc")
    .setRanges([newColumnRange])
    .build(); 

  var rule3 = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(progressFormula3)
    .setBackground("#93c47d")
    .setRanges([newColumnRange])
    .build();

  // Apply the new rule to the sheet
  var rules = overviewSheet.getConditionalFormatRules();
  rules.push(rule1,rule2,rule3);
  overviewSheet.setConditionalFormatRules(rules);

  //Hide older column
  overviewSheet.hideColumns(leadingColumnIndex - 3);

  // Get a reference to the cells we want to set the value in (1st row, 2nd column)
  var detailsDate1 = overviewSheet.getRange(1, 1);
  var detailsDate2 = overviewSheet.getRange(2, leadingColumnIndex);

  // Set the value of the cell to the text entered by the user
  detailsDate1.setValue('Vulnerability Details (' + updateText + ')');
  detailsDate2.setValue(updateText);
}

function formatNewSheet(updateText) {
  Logger.log("Beginning of format: " + updateText);
  var sheet = spreadsheet.getSheetByName("Vulnerability Details (" + updateText + ")");
  var data = sheet.getDataRange().getValues();
  var rowsToDelete = [];

  for (var i = 0; i < data.length; i++) {
    if (data[i][0] === "IP") { // If row w/ "IP" is found, end loop
      break;
    }
    else {
      rowsToDelete.push(i+1); // Add the row number (1 - indexed) to the array
    }
  }

  // Delete the rows in reverse so that the indexing doesn't get messed up
  for (var i = rowsToDelete.length - 1; i >= 0; i--) {
    sheet.deleteRow(rowsToDelete[i]);
  }

  // Create a filter across the top row
  var range = sheet.getDataRange();
  range.createFilter();

  Logger.log("Filter created");

  // Format all rows to be 21 pixels
  var numRows = sheet.getMaxRows();
  sheet.setRowHeightsForced(1, numRows, 21);

  Logger.log("Ending of format: " + updateText);
  return;
}

function main() {
  var sessionID = startSession(); // Authenticate
  var targetReport = listReport(sessionID); // Find BMI Server report, return report ID
  var updateText = downloadReport(sessionID, targetReport); // Download server report based on supplied report ID
  killSession(sessionID); // De-authenticate

  formatNewSheet(updateText);
  updateCheckpointColumnsChild("Linux Overview", updateText);
  updateCheckpointColumnsChild("Windows Overview", updateText);
  updateCheckpointColumnsChild("Remediated", updateText);
}
