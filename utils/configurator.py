from configparser import ConfigParser
import os, sys

if __name__ == '__main__':
    sys.path.append(os.getcwd())
sys.path[0]=os.path.dirname(os.path.realpath(__file__))

class Configurator():
        
    def __init__(self, filename='/home/david/iot/project/settings.ini'): 
        self.__config = ConfigParser()
        self.__config.read(filename)
        print(self.__config['Dataset']['dataset_root_path'])

    def get(self, section='', config_name=''):
        return self.__config[section][config_name]
    