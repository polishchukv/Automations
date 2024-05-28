import csv
import demisto_sdk as demisto
import pandas as pd
import os

class DataImporter:
    """
    Class to handle the import of data from CSV or Excel files into a SQL table.
    """
    def __init__(self):
        self.debug_log = []

    def add_debug_log(self, log):
        """
        Adds a log entry to the debug log and uses demisto to log the message.
        """
        demisto.debug(log)
        self.debug_log.append(log)

    def fetch_args(self):
        """
        Fetches arguments from demisto and initializes necessary variables.
        """
        self.args = demisto.args()
        self.tableName = self.args.get('dbTable')
        self.fileLocation = None

    def remove_table(self):
        """
        Drops the existing SQL table if it exists.
        """
        try:
            demisto.executeCommand('asset-query-sql', {'query': f'DROP TABLE IF EXISTS {self.tableName}'})
            self.add_debug_log(f'Table {self.tableName} dropped.')
        except Exception as e:
            self.add_debug_log(f'Failed to drop table {self.tableName}. Error: {str(e)}')

    def process_entry_id(self):
        """
        Processes the entry ID to get the file path.
        """
        if self.args.get('entryId'):
            self.entryId = self.args['entryId']
            res = demisto.executeCommand('getFilePath', {'id': self.entryId})
            self.add_debug_log('getFilePath response for entryId received.')
            try:
                self.fileLocation = res[0]['Contents']['path']
                self.add_debug_log('File path retrieved successfully.')
            except KeyError as e:
                self.add_debug_log('Failed to retrieve file path from getFilePath response.')
                demisto.return_error('File was not found.')

    def process_file_extension(self):
        """
        Checks the file extension and processes accordingly.
        """
        try:
            extension = res[0]['Contents']['name'].split('.')[-1]
            if extension not in ['csv', 'xlsx']:
                self.add_debug_log(f'Unsupported file extension: {extension}')
                return 'File type not supported.'
            if extension == 'xlsx':
                newFile = pd.read_excel(self.fileLocation)
                csvOutput = newFile.to_csv(index=False)
                with open('table.csv', 'w') as csv_file:
                    csv_file.write(csvOutput)
                self.fileLocation = 'table.csv'
        except Exception as e:
            self.add_debug_log(f'Error processing file extension: {str(e)}')
            demisto.return_error('Error processing file extension.')

    def open_file(self):
        """
        Opens the CSV file for reading.
        """
        try:
            with open(self.fileLocation, 'r') as file:
                self.csvData = csv.reader(file)
                self.add_debug_log('CSV file opened successfully.')
        except Exception as e:
            self.add_debug_log(f'Failed to open file: {str(e)}')
            demisto.return_error('Failed to open file.')

    def process_wiz_report(self):
        """
        Processes the Wiz report data.
        """
        try:
            self.processedData = [row for row in self.csvData]
            self.add_debug_log('Wiz report processed successfully.')
        except Exception as e:
            self.add_debug_log(f'Error processing Wiz report: {str(e)}')
            demisto.return_error('Error processing Wiz report.')

    def save_file(self):
        """
        Saves the processed data to a CSV file.
        """
        try:
            with open('processed_data.csv', 'w') as file:
                writer = csv.writer(file)
                writer.writerows(self.processedData)
                self.fileLocation = 'processed_data.csv'
                self.add_debug_log('Processed data saved to CSV file.')
        except Exception as e:
            self.add_debug_log(f'Failed to save processed data: {str(e)}')
            demisto.return_error('Failed to save processed data.')

    def build_table(self):
        """
        Builds the SQL table structure.
        """
        try:
            table_schema = self.get_table_schema()
            demisto.executeCommand('asset-query-sql', {'query': table_schema})
            self.add_debug_log(f'Table {self.tableName} schema created.')
        except Exception as e:
            self.add_debug_log(f'Failed to create table schema: {str(e)}')
            demisto.return_error('Failed to create table schema.')

    def import_data(self):
        """
        Imports data into the SQL table.
        """
        try:
            demisto.executeCommand('asset-query-sql', {'query': 'SET GLOBAL local_infile = 1'})
            self.add_debug_log('Enabled local_infile for SQL.')
        except Exception as e:
            self.add_debug_log(f'Failed to enable local_infile: {str(e)}')
        try:
            import_query = f"""
                LOAD DATA LOCAL INFILE '{self.fileLocation}'
                INTO TABLE {self.tableName}
                FIELDS TERMINATED BY ','
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                IGNORE 1 ROWS;
            """
            demisto.executeCommand('asset-query-sql', {'query': import_query})
            self.add_debug_log(f'Updated table {self.tableName} with data from {self.fileLocation}.')
        except Exception as e:
            self.add_debug_log(f'Failed to update table {self.tableName}. Error: {str(e)}')
            demisto.return_error(f'Failed to update table {self.tableName}. Error: {str(e)}')

    def record_count(self):
        """
        Counts the total number of records in the SQL table.
        """
        try:
            self.totalRecords = demisto.executeCommand('asset-query-sql', {'query': f'SELECT COUNT(*) FROM {self.tableName}'})
            self.total = self.totalRecords[0]['Contents'][0]
            self.add_debug_log(f'Total records in table {self.tableName}: {self.total}')
        except Exception as e:
            self.add_debug_log(f'Failed to get total records: {str(e)}')
            self.total = 'Unknown'

    def output_results(self):
        """
        Outputs the final results and logs.
        """
        final_message = f'Table {self.tableName} has been updated with {self.total} records.'
        self.debug_log.append(final_message)
        demisto.return_results('\n'.join(self.debug_log))

    def execute(self):
        """
        Executes the data import process.
        """
        self.fetch_args()
        self.remove_table()
        self.process_entry_id()
        self.process_file_extension()
        self.open_file()
        self.process_wiz_report()
        self.save_file()
        self.build_table()
        self.import_data()
        self.record_count()
        self.output_results()

if __name__ in ('__main__', '__builtin__', 'builtins'):
    dataImporter = DataImporter()
    dataImporter.execute()
