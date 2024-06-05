from typing import Dict, Any
import traceback
import logging

# Set up logging at the INFO level
logging.basicConfig(level=logging.INFO)

# Define the TableManager class
class TableManager:
    # Initialize the class with arguments
    def __init__(self, args: Dict[str, Any]):
        # Get the table name, headers, and command from the arguments
        # The get method is used to avoid KeyError if the key is not present in the dictionary
        self.table_name = args.get('tableName')
        self.headers = args.get('headers')
        self.command = args.get('command', 'CREATE')

        # Validate the arguments
        self.validate_arguments()

    # Validate the arguments
    def validate_arguments(self):
        # Raise an error if the table name is not provided
        # This is necessary because the table name is required to execute any SQL command
        if not self.table_name:
            raise ValueError("Table name must be provided.")
        # Raise an error if headers are not provided for the CREATE command
        # This is necessary because the headers define the structure of the table
        if not self.headers and self.command == 'CREATE':
            raise ValueError("Headers must be provided for CREATE command.")
    
    # Parse the headers
    def parse_headers(self):
        headers = {}
        # Split the headers by comma and space, and assign a default type if not provided
        # This is done to allow the headers to be specified in a compact format
        for header in self.headers.split(','):
            name, *type_info = header.strip().split()
            data_type = ' '.join(type_info) if type_info else 'varchar(255)'
            headers[name] = data_type
        return headers

    # Generate a CREATE TABLE query
    def generate_create_query(self):
        headers = self.parse_headers()
        # Generate the column definitions for the SQL query
        columns = [f'{name} {data_type}' for name, data_type in headers.items()]
        joined_columns = ', '.join(columns)
        return f'CREATE TABLE {self.table_name} ({joined_columns})'

    # Generate a DROP TABLE query
    def generate_drop_query(self):
        return f'DROP TABLE IF EXISTS {self.table_name}'
    
    # Execute the command
    def execute(self):
        query = ""
        # Generate the appropriate query based on the command
        # This allows the class to support multiple commands
        if self.command == 'CREATE':
            query = self.generate_create_query()
        elif self.command == 'DROP':
            query = self.generate_drop_query()
        else:
            raise ValueError('Unsupported SQL command')

        # Try to execute the query and handle any exceptions
        # This is done to provide a useful error message if the query fails
        try:
            logging.info(f"Executing query: {query}")
            response = execute_command('asset-query-sql', {'query': query})
            return_results(response)
        except Exception as ex:
            demisto.error(traceback.format_exc())
            return_error(f'Failed to execute BaseScript. Error: {str(ex)}')

# Define the main function
def main(arguments):
    # Create an instance of TableManager and execute the command
    # This is done to encapsulate the functionality in a class and make the code more modular
    table_manager = TableManager(arguments)
    table_manager.execute()

# Execute the main function if the script is run directly
# This is a common Python idiom to allow or prevent parts of code from being run when the modules are imported
if __name__ in ('__main__', '__builtin__', 'builtins'):
    demisto.results(main(demisto.args()))