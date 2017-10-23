#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ATS socket
   by Kobe Gong. 2017-9-29
"""

import time
import sys
import re
import os
import random
import datetime
import socket
import Queue
import select
import threading
from basic.log_tool import MyLogger
from APIs.common_APIs import protocol_data_printB

class MyServer:
    def __init__(self, addr, logger, debug=False, singlethread=True):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(addr)
        server.listen(10000)
        self.server = server

        self.LOG = logger
        self.debug = debug
        self.singlethread = singlethread

        # comm data
        self.clients = {}
        self.inputs = [server]
        self.conn_to_addr = {}

    def run_forever(self):
        BUFF_SIZE = 1024
        timeout = 1

        try:
            while True:
                if self.debug:
                    self.LOG.debug("Waiting for next event, now has active clients: %d" % (len(self.clients)))
                readable, writable, exceptional = select.select(self.inputs, [], [], timeout)
                for conn in readable:
                    if conn == self.server:
                        try:
                            connection, client_address = self.server.accept()
                            connection.setblocking(0)
                            self.LOG.info(
                                "Get connection from: " + client_address[0])
                            self.clients[client_address] = {
                                'conn': connection,
                                'queue_in': Queue.Queue(),
                                'queue_out': Queue.Queue(),
                            }
                            self.inputs.append(connection)
                            self.conn_to_addr[connection] = client_address

                        except Exception as e:
                            self.LOG.error("Get connection %s falied![%s]" % (
                                client_address[0], e))
                            pass

                    else:
                        try:
                            data = conn.recv(BUFF_SIZE)
                            if data:
                                self.clients[self.conn_to_addr[conn]]['queue_in'].put(data)
                                self.clients[self.conn_to_addr[conn]]['queue_out'].put('1234567890')
                                if self.debug:
                                    self.LOG.info("Get data from " + self.conn_to_addr[conn][0] + ": " + data)
                            else:
                                # Interpret empty result as closed connection
                                self.LOG.error(
                                    self.conn_to_addr[conn][0] + ' closed!')
                                self.clients[self.conn_to_addr[conn]]['conn'].close()
                                self.inputs.remove(conn)
                                del self.clients[self.conn_to_addr[conn]]
                                del self.conn_to_addr[conn]

                        except socket.error:
                            self.LOG.error("Get data from %s falied!" %(self.conn_to_addr[conn][0]))
                            self.clients[self.conn_to_addr[conn]]['conn'].close()
                            self.inputs.remove(conn)
                            del self.clients[self.conn_to_addr[conn]]
                            del self.conn_to_addr[conn]
                            pass

                if self.singlethread:
                    self.send_once()

        except KeyboardInterrupt:
            self.LOG.info('KeyboardInterrupt, now to close all clinets and server!')
            for client in self.clients:
                self.clients[client]['conn'].close()
            self.server.close()
            sys.exit(0)

        finally:
            self.LOG.info("socket server end!")
            th.join()

    def sendloop(self):
        while True:
            self.send_once()

    def send_once(self):
        try:
            for client in self.conn_to_addr:
                if self.clients[self.conn_to_addr[client]]['queue_out'].empty():
                    pass
                else:
                    data = self.clients[self.conn_to_addr[client]]['queue_out'].get()
                    try:
                        client.send(data)
                        if self.debug:
                            self.LOG.yinfo("Send data to " + self.conn_to_addr[client][0] + ": " + data)
                    except:
                        self.LOG.error(self.conn_to_addr[client][0] + ' closed!')
                        self.clients[self.conn_to_addr[client]]['conn'].close()
                        self.inputs.remove(client)
                        del self.clients[self.conn_to_addr[client]]
                        del self.conn_to_addr[client]

        except Exception as e:
            self.LOG.warn(str(e))


class MyClient:
    def __init__(self, addr, logger, queue_in, queue_out, heartbeat=0, heartbeat_data='1\n', debug=False, singlethread=True):
        self.queue = {
            'queue_in': queue_in,
            'queue_out': queue_out,
        }
        self.client = ''
        self.addr = addr
        self.LOG = logger
        self.connected = False
        self.heartbeat = heartbeat
        self.heartbeat_data = heartbeat_data
        self.debug = debug
        self.singlethread = singlethread

    def run_forever(self):
        BUFF_SIZE = 1024
        timeout = 1

        try:
            while True:
                # wait for connection setup
                while self.connected == False:
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.inputs = [self.client]
                    try:
                        self.client.connect(self.addr)
                        self.LOG.info("Connection setup suceess!")
                        while not self.queue['queue_in'].empty():
                            self.queue['queue_in'].get_nowait()

                        while not self.queue['queue_out'].empty():
                            self.queue['queue_out'].get_nowait()

                        self.connected = True
                        break
                    except:
                        self.LOG.warn("Connect to server failed, wait 10s...")
                        time.sleep(10)

                readable, writable, exceptional = select.select(
                    self.inputs, [], self.inputs, timeout)

                # When timeout reached , select return three empty lists
                if not (readable):
                    pass
                else:
                    try:
                        data = self.client.recv(BUFF_SIZE)
                        if data:
                            self.queue['queue_in'].put(data)
                            if self.debug:
                                self.LOG.info("client get data: %s" % (data))
                        else:
                            self.LOG.error("Server maybe has closed!")
                            self.client.close()
                            self.inputs.remove(self.client)
                            self.connected = False

                    except socket.error:
                        self.LOG.error("socket error, don't know why.")
                        self.client.close()
                        self.inputs.remove(self.client)
                        self.connected = False

                if self.connected == True and self.singlethread:
                    self.send_once()

        except KeyboardInterrupt:
            self.client.close()
            self.LOG.warn("Oh, you killed me...")

        except Exception as e:
            self.client.close()
            self.connected = False
            self.LOG.error("server socket closed. %s" % (e))

        finally:
            self.LOG.info("End!")
            sys.exit(0)

    def sendloop(self):
        while True:
            self.send_once()

    def send_once(self):
        try:
            while self.connected != True:
                pass

            if self.queue['queue_out'].empty():
                if self.heartbeat:
                    time.sleep(self.heartbeat)
                    self.queue['queue_out'].put(self.heartbeat_data)
                else:
                    pass
            else:
                data = self.queue['queue_out'].get()
                if self.debug:
                    self.LOG.yinfo(protocol_data_printB(data, title="client send date:" % (self)))
                self.client.send(data)

        except Exception as e:
            self.LOG.warn(str(e))
