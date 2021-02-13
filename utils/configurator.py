from configparser import ConfigParser


class Configurator():
        
    def __init__(self, filename='/home/david/iot/project/settings.ini'): 
        self.__config = ConfigParser()
        self.__config.read(filename)
        print(self.__config['Dataset']['dataset_root_path'])

    def get(self, section='', config_name=''):
        return self.__config[section][config_name]
    