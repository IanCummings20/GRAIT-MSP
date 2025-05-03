import requests
import json
from Exceptions import BadRequestError, NoConfigError,\
                       InvalidAuthentication

class ConnectwiseCaller():
    """
    Object for making REST API requests to Connectwise Control
    
    Attributes:
      * config_file (str) - Path to a json file containing authentication
                            and url to your Connectwise client (see README for 
                            more information)
        o Config values needed for Connectwise Control:
          > authorization
          > base_url
        
    Methods:
     * set_config()
     * get()
     * post()
     * get_session_by_id()
     * get_details_by_id()
     * get_session_by_filter()
     * get_session_by_name()
     * get_all_access_sesions()
     * post_session()
     * post_note_to_session()
     * post_command_to_session()
     * post_message_to_session()
     * post_toolbox_to_session()
     * post_properties_to_session()
     * post_name_to_session()
    """
    def __init__(self, config_file=None):
        self.config_file = config_file
        
        if self.config_file != None:
            config = json.load(open(self.config_file))
            
            self.__has_config = True
            
            self.__auth = config['authorization']
            self.__base_url = config['base_url']
            self.__headers = {
                'accept': 'application/json',
                'CTRLAuthHeader': self.__auth,
                'origin': 'localhost'
            }
        else:
            self.__has_config = False
    
    def __check_config(self):
        if not self.__has_config:
            raise NoConfigError()
        
    def set_config(self, config_file):
        """
        Sets the config of the Connectwise Caller
        
        Parameters:
         * config_file (str) - Path to a json file containing authentication
                            and url to your Connectwise client (see README for 
                            more information)
          o Config values needed for Connectwise:
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
            'CTRLAuthHeader': self.__auth,
            'origin': 'localhost'
        }
        
        self.__check_config()
    
    def get(self, endpoint, data):
        """
        Basic get call to Connectwise client, only needed as a helper
        function, but could be used if wanted
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * data (list) - List of the required parameters for the endpoint
        
        Returns:
        * list - List of data
        """
        self.__check_config()
        
        url = self.__base_url + endpoint
        
        response = requests.get(url=url, headers=self.__headers, json=data)
        if response.status_code == 401:
            raise InvalidAuthentication('Authorization token not valid!')

        if response.status_code == 200:
            return response.json()
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
    def post(self, endpoint, data):
        """
        Basic post call to Connectwise client, only needed as a helper
        function, but could be used if wanted
        
        Parameters:
         * endpoint (str) - Desired endpoint (see SyncroGuide.txt for full list)
         * data (list) - List of the parameters to write
        
        Returns:
         * None
        """
        self.__check_config()
        
        url = self.__base_url + endpoint
        
        response = requests.post(url=url, headers=self.__headers, json=data)
        if response.status_code == 401:
            raise InvalidAuthentication('Authorization token not valid!')

        if response.status_code == 200:
            return None
        else:
            raise BadRequestError(f"{response.status_code}: {response.text}")
        
    
    def get_session_by_id(self, id: str):
        """
        Get session by the session id
        
        Parameters:
         * id (str) - Session id
        
        Returns:
         * list - A list containing the session
        """
        return self.get('GetSessionBySessionID', [id])

    def get_details_by_id(self, id: str):
        """
        Get session details by the session id
        
        Parameters:
         * id (str) - Session id
        
        Returns:
         * list - A list containing the session details
        """
        return self.get('GetSessionDetailsBySessionID', [id])

    def get_session_by_filter(self, filter):
        """
        Get session by the given SQL filter
        
        Parameters:
         * filter (str) - SQL filter
        
        Returns:
         * list - A list containing the sessions that match the filter 
        """
        return self.get('GetSessionsByFilter', [filter])

    def get_session_by_name(self, name):
        """
        Get session with the given name
        
        Parameters:
         * name (str) - Session name
        
        Returns:
         * list - A list containing the session with given name
        """
        return self.get('GetSessionsByName', [name])

    def get_all_access_sessions(self):
        """
        Get all access sessions
        
        Parameters:
         * None
        
        Returns:
         * list - A list containing all access sessions
        """
        return self.get('GetSessionsByFilter', ["SessionType = 'Access'"])

    def post_session(self, session_type, name, is_public, code, properties):
        """
        Post a new session
        
        Parameters:
         * session_type (str) - Session type
         * name (str) - Session name
         * is_public (bool) - If the session is public
         * code (str) - Session code
         * properties (list) - Session custom properties
        
        Returns:
         * None
        """
        return self.post('CreateSession', [session_type, name, is_public, code, properties])
        
    def post_note_to_session(self, id: str, note):
        """
        Post note to given session
        
        Parameters:
         * id (str) - Session id
         * note (str) - Note to post to the session
        
        Returns:
         * None
        """
        return self.post('AddNoteToSession', [id, note])

    def post_command_to_session(self, id, command):
        """
        Send a command to given session
        
        Parameters:
         * id (str) - Session id
         * command (str) - Command to send to the session
        
        Returns:
         * None
        """
        return self.post('SendCommandToSession', [id, command])

    def post_message_to_session(self, id, host, session):
        """
        Post message to given session
        
        Parameters:
         * id (str) - Session id
         * host (str) - Host the message will be sent by
         * message (str) - Message to send to the session
        
        Returns:
         * None
        """
        return self.post('SendMessageToSession', [id, host, session])

    def post_toolbox_to_session(self, id, toolbox_item_name):
        """
        Send a toolbox item to given session
        
        Parameters:
         * id (str) - Session id
         * toolbox_item_name (str) - Toolbox item name
        
        Returns:
         * None
        """
        return self.post('SendToolboxItemToSession', [id, toolbox_item_name])

    def post_properties_to_session(self, id, properties):
        """
        Post custom properties to given session
        
        Parameters:
         * id (str) - Session id
         * properties (list) - Session custom properties
        
        Returns:
         * None
        """
        return self.post('UpdateSessionCustomProperties', [id, properties])

    def post_name_to_session(self, id, name):
        """
        Post name to given session
        
        Parameters:
         * id (str) - Session id
         * name (str) - Session name
        
        Returns:
         * None
        """
        return self.post('UpdateSessionName', [id, name])
        
        
if __name__ == '__main__':
    connectwise = ConnectwiseCaller()
    
    connectwise.set_config("../../Auth/connectwise_params.json")
    
    response = connectwise.get_session_by_name('JMC-MAC-LT')
    
    print(response)