
import time
import telnetlib

#telnet to router
class MyTelnet():
    def __init__(self, host, user=None, logger=None):
        self.host = host
        self.user = user
        self.LOG = logger
        self.conn = None


    def connect(self):
        self.LOG.debug('telnet to %s' % (self.host))
        self.conn = telnetlib.Telnet(self.host, timeout=5)
        try:
            self.conn.open(self.host)
            time.sleep(1)
            rd = self.conn.read_very_eager()

        except Exception as er:
            self.LOG.critical("open telnet wrong!!![%s]" % (er))
            self.conn.close()
            self.conn = None
            return 0


    def send(self, cmd, timeout=5):
        self.LOG.debug('To send cmd: %s' % (cmd))
        try:
            cmd = cmd.encode('ascii')
            x = self.conn.write(cmd +'\n')
            time.sleep(1)
            r = self.conn.read_very_eager()
            return r

        except Exception as er:
            self.LOG.critical("send %s wrong!!![%s]" % (cmd, er))
            self.conn.close()
            return 0


    def get(self, timeout=5, prompt=None):
        pass


    def close(self):
        return self.conn.close()


    def is_open(self):
        if self.conn:
            return True
        else:
            return False
