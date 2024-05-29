import base64
import csv
import io
import sys
import re
from operator import itemgetter
import demisto_sdk as demisto
import xlsxwriter
import os

class QueryHelper:
    """
    Helper class to handle CrowdStrike and ServiceNow queries.
    """
    FIELD_MAPPING = {
        'inbound_relations': 'Inbound Relations',
        'outbound_relations': 'Outbound Relations'
    }

    ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    def __init__(self):
        # Initialize sets and lists to store results and checked items
        self.checked_items = set()
        self.crowdstrike_results = []
        self.crowdstrike_not_found = []
        self.servicenow_results = []
        self.servicenow_not_found = []
        # Read instance name from environment variable or configuration file
        self.servicenow_instance = os.getenv('SERVICENOW_INSTANCE', 'default_instance')

    def cs_query_helper(self, filter_key, filter_value):
        """
        Queries CrowdStrike Falcon for devices based on the filter key and value.
        Appends results to crowdstrike_results if found, otherwise appends to crowdstrike_not_found.
        """
        found = False
        response = demisto.executeCommand('cs-falcon-search-device', {'filter': f'{filter_key}:"{filter_value}"'})
        for res in response:
            if 'resources' in res['Contents']:
                found = True
                try:
                    self.crowdstrike_results.append(res['Contents']['resources'][0])
                except (KeyError, TypeError, IndexError):
                    continue
        return found

    def snow_query_helper(self, filter_key, filter_value):
        """
        Queries ServiceNow CMDB for records based on the filter key and value.
        Appends results to servicenow_results if found, otherwise appends to servicenow_not_found.
        """
        found = False
        snow_response = demisto.executeCommand('servicenow-cmdb-records-list', {
            'class': 'cmdb_ci',
            'limit': 20,
            'query': f'{filter_key}LIKE{filter_value}',
            'using': self.servicenow_instance
        })
        try:
            detailed_results = demisto.executeCommand('servicenow-cmdb-record-get-by-id', {
                'class': 'cmdb_ci',
                'sys_id': snow_response[0]['Contents']['result'][0]['sys_id'],
                'using': self.servicenow_instance
            })
            demisto.log(f'Queried {filter_value}! Results found.')
            for result in detailed_results:
                self.servicenow_results.append(result)
                found = True
        except (KeyError, TypeError, IndexError):
            pass
        return found

    def query_crowdstrike(self, data_list):
        """
        Iterates through the data_list and performs CrowdStrike queries for each item.
        Filters items based on the IP pattern.
        """
        for item in data_list:
            if self.ip_pattern.match(item):
                if item not in self.checked_items:
                    self.checked_items.add(item)
                    if not self.cs_query_helper('external_ip', item):
                        self.crowdstrike_not_found.append({'Data': item})

    def query_servicenow(self, data_list):
        """
        Iterates through the data_list and performs ServiceNow queries for each item.
        """
        for item in data_list:
            if item not in self.checked_items:
                self.checked_items.add(item)
                if not self.snow_query_helper('ip_address', item):
                    self.servicenow_not_found.append({'Data': item})

    @staticmethod
    def generate_csv(filename, data):
        """
        Generates a CSV file from the given data and returns it as a string.
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()


class MainApp:
    """
    Main application class to orchestrate the data processing and querying.
    """
    def __init__(self):
        # Initialize the QueryHelper instance
        self.helper = QueryHelper()

    def main(self):
        """
        Main method to execute the query and processing logic.
        """
        input_data = demisto.args().get('data', [])
        self.helper.query_crowdstrike(input_data)
        self.helper.query_servicenow(input_data)

        # Clean and deduplicate ServiceNow results
        servicenow_cleaned = list({v['name']: v for v in self.helper.servicenow_results}.values())
        servicenow_not_found_cleaned = list({v['Data']: v for v in self.helper.servicenow_not_found}.values())
        crowdstrike_not_found_cleaned = list({v['Data']: v for v in self.helper.crowdstrike_not_found}.values())

        # Remove empty values from the ServiceNow results
        for idx, record in enumerate(servicenow_cleaned):
            servicenow_cleaned[idx] = {k: v for k, v in record.items() if v}

        # Generate CSV files for the results
        snow_csv = self.helper.generate_csv('snow_results.csv', servicenow_cleaned)
        cs_csv = self.helper.generate_csv('cs_results.csv', self.helper.crowdstrike_results)

        # Prepare results for CrowdStrike not found
        cs_not_found_markdown = tableToMarkdown('Not Found in CrowdStrike', crowdstrike_not_found_cleaned)
        cs_not_found_results = {
            'Queries': {'cs_not_found': crowdstrike_not_found_cleaned}
        }
        command_results_cs = CommandResults(
            outputs=cs_not_found_results, raw_response=crowdstrike_not_found_cleaned, readable_output=cs_not_found_markdown
        )
        return_results(command_results_cs)

        # Prepare results for ServiceNow not found
        snow_not_found_markdown = 'Not Found in ServiceNow CMDB\n' + tableToMarkdown('Not Found in ServiceNow CMDB', servicenow_not_found_cleaned)
        overall_results = {
            'Queries': {
                'snow_csv_file': snow_csv,
                'cs_csv_file': cs_csv,
                'servicenow_results': servicenow_cleaned,
                'snow_not_found': servicenow_not_found_cleaned,
                'checked_items': list(self.helper.checked_items)
            }
        }
        command_results_snow = CommandResults(
            outputs=overall_results, raw_response=servicenow_not_found_cleaned, readable_output=snow_not_found_markdown
        )
        return_results(command_results_snow)

        # Output the final results
        demisto.results(snow_csv)
        demisto.results(cs_csv)
        demisto.results('Finished executing all commands.')


if __name__ in ('__main__', '__builtin__', 'builtins'):
    # Create an instance of MainApp and execute the main method
    app = MainApp()
    app.main()
