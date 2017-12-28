#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os, sys, re, xmltodict, time
import subprocess

from APIs.common_APIs import my_system_no_check as _my_system_no_check


class WinNetwork():
    def __init__(self, ssid='cmcc'):
        self.ssid = ssid

    def win_wifi_connect(self, ssid, passwd='123456789', authentication='WPA2PSK', encryption='AES'):
        self.ssid = ssid
        self.profile = 'C:\\wifi_%s.xml' % (ssid)
        self.xml = xmltodict.parse('''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>xxxx</name>
    <SSIDConfig>
        <SSID>
            <name>xxxx</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>12345678</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
        ''')

        self.xml['WLANProfile']['name'] = ssid
        self.xml['WLANProfile']['SSIDConfig']['SSID']['name'] = ssid
        self.xml['WLANProfile']['MSM']['security']['authEncryption']['authentication'] = authentication
        self.xml['WLANProfile']['MSM']['security']['authEncryption']['encryption'] = encryption
        self.xml['WLANProfile']['MSM']['security']['sharedKey']['keyMaterial'] = passwd
        if passwd=='':
            self.xml['WLANProfile']['MSM']['security']['authEncryption']['authentication'] = 'open'
            self.xml['WLANProfile']['MSM']['security']['authEncryption']['encryption'] = 'none'
        
        with open(self.profile, 'w') as f:
            xmltodict.unparse(input_dict=self.xml, output=f)

        _my_system_no_check('netsh wlan add profile filename=%s' % (self.profile))
        time.sleep(1)
        _my_system_no_check('netsh wlan connect name=%s' % (self.ssid))
        time.sleep(5)

    def win_wifi_close(self):
        _my_system_no_check('netsh wlan disconnect')

    def win_wifi_clean(self):
        _my_system_no_check('netsh wlan delete profile *')

    def win_wifi_get_wifi_service_ipv4(self):
        output = _my_system_no_check('ipconfig')

        eths = re.split(r'\n+(?!\s)', output, re.S)

        for i in eths:
            i = i.strip()
            if re.search('wireless:.*192\.168\.10\.', i, re.S):
                print('=' * 20)
                print(i)
                ips = re.findall(r'(192\.168\.10\.\d+)', i, re.M)
                for ip in ips:
                    if ip != '192.168.10.1' and ip != '192.168.10.255':
                        return ip
            else:
                pass
        return None

    def win_ping_check(self, localip, remoteip='192.168.10.1'):
        output = _my_system_no_check('ping %s -S %s -n 1' % (remoteip, localip))
        print(output)
        if re.search(r'\(0\%', output, re.S):
            return 'pass'
        else:
            return 'fail'

    def win_wifi_get_ssids(self):
        _my_system_no_check('netsh wlan delete profile *')
        _my_system_no_check('netsh wlan refresh hostednetwork key')
        output = _my_system_no_check('netsh wlan show all')
        ssids = re.findall(r'^SSID\s*\d+\s*:\s*(\w+)', output, re.M)
        if ssids:
            return ssids
        else:
            return []


    def win_wifi_get_wire_service_ipv4(self):
        output = _my_system_no_check('ipconfig')

        eths = re.split(r'\n+(?!\s)', output, re.S)

        for i in eths:
            i = i.strip()
            if re.search('wire:.*192\.168\.10\.', i, re.S):
                print('=' * 20)
                print(i)
                ips = re.findall(r'(192\.168\.10\.\d+)', i, re.M)
                for ip in ips:
                    if ip != '192.168.10.1' and ip != '192.168.10.255':
                        return ip
            else:
                pass
        return None

    def win_interface_disabled(self, interface='wireless'):
        return _my_system_no_check('netsh interface set interface name=%s admin=disabled' % (interface))

    def win_interface_enabled(self, interface='wireless'):
        return _my_system_no_check('netsh interface set interface name=%s admin=enabled' % (interface))

    def win_interface_spead_get(self):
        return _my_system_no_check('wmic NIC where NetEnabled=true get Name, Speed')

    def win_execmd(self,cmd):
        return _my_system_no_check(cmd)


if __name__ == "__main__":
    obj=WinNetwork()
