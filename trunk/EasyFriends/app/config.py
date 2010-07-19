
import ConfigParser
import string

class IniSettings(dict):
    def __init__(self, filename):
        self.filename = filename
        self.__loadConfig()

    # Load the ini file into a dictionarie
    def __loadConfig(self):
        self.clear()
        cp = ConfigParser.ConfigParser()
        cp.read(self.filename)
        for sec in cp.sections():
            settings={}
            name = string.lower(sec)
            for opt in cp.options(sec):
                settings[string.lower(opt)] = string.strip(cp.get(sec, opt))
            self.__setitem__(name,settings)

    def reload(self):
        """Reload the config file"""
        self.settings = self.__loadConfig()
    
    def save(self):
        """save the config file"""
        inifile = open(self.filename, 'w')
        for group in self.keys():
            inifile.write("\n["+group+"]\n")
            for key in self[group].keys():
                inifile.write(str(key)+"="+str(self[group][key])+"\n")

