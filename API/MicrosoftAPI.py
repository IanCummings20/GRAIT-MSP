import requests
import json
import msal
from Exceptions import BadRequestError, NoConfigError, InvalidAuthentication

class MicrosoftGraphCaller():
    """
    **NOT IMPLEMENTED**
    Object for making REST API requests to Microsoft Graph
    
    Attributes:
      * config_file (str) - Path to a json file containing authentication
                            and url to your Graph client (see README for 
                            more information)
        o Config values needed for Connectwise Control:
          > authority
          > client_id
          > scope
          > client_secret
          > base_url
        
    Methods:
     * set_config()
     * get()    #TODO: Implement
     * post()   #TODO: Implement
     * list_users_in_client()
    """
    def __init__(self, config_file=None):
        self.config_file = config_file
        
        if self.config_file != None:
            config = json.load(open(config_file))
            
            self.__has_config = True
            
            self.__client_base = config['authority']
            self.__id = config['client_id']
            self.__scope = config['scope']
            self.__secret = config['secret']
            self.__base_url = config['base_url']
            
            self.__check_config()
        else:
            self.__has_config = False
            
    def __check_config(self):
        if not self.__has_config:
            raise NoConfigError()
        
    def set_config(self, config_file):
        """
        Sets the config of the Microsoft Graph Caller
        
        Parameters:
         * config_file (str) - Path to a json file containing authentication
                            and url to your Microsoft Graph client (see README for 
                            more information)
          o Config values needed for Connectwise:
            > authorization
            > base_url
         
        Returns: None
        """
        config = json.load(open(config_file))
        
        self.__has_config = True
        
        self.__client_base = config['authority']
        self.__id = config['client_id']
        self.__scope = config['scope']
        self.__secret = config['secret']
        self.__endpoint = config['endpoint']
        
        self.__check_config()
        
    def get(self, endpoint, data):
        """
        **NOT IMPLEMENTED**
        Basic get call to Graph client
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * data (list) - List of the required parameters for the endpoint
        
        Returns:
        """
        raise NotImplementedError
    
    def post(self, endpoint, data):
        """
        **NOT IMPLEMENTED**
        Basic post call to Graph client
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * data (list) - List of the required parameters for the endpoint
        
        Returns:
        """
        raise NotImplementedError
        
    def list_users_in_client(self, client_id):
        """
        Lists the users in a client, given client ID
        
        Parameters:
         * client_id (str) - ID of client
        
        Returns:
        * list - List of the users
        """
        url = self.__base_url + "users"
        auth = self.__client_base + client_id
        
        app = msal.ConfidentialClientApplication(
            client_id=self.__id, authority=auth,
            client_credential=self.__secret
        )
        
        #Check for cached token
        result = None
        result = app.acquire_token_silent(scopes=self.__scope, account=None)
        
        if not result:
            result = app.acquire_token_for_client(scopes=self.__scope)
        
        if "access_token" in result:
            headers = {
                'Authorization': 'Bearer ' + result['access_token']
            }
            
            response = requests.get(
                url=self.__endpoint,
                headers=headers)
        else:
            raise InvalidAuthentication("Authentication error for Graph API!")
        
        if response.status_code == 200:
            return response.json()['value']
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
    
if __name__ == '__main__':
    mGraph_obj = MicrosoftGraphCaller(config_file='../../Auth/microsoft_params.json')