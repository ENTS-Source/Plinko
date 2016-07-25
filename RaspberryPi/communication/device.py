from serial import Serial
import threading
import time

class PlinkoBoard:
    def __init__(self, port):
        self._initPort(port)
        self.score = 0
        self.scoreUpdated = False;
        self.newScore = False

    def _initPort(self, port):
        self.__port = Serial(port, baudrate=9600)
        self.__thread = threading.Thread(target=self._thread_check_score, args=[])
        self.__thread.daemon = True
        self.__thread.start()

    def _thread_check_score(self):
        print("Running check Plinko board thread...")
        while True:
            try:
                time.sleep(0.1) # for thread catchup

                val = self.__port.readline()
                if val == '' or val[0] == 'H': # H = heartbeat
                    continue
                self.score = int(val[1:]) # strip off first character`
                if val[0] == 'P':
                    self.scoreUpdated = True
                elif val[0] == 'F':
                    self.scoreUpdated = True
                    self.newScore = True
                print("Read score: " + val)
            except IOError as e:
                pass
            except Exception as e:
                print("Exception encountered during serial read: " + e.message)
                time.sleep(5)

    def close(self):
        self.__port.close()
