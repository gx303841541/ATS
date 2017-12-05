
import os, logging, datetime, re, sys, time
import paramiko


#ssh to router
class MySsh():
    def __init__(self, host, user=None, password=None, log_file=sys.stdout, logger=None):
        self.host = host
        self.user = user
        self.password = password
        self.log_file = log_file
        self.LOG = logger
        self.conn = None


    def connect(self):
        self.LOG.debug('ssh to %s' % (self.host))
        #paramiko.util.log_to_file(self.log_file + 'ssh.log')
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conn.connect(self.host, 22, self.user, self.password, timeout=5)


    def send(self, cmd, timeout=5, prompt=None):
        self.LOG.debug('To send cmd: %s' % (cmd))
        try:
            stdin, stdout, stderr = self.conn.exec_command(cmd)
            err = stderr.read()
            out = stdout.read()

        except Exception as er:
            self.LOG.error('Send %s wrong: %s\n[[%s]]' % (cmd, err, str(er)))
            return None
        return out


    def get(self, timeout=5, prompt=None):
        try:
            stdin, stdout, stderr = self.conn.exec_command('\n')
            err = stderr.read()
            out = stdout.read()

        except Exception as er:
            self.LOG.error('get output wrong: %s\n[%s]' % (err, str(er)))
            return None
        return out + err


    def close(self):
        return self.conn.close()


    def is_open(self):
        if self.conn:
            return True
        else:
            return False
