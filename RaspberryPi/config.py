import os.path
from configobj import ConfigObj


class Configuration:
    def __init__(self):
        path = "../plinko.conf"
        # TODO: "Get updates" approach instead of "has config"
        if not os.path.exists(path):
            self.__getconf(path)
        config = ConfigObj(path)
        self.game = GameInfo(config['Game'])
        self.devices = DevicesInfo(config['Devices'])
        self.buttons = ButtonInfo(config['Buttons'])

    @staticmethod
    def __getconf(target_path):
        f = open(target_path, 'w')
        for line in open("config.conf"):
            if line.startswith('# !!'): continue
            f.write(line + '\n')
        f.close()


class GameInfo:
    def __init__(self, section):
        self.fullscreen = int(section['fullscreen']) == 1


class DevicesInfo:
    def __init__(self, section):
        self.left = section['left']
        self.right = section['right']

class ButtonInfo:
    def __init__(self, section):
        self.btn1_pin = int(section['btn1_pin'])
        self.btn2_pin = int(section['btn2_pin'])
