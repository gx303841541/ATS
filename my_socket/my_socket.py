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
from basic.log_tool import MyLogger
from APIs.common_APIs import protocol_data_printB

class MyServer:
    def __init__(self, addr, logger):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(False)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(addr)
        server.listen(10000)
        self.server = server

        # comm data
        self.clients = {}
        self.inputs = {server: 1}
        self.LOG = logger

    def run_forever(self):
        timeout = 0.01
        BUFF_SIZE = 1024
        conn_to_addr = {}

        try:
            while True:
                self.LOG.debug("Waiting for next event, now has active clients: %d" % (len(self.clients)))
                readable, writable, exceptional = select.select(
                    self.inputs, [], [], timeout)

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
                            self.inputs[connection] = 1
                            conn_to_addr[connection] = client_address

                        except Exception as e:
                            self.LOG.error("Get connection %s falied![%s]" % (
                                client_address[0], e))
                            pass

                    else:
                        try:
                            data = conn.recv(BUFF_SIZE)
                            if data:
                                self.clients[conn_to_addr[conn]
                                             ]['queue_in'].put(data)
                                self.LOG.info(
                                    "Get data from " + conn_to_addr[conn][0] + ": " + data)
                            else:
                                # Interpret empty result as closed connection
                                self.LOG.error(
                                    conn_to_addr[conn][0] + ' closed!')
                                self.clients[conn_to_addr[conn]
                                             ]['conn'].close()
                                del self.inputs[conn]
                                del self.clients[conn_to_addr[conn]]
                                del conn_to_addr[conn]


                        except socket.error:
                            self.LOG.error("Get data from %s falied!" %
                                           (conn_to_addr[conn][0]))
                            self.clients[conn_to_addr[conn]]['conn'].close()
                            del self.inputs[conn]
                            del self.clients[conn_to_addr[conn]]
                            del conn_to_addr[conn]

                            pass

                for clinet in conn_to_addr:
                    if self.clients[conn_to_addr[clinet]]['queue_out'].empty():
                        #self.LOG.debug(
                        #    "No data need send to client: " + conn_to_addr[clinet][0])
                        pass
                    else:
                        data = self.clients[conn_to_addr[clinet]
                                            ]['queue_out'].get()
                        try:
                            clinet.send(data)
                            self.LOG.yinfo(
                                "Send data to " + conn_to_addr[clinet][0] + ": " + data)
                        except:
                            self.LOG.error(
                                conn_to_addr[clinet][0] + ' closed!')
                            self.clients[conn_to_addr[clinet]]['conn'].close()
                            del self.inputs[clinet]
                            del self.clients[conn_to_addr[clinet]]
                            del conn_to_addr[clinet]

        except KeyboardInterrupt:
            self.LOG.info(
                'KeyboardInterrupt, now to close all clinets and server!')
            for client in self.clients:
                self.clients[client]['conn'].close()
            self.server.close()

        finally:
            self.LOG.info("socket server end!")


class MyClient:
    def __init__(self, addr, logger, queue_in, queue_out, heartbeat=False, debug=False):
        self.queue = {
            'queue_in': queue_in,
            'queue_out': queue_out,
        }
        self.client = ''
        self.addr = addr
        self.LOG = logger
        self.connected = False
        self.heartbeat = heartbeat
        self.debug = debug

    def run_forever(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = client
        self.inputs = [client]

        while True:
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

        BUFF_SIZE = 1024
        timeout = 0.01

        try:
            while True:
                readable, writable, exceptional = select.select(
                    self.inputs, [], self.inputs, timeout)

                for server in exceptional:
                    server.close()
                    self.client.close()
                    self.LOG.error("Server maybe has closed!")
                    return

                # When timeout reached , select return three empty lists
                if not (readable):
                    #self.LOG.debug("No data recived!")
                    pass

                for server in readable:
                    if server == self.client:
                        try:
                            data = self.client.recv(BUFF_SIZE)
                            if data:
                                self.queue['queue_in'].put(data)
                                if self.debug:
                                    self.LOG.info("client get data: %s" % (data))

                            else:
                                self.client.close()
                                self.LOG.error("Server maybe has closed!")
                                return

                        except socket.error:
                            self.LOG.error("socket error, don't know why.")

        except KeyboardInterrupt:
            self.client.close()
            self.LOG.warn("Oh, you killed me...")
            sys.exit(0)

        except Exception as e:
            self.client.close()
            self.LOG.error("server socket closed. %s" % (e))

        finally:
            self.LOG.info("End!")

    def sendloop(self):
        try:
            while True:
                while self.connected != True:
                    pass

                if self.queue['queue_out'].empty():
                    if self.heartbeat:
                        time.sleep(self.heartbeat)
                        self.queue['queue_out'].put('1\n')
                else:
                    data = self.queue['queue_out'].get()
                    if self.debug:
                        self.LOG.yinfo(protocol_data_printB(data, title="client send date:" % (self)))
                    self.client.send(data)

        except KeyboardInterrupt:
            self.client.close()
            self.LOG.warn("Oh, you killed client send...")
            sys.exit(0)
