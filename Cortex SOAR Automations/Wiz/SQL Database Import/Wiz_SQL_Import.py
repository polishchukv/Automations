import csv
import demisto_sdk as demisto
import pandas as pd

class DataImporter:
    def __init__(self):
        self.debug_log = []

    def add_debug_log(self, log):
        demisto.debug(log)
        self.debug_log.append(log)

    def fetch_args(self):
        self.args = demisto.args()
        self.tableName = self.args['dbTable']
        self.fileLocation = None

    def remove_table(self):
        try:
            demisto.executeCommand('asset-query-sql', {'query': f'DROP TABLE IF EXISTS {self.tableName}'})
            self.add_debug_log(f'Table {self.tableName} dropped.')
        except Exception as e:
            self.add_debug_log(f'Failed to drop table {self.tableName}. Error: {str(e)}')

    def process_entry_id(self):
        if self.args.get('entryId'):
            self.entryId = self.args['entryId']
            res = demisto.executeCommand('getFilePath', {'id': self.entryId})
            self.add_debug_log(f'getFilePath response for entryId {self.entryId}: {res}')
            try:
                self.fileLocation = res[0]['Contents']['path']
                self.add_debug_log(f'File path retrieved: {self.fileLocation}')
            except KeyError as e:
                self.add_debug_log(f'Failed to retrieve file path from getFilePath response. Error: {str(e)} - res: {res}')
                demisto.return_error('File was not found.')

    def process_file_extension(self):
        try:
            extension = res[0]['Contents']['name'].split('.')[-1]
            if extension != 'csv' and extension != 'xlsx':
                self.add_debug_log(f'File extension is not supported: {extension}')
                return 'File type not supported.'
            if extension == 'xlsx':
                newFile = pd.read_excel(self.fileLocation)
                csvOutput = newFile.to_csv(index=False)
                with open('table.csv', 'w') as csv:
                    csv.write(csvOutput)
                self.fileLocation = 'table.csv'
                self.add_debug_log(f'Converted xlsx file to csv: {self.fileLocation}')
        except KeyError as e:
            self.add_debug_log(f'KeyError in file handling: {str(e)} - res: {res}')
            pass

    def open_file(self):
        with open(self.fileLocation, 'r') as f:
            tempList = f.readlines()
        self.initialData = tempList
        self.add_debug_log(f'Initial data read within tempList length: {len(tempList)}')
        self.header = tempList[0].replace(' ','').replace('/','_').replace('(CONTAINER|CONTAINER_IMAGE|SERVERLESS|VIRTUAL_MACHINE)', 'TECHNINSTANCE').replace('(','').replace(')','').replace('.','').replace('|','_')

    def process_wiz_report(self):
        if self.args.get('wizReport'):
            self.reportId = self.args['wizReport']
            self.add_debug_log(f'Fetching report with ID: {self.reportId}')
            try:
                res = demisto.executeCommand('wiz-download-report', {'reportId': self.reportId, 'csv': 'no'})
                self.add_debug_log('Response from wiz-download-report: ' + str(res))
                if not res or not res[0].get('Contents'):
                    self.add_debug_log('Failed to download report. No content found for given report ID')
                    return 'Failed to download report. No content found for given report ID'
                self.report = res[0]['Contents']
                self.add_debug_log(f'Initial report contents: {self.report[:100]}...')
                if self.report:
                    self.process_report_content()
                else:
                    demisto.return_error('Error: Report content is empty of malformed.')
            except Exception as e:
                self.add_debug_log(f'Exception occurred: {str(e)}')
                demisto.return_error(f'An error occurred while processing the wizReport: {str(e)}')

    def process_report_content(self):
        headerRaw = self.report.split('\n')[0]
        self.add_debug_log(f'Header raw: {headerRaw}')
        self.header = headerRaw.replace('(','').replace(')','').replace(' ','').replace('.','').replace('|','_')
        self.add_debug_log(f'Header cleaned: {self.header}')
        self.report = self.report.replace(headerRaw, self.header)
        self.initialData = self.report.split('\n')[1:]
        self.add_debug_log(f'Initial data split {self.initialData[:5]}...')
        reportListBytes = self.report.encode('utf-8')
        file_content = reportListBytes
        demisto.return_results(fileResult('table.csv', file_content))
        contextRes = demisto.executeCommand('GetContextValue', {'key': 'File'})
        self.add_debug_log(f'contextRes: {contextRes}')
        if not contextRes or not contextRes[0].get('Contents'):
            self.add_debug_log('Failed to get file context')
            return 'Failed to get file context'
        self.entryId = contextRes[0]['Contents'].get('entryID')
        self.add_debug_log(f'Retrieved entryId: {self.entryId}')
        if not self.entryId:
            demisto.return_error('Error: EntryID was not found in context value.')
        res = demisto.executeCommand('getFilePath', {'id': self.entryId})
        self.add_debug_log(f'getFilePath response for entryId {self.entryId}: {res}')
        try:
            self.fileLocation = res[0]['Contents']['path']
            self.add_debug_log(f'File path retrieved from context: {self.fileLocation}')
        except KeyError as e:
            self.add_debug_log(f'KeyError in retrieving file path: {str(e)} - res: {res}')
            demisto.return_error('File was not found.')

    def save_file(self):
        with open(self.fileLocation, 'w') as f2:
            for line in self.initialData:
                line = line.replace('<br>', '\\n').replace('\\','')
                if self.args.get('newField'):
                    newField = self.args['newField']
                    line = line.rstrip() + ',' + newField
                f2.write(line)
            self.add_debug_log(f'Processed initial data and wrote to file: {self.fileLocation}')

    def build_table(self):
        self.queryHeader = self.header.replace(',',' varchar(255),') + ' varchar(255)'
        self.createQuery = f'CREATE TABLE {self.tableName} ({self.queryHeader})'
        try:
            demisto.executeCommand('asset-query-sql', {'query': self.createQuery})
            self.add_debug_log(f'Created table {self.tableName} with header {self.queryHeader}')
        except Exception as e:
            self.add_debug_log(f'Exception in creating table: {str(e)}')
            if self.args.get('append') == 'no' and not self.args.get('newField'):
                try:
                    demisto.executeCommand('asset-query-sql', {'query': f'TRUNCATE TABLE {self.tableName}'})
                    self.add_debug_log(f'Truncated table {self.tableName}')
                except Exception as e:
                    self.add_debug_log(f'Exception in truncating table: {str(e)}')
                    demisto.return_error(f'Failed to truncate table {self.tableName}. Error: {str(e)}')

    def import_data(self):
        self.query = f'''
        LOAD DATA LOCAL INFILE '{self.fileLocation}'
        INTO TABLE {self.tableName}
        FIELDS TERMINATED BY ','
        ENCLOSED BY '"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS;
        '''
        try:
            demisto.executeCommand('asset-query-sql', {'query': 'SET GLOBAL local_infile = 1'})
            self.add_debug_log('Enabled local_infile for SQL')
        except Exception as e:
            self.add_debug_log(f'Failed to enable local_infile: {str(e)}')
        try:
            demisto.executeCommand('asset-query-sql', {'query': self.query})
            self.add_debug_log(f'Updated table {self.tableName} with data from {self.fileLocation}')
        except Exception as e:
            self.add_debug_log(f'Failed to update table {self.tableName}. Error: {str(e)}')
            demisto.return_error(f'Failed to update table {self.tableName}. Error: {str(e)}')

    def record_count(self):
        self.totalRecords = demisto.executeCommand('asset-query-sql', {'query': f'SELECT COUNT(*) FROM {self.tableName}'})
        self.add_debug_log(f'Total records in table {self.tableName}: {self.totalRecords}')
        try:
            self.total = self.totalRecords[0]['Contents'][0]
            self.add_debug_log(f'Total records in table {self.tableName}: {self.total}')
        except Exception as e:
            self.add_debug_log(f'Failed to get total records: {str(e)}')
            self.total= 'Uknown'

    def output_results(self):
        final_message = f'Table {self.tableName} has been updated with {self.total} records.'
        self.debug_log.append(final_message)
        demisto.return_results('\n'.join(self.debug_log))

    def execute(self):
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