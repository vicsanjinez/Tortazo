# coding=utf-8
'''
Created on 22/01/2014

#Author: Adastra.
#twitter: @jdaanial

CommandAndControl.py

Reporting is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

Reporting is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Tortazo; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

from jinja2 import Environment, FileSystemLoader
import os
from stem.util import term
from config import config

#from data.TorNodeData import TorNodeData, TorNodePort

class Reporting:

    def __init__(self, cli=None):
        self.cli = cli

    def generateNmapReport(self, nodes, absolutePathFile):
        '''
        Generate NMap report.
        '''
        if self.cli:
            self.cli.logger.info(term.format("[+] Generating the NMAP Report in: "+absolutePathFile, term.Color.YELLOW))
        templateDir = config.resource_path(os.path.join('templates'))
        env = Environment(loader=FileSystemLoader(templateDir))
        template = env.get_template('nmapTemplate.html')
        templateVars = { "title" : "NMAP Report generated with Tortazo",
                         "nodes" : nodes}
        fd = open(absolutePathFile, 'w')
        fd.write(template.render(templateVars))
        fd.close()

    def generateShodanReport(self, shodanHosts, absolutePathFile):
        '''
        Generate Shodan Report.
        '''
        if self.cli:
            self.cli.logger.info(term.format("[+] Generating the Shodan Report in: "+absolutePathFile, term.Color.GREEN))
        #dir = os.path.dirname(os.path.abspath(__file__))
        #env = Environment(loader=FileSystemLoader(dir+'/templates'))
        templateDir = config.resource_path(os.path.join('templates'))
        env = Environment(loader=FileSystemLoader(templateDir))
        template = env.get_template('shodanTemplate.html')
        hosts = []
        for shodanHost in shodanHosts:
            if shodanHost is not None:
                hosts.append(shodanHost)

        #for shodanHost in shodanHosts:
        #    for key in shodanHost.results.keys():
        #        print key

        templateVars = { "title" : "Shodan Report generated with Tortazo", "ShodanHosts" : hosts, "APIInfo" : shodanHosts[0].keyInfo}
        fd = open(absolutePathFile, 'w')
        fd.write(template.render(templateVars).encode('utf-8'))
        fd.close()

    '''def compose(self,data):
        for key, value in data.iteritems():
            #if key == "data":
            #    self.processData(results)
            if type(value) == dict:
                self.compose(value)
            elif type(value) == list:
                for item in value:
                    if type(item) == dict:
                        self.compose(item)
                    else:
                        print "{0} : {1}".format(key, value)
                        self.results[key] = value
            print "{0} : {1}".format(key, value)
            self.results[key] = value
        return self.results
'''
    def extract(self, DictIn, Dictout):
        for key, value in DictIn.iteritems():
            if isinstance(value, dict): # If value itself is dictionary
                self.extract(value, Dictout)
            elif isinstance(value, list): # If value itself is list
                for i in value:
                    if type(i) == dict:
                        self.extract(i, Dictout)
                    else:
                        Dictout[i] = value
            else:
                Dictout[key] = value
    #def processData(self, data):


    '''def compose(self, data):
        results = {}
        if type(data) == dict:
            for key in data.keys():
                if type(key) == dict:
                    self.recursiveInfo(key)
                elif type(key) == list:
                    for element in key:
                        if type(key) == dict:
                            self.recursiveInfo(key)

                else:
                    results[key] = data[key]
        return results
    '''

'''
r = Reporting()
torNodeData = TorNodeData()
torNodePort = TorNodePort()
torNodePort.state='open'
torNodePort.reason='up and running'
torNodePort.name='ssh'
torNodePort.port=22
torNodeData.host = '90.98.110.220'
torNodeData.reason = 'Reason Test'
torNodeData.state = 'UP AND RUNNING '
torNodeData.nickName = 'NickTest'
torNodeData.openPorts.append(torNodePort)
r.generateNmapReport([torNodeData])
'''
#https://github.com/chrisglass/xhtml2pdf/blob/master/doc/usage.rst