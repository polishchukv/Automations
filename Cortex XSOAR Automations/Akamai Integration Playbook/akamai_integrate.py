import os
import requests
import logging
from akamai.edgegrid import EdgeGridAuth

class AkamaiIntegration:
    def __init__(self, params):
        self.server = params['url'].rstrip('/')
        self.client_token = params.get('client_token')
        self.client_secret = params.get('client_secret')
        self.access_token = params.get('access_token')
        self.use_ssl = not params.get('insecure', False)
        self.network_lists = '/network-list/v2/network-lists?includeElements=true&extended=true&listType=IP'

        if not params['proxy']:
            os.environ.pop('HTTP_PROXY', None)
            os.environ.pop('HTTPS_PROXY', None)
            os.environ.pop('http_proxy', None)
            os.environ.pop('https_proxy', None)

        # Initialize logger
        logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
        self.logger = logging.getLogger(__name__)

        # Initialize requests Session
        self.api = requests.Session()
        self.api.auth = EdgeGridAuth(
            client_token=self.client_token,
            client_secret=self.client_secret,
            access_token=self.access_token
        )

    def _construct_address(self, list_id, ip):
        # Validate list_id and ip
        if not list_id or not ip:
            raise ValueError("Both list_id and ip must be provided")
        return f'/network-list/v2/network-lists/{list_id}/elements?element={ip}'

    def _http_request(self, api_call, method, test):
        try:
            response = getattr(self.api, method)(self.server + api_call)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error(f"HTTP error occurred: {err}")
            raise
        except Exception as err:
            self.logger.error(f"An error occurred: {err}")
            raise

        return response.json() if not test else response

    def get_network_list(self, page=1):
        list_id = demisto.args()['list-id']
        results = []
        response = self._http_request(f"{self.network_lists}&page={page}", 'get', False)
        for item in response.get('networkLists', []):
            if item['uniqueId'] == list_id:
                ip_list = item.get('list')
                results.append({
                    'uniqueId': item['uniqueId'], 
                    'name': item['name'], 
                    'accessControlGroup': item['accessControlGroup'], 
                    'networkListType': item['networkListType'], 
                    'IP': ip_list
                })
        return results

    def get_network_lists(self, page=1):
        results = []
        response = self._http_request(f"{self.network_lists}&page={page}", 'get', False)
        for item in response.get('networkLists', []):
            results.append({'uniqueId': item['uniqueId'], 'name': item['name']})
        return results

    def test_module(self):
        try:
            self._http_request(self.network_lists, 'get', True)
            demisto.results('ok')
        except Exception as e:
            self.logger.error(str(e))
            return_error(str(e))
        demisto.results('ok')

    def add_ip_to_list(self, list_id, ip):
        site = self._construct_address(list_id, ip)
        response = self._http_request(site, 'put', True)
        if response.status_code == 204:
            return f"IP {ip} added to list {list_id}"
        else:
            return f"Failed to add IP {ip} to list {list_id}"

def main():
    akamai = AkamaiIntegration(demisto.params())
    try:
        if demisto.command() == 'test-module':
            akamai.test_module()
        elif demisto.command() == 'akamai-show-network-lists':
            demisto.results(akamai.get_network_list())
        elif demisto.command() == 'akamai-list-network-lists':
            demisto.results(akamai.get_network_lists())
        elif demisto.command() == 'akamai-add-ip-to-list':
            list_id = demisto.args()['list-id']
            ip = demisto.args()['ip']
            demisto.results(akamai.add_ip_to_list(list_id, ip))
    except Exception as e:
        akamai.logger.exception(f'Error has occurred in the Akamai Integration: {type(e)}\n {str(e)}')
        raise

if __name__ == "__main__":
    main()