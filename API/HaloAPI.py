import requests
import json
from Exceptions import InvalidAuthentication, BadRequestError,\
                       NoConfigError, ParseError

class HaloCaller():
    """
    Object for making REST API requests to HaloPSA
    
    Attributes:
      * config_file (str) - Path to a json file containing authentication
                            and url to your Halo client (see README for 
                            more information)
        o Config values needed for Halo:
          > client_id
          > client_secret
          > base_url
        
    Methods:
     * set_config()
     * get()
     * post()
     * delete()
     * search()
     * get_list()
     * get_id()
    """
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.__repeat = 0
        
        if config_file != None:
            config = json.load(open(self.config_file))
            
            self.__has_config = True
            
            self.__id = config['client_id']
            self.__secret = config['client_secret']
            self.__base_url = config['base_url'] + "api/"
            self.__auth_url = config['base_url'] + "auth/token"
            self.__headers = {
                'accept': 'applications/json',
                'Authorization': 'Bearer '
            }
            
            self.__check_config()
            self.__refresh_token()
        else:
            self.__has_config = False
    
    def __refresh_token(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.__id,
            'client_secret': self.__secret,
            'scope': 'all'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'applications/json',
        }

        response = requests.post(self.__auth_url, headers=headers, data=data)
        
        if response.status_code != 200:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
        self.__headers['Authorization'] = 'Bearer ' + response.json()['access_token']
        
    def __check_config(self): #TODO: Make more comprehensive??
        if self.__has_config == False:
            raise NoConfigError()
            
            
    def set_config(self, config_file):
        """
        Sets the config of the Halo Caller
        
        Parameters:
         * config_file (str) - Path to a json file containing authentication
                            and url to your Halo client (see README for 
                            more information)
          o Config values needed for Halo:
            > client_id
            > client_secret
            > base_url
         
        Returns: None
        """
        self.config_file = config_file
        
        config = json.load(open(self.config_file))
        
        self.__has_config = True
        
        self.__id = config['client_id']
        self.__secret = config['client_secret']
        self.__base_url = config['base_url']
        self.__headers = {
            'accept': 'applications/json',
            'Authorization': 'Bearer '
        }
        
        self.__check_config()
        self.__refresh_token()
        
    
    def get(self, endpoint, params=None):
        """
        Most basic get call to Halo client at a given endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * params (dict) - Dictionary of desired params (see HaloGuide.txt)
        
        Returns:
        * dict - The json data of the response
        """
        self.__check_config()
        url = self.__base_url + endpoint
        
        if params == None:
            params = {
                'count': 10000
            }
        else:
            if not 'count' in params:
                params['count'] = 10000
        
        response = requests.get(url=url, headers=self.__headers, params=params)
        if response.status_code == 401:
            if self.__repeat == 1:
                raise InvalidAuthentication("Error getting valid token for Halo API read requests")
            self.__refresh_token()
            self.__repeat = 1
            return self.get_list(endpoint=endpoint, params=params)
        
        if response.status_code == 200:
            self.__repeat = 0
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
    
    def post(self, endpoint, data):
        """
        Most basic post call to Halo client at a given endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * data (dict) - Dictionary of desired the data to be posted
        
        Returns:
        * dict - The json data of the response
        """
        self.__check_config()
        url = self.__base_url + endpoint
        
        response = requests.post(url=url, headers=self.__headers, json=[data])
        if response.status_code == 401:
            if self.__repeat == 1:
                raise PermissionError("Error getting valid token for Halo API post requests")
            self.__refresh_token()
            self.__repeat = 1
            self.post(endpoint=endpoint, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
    def delete(self, endpoint, id):
        """
        Most basic delete call to Halo client at a given endpoint and id
        
        Parameters:
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * id (int) - ID of the object to be deleted
        
        Returns:
        * dict - The json data of the response
        """
        self.__check_config()
        url = self.__base_url + endpoint + "/" + str(id)
        
        response = requests.delete(url=url, headers=self.__headers)
        if response.status_code == 401:
            if self.__repeat == 1:
                raise PermissionError("Error getting valid token for Halo API post requests")
            self.__refresh_token()
            self.__repeat = 1
            self.delete(endpoint=endpoint, id=id)
        
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
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * query (str) - Search query
         * params (dict) - Dictionary of desired params (see HaloGuide.txt)
        
        Returns:
        * list - List of the desired data
        """
        if params == None:
            params = {}
            
        params['search'] = query
        
        return self.get_list(endpoint=endpoint, params=params)
    
    def get_list(self, endpoint, params=None):
        """
        Similar to the get function, but simply returns a list of the data,
        excluding the extra json data
        
        Parameters:
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * params (dict) - Dictionary of desired params (see HaloGuide.txt)
        
        Returns:
        * list - List of the desired data
        """
        response = self.get(endpoint=endpoint, params=params)
        
        self.__repeat = 0
        response = response
        if type(response) == list:
            return response
        elif type(response) == dict:
            desired_len = 0
            if 'record_count' in response:
                desired_len = response['record_count']
            for lbl in response:
                if type(response[lbl]) == list and len(response[lbl]) == desired_len:
                    return response[lbl]
            raise ParseError(f"Cannot parse response to create a list for {endpoint}")
        
    def get_id(self, endpoint, id, params=None):
        """
        Similar to the get function, but gets the information for a
        specific id in the endpoint
        
        Parameters:
         * endpoint (str) - Desired endpoint (see HaloGuide.txt for full list)
         * id (int/str) - ID of the desired object
         * params (dict) - Dictionary of desired params (see HaloGuide.txt)
        
        Returns:
        * dict - The json data of the response
        """
        endpoint = endpoint + "/" + str(id)
        
        return self.get(endpoint=endpoint, params=params)
    
    """ Keep or no?
    def search_client_name(self, client_name, repeat=0):
        self.__check_config()
        url = self.__base_url + 'Client'
        
        params = {
            'search': client_name
        }
        
        clients = requests.get(url=url, headers=self.__headers, params=params)
        if clients.status_code == 401:
            if repeat == 1:
                raise PermissionError("Error getting valid token for Halo API read requests")
            self.__refresh_token()
            self.search_client_name(client_name, repeat=1)
        
        try:
            return clients.json()['clients']
        except Exception as e:
            print(clients.status_code)
            print(clients.text)
            raise(e)
    
    def list_users_in_client(self, client_id, repeat=0):
        self.__check_config()
        url = self.__base_url + 'Users'
        
        params = {
            'count': 1000,
            'client_id': client_id
        }
        
        users = requests.get(url=url, headers=self.__headers, params=params)
        if users.status_code == 401:
            if repeat == 1:
                raise PermissionError("Error getting valid token for Halo API read requests")
            self.__refresh_token()
            self.list_users_in_client(client_id, repeat=1)
            
        if len(users.json()['users']) == 0:
            print('No users found in specified client!')
        
        return users.json()['users']
    """
        
        
def get_list_test(halo_obj: HaloCaller):
    endpoints = ["Actions", "Agent", "Appointment", "Asset", "Attachment", "Client", 
                 "ClientContract", "Invoice", "Item", "KBArticle", "Opportunities",
                 "Projects", "Quotation", "Report", "Site", "Status", "Supplier",
                 "Team", "TicketType", "Tickets", "Users"]
    
    try:
        for endpoint in endpoints:
            halo_obj.get_list(endpoint=endpoint)
    except ParseError:
        print(f"Parse error for endpoint: {endpoint}")
        return
    

if __name__ == '__main__':
    halo_obj = HaloCaller()
    
    halo_obj.set_config('../../Auth/halo_params.json')
    
    #get_list_test(halo_obj=halo_obj)