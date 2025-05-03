import requests
import json
from Exceptions import BadRequestError, NoConfigError,\
                       ParseError, InvalidAuthentication

class SyncroCaller():
    """
    Object for making REST API requests to SyncroMSP
    
    Attributes:
      * config_file (str) - Path to a json file containing authentication
                            and url to your Syncro client (see README for 
                            more information)
        o Config values needed for Syncro:
          > authorization
          > base_url
        
    Methods:
     * set_config()
     * get()
     * post()
     * delete()
     * search()
     * search_all()
     * get_list()
     * get_id()
    """
    def __init__(self, config_file=None):
        self.config_file = config_file
        
        if config_file != None:
            self.__has_config = True
            config = json.load(open(config_file))
            
            self.__auth = config['authorization']
            self.__base_url = config['base_url']
            self.__headers = {
                'accept': 'application/json',
                'Authorization': self.__auth
            }
            
            self.__check_config()
        else:
            self.__has_config = False
    
    def __check_config(self):
        if not self.__has_config:
            raise NoConfigError()
    
    def set_config(self, config_file):
        """
        Sets the config of the Syncro Caller
        
        Parameters:
         * config_file (str) - Path to a json file containing authentication
                            and url to your Syncro client (see README for 
                            more information)
          o Config values needed for Syncro:
            > authorization
            > base_url
         
        Returns: None
        """
        self.config_file = config_file
        
        config = json.load(open(config_file))
        
        self.__has_config = True
        
        self.__auth = config['authorization']
        self.__base_url = config['base_url']
        self.__headers = {
            'accept': 'application/json',
            'Authorization': self.__auth
        }
        
        self.__check_config()

    def get(self, endpoint, params=None):
        """
        Most basic get call to Syncro client at a given endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * params (dict) - Any parameters to be included with the get request
        
        Returns:
        * dict - The json data of the response
        """
        url = self.__base_url + endpoint
        
        response = requests.get(url=url, headers=self.__headers, params=params)
        if response.status_code == 401:
            raise InvalidAuthentication('Authorization token not valid!')
        if response.status_code == 429:
            import time
            print("Syncro get requests occuring too frequently! Pausing for one second then proceeding...")
            time.sleep(1)
            return self.get(endpoint=endpoint, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
    def post(self, endpoint, data):
        """
        Most basic post call to Syncro client at a given endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * data (dict) - Data to be posted
        
        Returns:
        * dict - The json data of the response
        """
        url = self.__base_url + endpoint
        
        response = requests.post(url=url, headers=self.__headers, data=data)
        if response.status_code == 401:
            raise InvalidAuthentication("Auth token does not have permission to post to Syncro!")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
    def delete(self, endpoint, id):
        """
        Most basic delete call to Syncro client at a given endpoint and id
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * id (int) - ID of the object to be deleted
        
        Returns:
        * dict - The json data of the response
        """
        self.__check_config()
        url = self.__base_url + endpoint + '/' + id
        
        response = requests.delete(url=url, headers=self.__headers)
        if response.status_code == 401:
            raise InvalidAuthentication("Auth token does not have permission to post to Syncro!")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
            
    def search(self, endpoint, query, params=None):
        """
        Search for matching objects at a given endpoint
        
        Note: Not all endpoints will be searched, if an unsearchable endpoint is
              used, the output of get_list at that endpoint will be returned
              
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * query (str) - Search query
         * params (dict) - Dictionary of desired params (see SyncroGuide.txt)
        
        Returns:
        * list - List of the desired data
        """
        if params == None:
            params = {}
            
        params['query'] = query
        
        return self.get_list(endpoint=endpoint, params=params)
    
    def search_all(self, query, params=None):
        """
        Search all of syncro
              
        Parameters:
         * query (str) - Search query
         * params (dict) - Dictionary of desired params (see SyncroGuide.txt)
        
        Returns:
        * list - List of the desired data
        """
        if params == None:
            params = {}
            
        params['query'] = query
        
        return self.get_list('search', params=params)
    
    def get_list(self, endpoint, params=None):
        """
        Similar to the get function, but simply returns a list of the data,
        going through every page of the response.
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * params (dict) - Dictionary of desired params (see SyncroGuide.txt)
        
        Returns:
        * list - List of the desired data
        """
        response = self.get(endpoint=endpoint, params=params)

        data_list = None
        for lbl in response:
            if type(response[lbl]) == list:
                data_list = response[lbl]
                break
        if data_list == None:
            if endpoint == 'search': #Only one that returns None instead of an empty list
                return []
            raise ParseError(f"Cannot parse response to create a list for {endpoint}")
        
        if 'meta' in response:
            if params == None:
                params = {}
            
            pages = response['meta']['total_pages']
            i = 2
            while i <= pages:
                params['page'] = i
                
                response = self.get(endpoint=endpoint, params=params)
                
                for lbl in response:
                    if type(response[lbl]) == list:
                        data_list = [*data_list, *response[lbl]]
                        break
                
                i += 1
    
        return data_list
    
    def get_id(self, endpoint, id, params=None):
        """
        Similar to the get function, but gets the information for a
        specific id in the endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * id (int/str) - ID of the desired object
         * params (dict) - Dictionary of desired params (see SyncroGuide.txt)
        
        Returns:
        * dict - The json data of the response
        """
        endpoint = endpoint + '/' + str(id)
        
        return self.get(endpoint=endpoint, params=params)
    
    """ Keep or no?
    def list_users_in_client(self, client_id):
        url = self.__base_url + 'contacts'
        
        params = {
            'customer_id': client_id
        }
        
        users = requests.get(url=url, headers=self.__headers, params=params)
        if users.status_code == 401:
            raise PermissionError('Authorization token not valid!')
        
        all_users = []
        
        all_users = [*all_users, *users.json()['contacts']]
        
        pages = users.json()['meta']['total_pages']
        if pages > 1:
            for i in range(2,pages+1):
                params = {
                    'customer_id': client_id,
                    'page': i
                }
                
                users = requests.get(url=url, headers=self.__headers, params=params)
                
                all_users = [*all_users, *users.json()['contacts']]
                
        return all_users
    """
        
if __name__ == '__main__':
    syncro_obj = SyncroCaller(config_file='../../Auth/syncro_params.json')
    
    response = syncro_obj.search_all('Sealstrip')
    print(response)