
import yaml 

class Config :
    def __init__(self,  config_file):
        self.config_file = config_file
        self.data = None
        
    def load(self) :
        stream = file(self.config_file, 'rb')    
        self.data =  yaml.load(stream)
        return self.data
        
    def save(self) :
        stream = file(self.config_file, 'wb')    
        yaml.dump(self.data,  stream)
        
