# coding=utf-8
'''
Created on 22/01/2014

#Author: Adastra.
#twitter: @jdaanial

Tortazo.py

Tortazo is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

Tortazo is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Tortazo; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

from plumbum import cli
from time import gmtime, strftime
from core.tortazo.Discovery import Discovery
from core.tortazo.WorkerThread import WorkerThread
from core.tortazo.BotNet import BotNet
from core.tortazo.Reporting import Reporting
import Queue
from stem.util import term
import stem.process
import logging as log
import config as tortazoConfiguration
from core.tortazo.databaseManagement.TortazoDatabase import  TortazoDatabase
import sys


#  ████████╗ ██████╗ ██████╗ ████████╗ █████╗ ███████╗ ██████╗ 
#  ╚══██╔══╝██╔═══██╗██╔══██╗╚══██╔══╝██╔══██╗╚══███╔╝██╔═══██╗
#     ██║   ██║   ██║██████╔╝   ██║   ███████║  ███╔╝ ██║   ██║
#     ██║   ██║   ██║██╔══██╗   ██║   ██╔══██║ ███╔╝  ██║   ██║
#     ██║   ╚██████╔╝██║  ██║   ██║   ██║  ██║███████╗╚██████╔╝
#     ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═════╝ 
#                                                              

#
#	Attack exit nodes of the TOR Network.
#	Author: Adastra.
#	http://thehackerway.com
#
#   TODO IN V1.1:
#   - Report issues to the administrator of the exitnode.
#   - Gather information about SNMP Devices.
#   - Upload and execute files to the compromised machines using SFTP and FTP.
#   - Check subterfuge: http://code.google.com/p/subterfuge/
#   - Allow 'windows', 'linux', 'bsd', and other filters. (Also, allow any type of OS.)
#   - Check what do bannergrab:  http://sourceforge.net/projects/bannergrab/
#   - GeoLocation, for example using: http://www.melissadata.com/lookups/iplocation.asp?ipaddress=46.17.138.212
#   - Use PyInstaller to generate an executable for Linux and Windows.
#   - Banner ArtAscii
#   - Plugin Arguments. Socks Settings, Start TOR Instance, etc.
#   - Develop unit tests using Python unittest.
#   - Plugin for Metasploit Framework.
#   - Plugin for Nikto.
#   - Plugin for NeXpose.
#   - Plugin: Deep Web Crawler: Crawler using Mechanize and scrapy to crawl hidden services in TOR. Crawl links, forms and store in database
#   - Plugin: Deep Web Finder: Compare sites in the clear web (from the relays found) with hidden services in TOR.
#   - Plugin: Deep Web Bruter: Find hidden directories in deep web sites using a custom list of directories or using FuzzDB project.
#   - Plugin: Deep Web Auth: Find protected resources using authentication (HTTP 401 code) and try to guess the username and password using custom lists of users and passwords or using FuzzDB project.


#    TODO FIXES:
#    - Report generated by Jinja2, align the column of ports in Nmap report.
#    - Using shodan with -s or -k shows a error message when there's no info about a relay. This shouldn't be a message error.
#    - Missing FingerPrint column in the TorNodeData table.
#    - Improve the bruteforce mode (-b switch) include SNMP and test deeply
#    - More tests about the W3AF and Nessus plugins.


class Cli(cli.Application):
    '''
    Command-Line options received.
    '''
    PROGNAME = "TORTAZO"
    AUTHOR = "Adastra"
    VERSION = "1.1"
    SEPARATOR = ':' #Separator for the dictionary (bruteforce attacks) for each line in the file, the user and password must be separated by colon. For Instance -> user:password
    verbose = cli.Flag(["-v", '--verbose'], help="Verbose Mode.")
    brute = cli.Flag(["-b", '--brute'], help="Brute Force Mode. (Specify -f/--passwords-file option to select the passwords file. Every line should contain the the username and password to test separated with a colon <USER>:<PASSWORD>)")
    useMirror = cli.Flag(["-d", '--use-mirrors'], help="Use the mirror directories of TOR. This will help to not overwhelm the official directories")
    useShodan = cli.Flag(["-s", '--use-shodan'], help="Use ShodanHQ Service. (Specify -k/--shodan-key to set up the file where's stored your shodan key.)")
    useCircuitExitNodes = cli.Flag(["-c", "--use-circuit-nodes"], help="Use the exit nodes selected for a local instance of TOR.")
    openShell = cli.Flag(["-o", "--open-shell"], excludes=["--mode"], requires=["--zombie-mode"],  help="Open a shell on the specified host.")
    useDatabase = cli.Flag(["-D", '--use-database'], help="Tortazo will store the last results from the scanning process in a database. If you use this flag, Tortazo will omit the scan and just will try use the data stored from the last execution.")
    cleanDatabase = cli.Flag(["-C", '--clean-database'], help="Tortazo will delete all records stored in database when finished executing. This option will delete every record stored, included the data from previous scans.")
    listPlugins = cli.Flag(["-L", '--list-plugins'], help="List of plugins loaded.")
    useLocalTorInstance = cli.Flag(["-U", '--use-localinstance'], help="Use a local TOR instance started with the option -T/--tor-localinstance (Socks Proxy included) to execute requests from the plugins loaded. By default, if you don't start a TOR local instance and don't specify this option, the settings defined in 'config.py' will be used to perform requests to hidden services.")	

    threads = 1 #Execution Threads.
    dictFile = None #Dict. file for brute-force attacks.
    exitNodesToAttack = 10 #Number of default exit-nodes to filter from the Server Descriptor file.
    shodanKey = None #ShodanKey file.
    scanPorts = "21,22,23,53,69,80,88,110,139,143,161,162,389,443,445,1079,1080,1433,3306,5432,8080,9050,9051,5800" #Default ports used to scan with nmap.
    scanArguments = None #Scan Arguments passed to nmap.
    exitNodeFingerprint = None #Fingerprint of the exit-node to attack.
    queue = Queue.Queue() #Queue with the host/open-port found in the scanning.
    controllerPort = '9151'
    zombieMode = None
    mode = None
    runCommand = None
    pluginManagement = None
    torLocalInstance = None
    scanIdentifier = None

    socksHost = None
    socksPort = None

    @cli.switch(["-n", "--servers-to-attack"], int, help="Number of TOR exit-nodes to attack. If this switch is used with --use-database, will recover information stored from the last 'n' scans. Default = 10")
    def servers_to_attack(self, exitNodesToAttack):
        '''
        Number of "exit-nodes" to attack received from command-line
        '''
        self.exitNodesToAttack = exitNodesToAttack

    @cli.switch(["-t", "--threads"], cli.Range(1, 20), help='Number of threads to use.')
    def number_threads(self, threads):
        '''
        Number of threads to create when the brute-force switches has been specified.
        '''
        self.threads = threads

    @cli.switch(["-m", "--mode"], cli.Set("windows", "linux", "darwin", "freebsd", "openbsd", "bitrig","netbsd", case_sensitive=False),  excludes=["--zombie-mode"] , help="Filter the platform of exit-nodes to attack.")
    def server_mode(self, mode):
        '''
        Server Mode: Search for Windows or Linux machines.
        '''
        self.mode = mode

    @cli.switch(["-f", "--passwords-file"], str, help="Passwords File in the Bruteforce mode.", requires=["--brute"])
    def passwords_file(self, dictFile):
        '''
        User's file. Used to perform bruteforce attacks.
        '''
        self.dictFile = dictFile

    @cli.switch(["-k", "--shodan-key"], str, help="Development Key to use Shodan API.", requires=["--use-shodan"])
    def shodan_key(self, shodanKey):
        '''
        This option is used to specify the file where the shodan development key is stored
        '''
        self.shodanKey = shodanKey

    @cli.switch(["-l", "--list-ports"], str, help="Comma-separated List of ports to scan with Nmap. Don't use spaces")
    def list_ports(self, scanPorts):
        '''
        List of ports used to perform the nmap scan.
        '''
        self.scanPorts = scanPorts

    @cli.switch(["-a", "--scan-arguments"], str, help='Arguments to Nmap. Use "" to specify the arguments. For example: "-sSV -A -Pn"')
    def scan_arguments(self, scanArguments):
        '''
        Arguments used to perform the nmap scan.
        '''
        self.scanArguments = scanArguments

    @cli.switch(["-e", "--exit-node-fingerprint"], str, help="ExitNode's Fingerprint to attack.")
    def exitNode_Fingerprint(self, exitNodeFingerprint):
        '''
        If we want to perform a single attack against an known "exit-node", We can specify the fingerprint of the exit-node to perform the attack.
        '''
        self.exitNodeFingerprint = exitNodeFingerprint

    @cli.switch(["-i", "--controller-port"], str, help="Controller's port of the local instance of TOR. (Default=9151)", requires=["--use-circuit-nodes"])
    def controller_port(self, controllerPort):
        '''
        Controller's Port. Default=9151
        '''
        self.controllerPort = controllerPort

    @cli.switch(["-z", "--zombie-mode"], str, help="This option reads the tortazo_botnet.bot file generated from previous successful attacks. With this option you can select the Nicknames that will be excluded. (Nicknames included in the tortazo_botnet.bot). For instance, '-z Nickname1,Nickname2' or '-z all' to include all nicknames.")
    def zombie_mode(self, zombieMode):
        '''
        Zombie mode to execute commands across the compromised hosts.
        '''
        if zombieMode == None:
            self.zombieMode = ""
        self.zombieMode = zombieMode

    @cli.switch(["-r", "--run-command"], str, excludes=["--mode"], requires=["--zombie-mode"],  help='Execute a command across the hosts of the botnet. Requieres the -z/--zombie-mode. example: --run-command "uname -a; uptime" ')
    def run_command(self, runCommand):
        '''
        Command to execute across the compromised hosts.
        '''
        self.runCommand = runCommand

    @cli.switch(["-P", "--use-plugin"], str, help='Execute a plugin (or list) included in the plugins directory. for instance: "-P simplePlugin:simplePrinter,argName1=arg1,argName2=arg2,argNameN=argN;anotherSimplePlugin:anotherSimpleExecutor,argName1=arg1,argName2=arg2,argNameN=argN" where simplePlugin is the module, simplePrinter is a class which inherites from BasePlugin class and argName1=argValue1,argName2=argValue2,argNameN=argValueN are arguments used for this plugin. Multiple plugins should be separated by ";" and you can get the help banner for a plugin executing "pluginName:help". Check the documentation for more detailed information')
    def plugin_management(self, pluginManagement):
        '''
        Plugin Management.
        '''
        self.pluginManagement = pluginManagement

    @cli.switch(["-T", "--tor-localinstance"], str, help='Start a new local TOR instance with the "torrc" file specified. DO NOT RUN TORTAZO WITH THIS OPTION AS ROOT!')
    def tor_localinstance(self, torLocalInstance):
        '''
        TOR Local Instance.
        '''
        self.torLocalInstance = torLocalInstance

    @cli.switch(["-S", "--scan-identifier"], int, requires=["--use-database"],  help="scan identifier in the Scan table. Tortazo will use the relays related with the scan identifier specified with this option.")
    def scan_identifier(self, scanIdentifier):
        '''
        Scan Identifier. Tortazo will use the relays associated with this scan. (Relation between the Scan and TorNodeData tables.)
        '''
        self.scanIdentifier = scanIdentifier


    def logsTorInstance(self, log):
        '''
        Shows the Logs for the TOR startup.
        '''
        if "Bootstrapped " in log:
            self.logger.debug(term.format(log, term.Color.GREEN))

    def main(self):
        '''
        Initialization of logger system.
        '''

        self.logger = log
        self.exitNodes = []
        self.database = TortazoDatabase()

        if self.verbose:
            self.logger.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
            self.logger.debug(term.format("[+] Verbose mode activated.", term.Color.GREEN))
        else:
            self.logger.basicConfig(format="%(levelname)s: %(message)s", level=log.WARN)
        self.logger.info(term.format("[+] Process started at " + strftime("%Y-%m-%d %H:%M:%S", gmtime()), term.Color.YELLOW))

        if self.listPlugins:
            '''import glob
            plugins = glob.glob("plugins/*.py")
            plugins.remove('plugins/__init__.py')

            print "[*] Plugins list... "
            for plugin in plugins:
                pluginModule = plugin.replace(".py", "").replace(".pyc", "").replace('/', '.')
                import pyclbr
                moduleReaded = pyclbr.readmodule(pluginModule)
                for k, v in moduleReaded.items():
                    mod = __import__(pluginModule)
                    fullClassName = pluginModule+"."+v.name
                    components = fullClassName.split('.')
                    for comp in components[1:]:
                        mod = getattr(mod, comp)
                    inst = mod([])
                    print "Plugin Name: %s" %(inst.name)
                    print "Plugin Description: %s" %(inst.desc)
                    print "Plugin Version: %s" %(inst.version)
                    print "Plugin Author: %s" %(inst.author)
                    print "\n"
            '''
            print "[*] Plugins list... "
            import pluginsDeployed
            for plugin in pluginsDeployed.plugins.keys():
                completeModulePath = pluginsDeployed.plugins.get(plugin)
                pluginModule = completeModulePath[:completeModulePath.rfind(".")]
                module = __import__(pluginModule)
                components = completeModulePath.split('.')
                for comp in components[1:]:
                    module = getattr(module, comp)
                inst = module([])
                print "Plugin Name: %s" %(inst.name)
                print "Plugin Description: %s" %(inst.desc)
                print "Plugin Version: %s" %(inst.version)
                print "Plugin Author: %s" %(inst.author)
                print "\n"
            return

        if self.torLocalInstance:
            self.logger.info(term.format("[+] Starting TOR Local instance with the following options: ", term.Color.YELLOW))
            import os.path
            if os.path.exists(self.torLocalInstance) and os.path.isfile(self.torLocalInstance):
                torrcFile = open(self.torLocalInstance,'r')
                torConfig = {}
                for line in torrcFile:
                    if line.startswith("#", 0, len(line)) is False and len(line.split()) > 0:
                        torOptionName = line.split()[0]
                        if len(line.split()) > 1:
                            torOptionValue = line[len(torOptionName)+1 : ]
                        torConfig[torOptionName] = torOptionValue
                try:
                    for config in torConfig.keys():
                        self.logger.info(term.format("[+] Config: %s value: %s " %(config, torConfig[config]), term.Color.YELLOW))
                    torProcess = stem.process.launch_tor_with_config(config = torConfig, init_msg_handler=self.logsTorInstance)
                    if torProcess > 0:
                        self.logger.debug(term.format("[+] TOR Process created. PID %s " %(torProcess.pid),  term.Color.GREEN))
                        self.socksHost = torConfig['SocksListenAddress']
                        self.socksPort = torConfig['SocksPort']
                        #If SocksListenAddress or SocksPort properties are empty but the process has been started, the socks proxy will use the default values.
                        if self.socksHost is None:
                            self.socksHost = '127.0.0.1'
                        if self.socksPort is None:
                            self.socksPort = '9150'
                except OSError, ose:
                    print sys.exc_info()
                    #OSError: Stem exception raised. Tpically, caused because the "tor" command is not in the path.
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    self.logger.warn(term.format("Exception raised during the startup of TOR Local instance.... "+str(ose), term.Color.RED))
                    self.logger.warn(term.format("Details Below: \n", term.Color.RED))
                    self.logger.warn(term.format("Type: %s " %(str(exc_type)), term.Color.RED))
                    self.logger.warn(term.format("Value: %s " %(str(exc_value)), term.Color.RED))
                    self.logger.warn(term.format("Traceback: %s " %(str(exc_traceback)), term.Color.RED))


        if self.zombieMode is None and self.useDatabase is False and self.mode is None:
            self.logger.warn(term.format("Specify the execution mode. You should use Info Gathering (-m), Botnet Mode (-z) or Database Mode (-D). Type '--help' to see the available options. ", term.Color.RED))
            return

        #self.loadAndExecute(self,"simplePlugin:simplePrinter")
        '''
            List and Scan the exit nodes. The function will return an dictionary with the exitnodes found and the open ports.
            THIS PROCESS IS VERY SLOW AND SOMETIMES THE CONNECTION WITH THE DIRECTORY AUTHORITIES IS NOT AVAILABLE.
        '''
        if self.zombieMode:
            '''
            In zombie mode, The program should read the file named "tortazo_botnet.bot".
            In that file, every line have this format: host:user:password:nickname
            Extract every host and then, create a list of bots.
            '''
            botnet = BotNet(self)
            botnet.start()


        else:
            discovery = Discovery(self)

            if self.useDatabase:
                #There's a previous scan stored in database. We'll use that information!
                if self.scanIdentifier is None:
                    self.logger.info(term.format("[+] Getting the last %s scans executed from database..."  %(self.exitNodesToAttack),  term.Color.YELLOW))
                    self.logger.debug(term.format("[+] Use -n/--servers-to-attack option to include more or less records from the scans recorded in database.",  term.Color.GREEN))
                    self.exitNodes = self.database.searchExitNodes(self.exitNodesToAttack, None)
                else:
                    self.logger.info(term.format("[+] Getting the relays for the scan %d ..."  %(self.scanIdentifier),  term.Color.YELLOW))
                    self.exitNodes = self.database.searchExitNodes(self.exitNodesToAttack, self.scanIdentifier)

                if len(self.exitNodes) > 0:
                    self.logger.info(term.format("[+] Done!" , term.Color.YELLOW))
                else:
                    if self.scanIdentifier is None:
                        self.logger.info(term.format("[+] No records found... You should execute an initial scan." , term.Color.YELLOW))
                        self.logger.warn(term.format("[-] You've chosen to use the database records, however the database tables are empty because you have not run an initial scan." , term.Color.RED))
                        self.logger.warn(term.format("[-] Tortazo just saves the relays found in the last scan. Previous scans always will be deleted." , term.Color.RED))
                    else:
                        self.logger.warn(term.format("[+] No records found with the scan identifier specified, check the database..." , term.Color.RED))
                    return
            else:
                if self.useCircuitExitNodes:
                    #Try to use a local instance of TOR to get information about the relays in the server descriptors.
                    self.exitNodes = discovery.listCircuitExitNodes()
                elif self.mode:
                    #Try to connect with the TOR directories to get information about the relays in the server descriptors.
                    self.exitNodes = discovery.listAuthorityExitNodes() #Returns a list of TorNodeData objects

            if self.exitNodes is not None and len(self.exitNodes) > 0:
                reporter = Reporting(self)
                reporter.generateNmapReport(self.exitNodes, tortazoConfiguration.NmapOutputFile)
                self.shodanHosts = []
                for torNode in self.exitNodes:
                    if self.brute:
                        self.queue.put(torNode)
                    #If shodan is activated, let's try to gather some information for every node found.
                    if self.useShodan == True:
                        #Using Shodan to search information about this machine in shodan database.
                        self.logger.info(term.format("[+] Shodan Activated. About to read the Development Key. ", term.Color.YELLOW))
                        if self.shodanKey == None:
                            #If the key is None, we can't use shodan.
                            self.logger.warn(term.format("[-] Shodan Key's File has not been specified. We can't use shodan without a valid key", term.Color.RED))
                        else:
                            #Read the shodan key and create the Shodan object.
                            try:
                                shodanKeyString = open(self.shodanKey).readline().rstrip('\n')
                                shodanHost = discovery.shodanSearchByHost(shodanKeyString, torNode.host)
                                self.shodanHosts.append(shodanHost)
                            except IOError, ioerr:
                                self.logger.warn(term.format("[-] Shodan's key File: %s not Found." %(self.shodanKey), term.Color.RED))

                if len(self.shodanHosts) > 0:
                    reporter.generateShodanReport(self.shodanHosts, tortazoConfiguration.ShodanOutputFile)

                #Check if there's any plugin to execute!
                if self.pluginManagement != None:
                    self.loadAndExecute(self.pluginManagement, self.exitNodes)

                #Block until the queue is empty.
                if self.brute:
                    for thread in range(self.threads): #Creating the number of threads specified by command-line.
                        worker = WorkerThread(self.queue, thread, self)
                        worker.setDaemon(True)
                        worker.start()
                    self.queue.join()

                if self.cleanDatabase:
                    self.logger.info(term.format("[+] Cleaning database... Deleting all records.", term.Color.YELLOW))
                    self.database.initDatabase()
                    self.database.cleanDatabaseState()
        self.logger.info((term.format("[+] Process finished at "+ strftime("%Y-%m-%d %H:%M:%S", gmtime()), term.Color.YELLOW)))

    def loadAndExecute(self, listPlugins, torNodesFound):
        #simplePlugin:simplePrinter
        if listPlugins is None:
            self.logger.warn((term.format("[-] You should specify a plugin with the option -P/--use-plugin", term.Color.YELLOW)))
            return
        '''pluginModule, pluginClass = listPlugins.split(":")
        if pluginModule is None or pluginClass is None:
            self.logger.info((term.format("[-] Format "+ listPlugins +" invalid. Check the documentation to use plugins in Tortazo", term.Color.YELLOW)))
            return
        '''
        try:
            '''module = __import__("plugins."+pluginModule)
            pluginArguments = pluginClass.split(',')
            pluginClassName = pluginArguments[0]
            components = ("plugins."+pluginModule+"."+pluginClassName).split('.')
            '''
            import pluginsDeployed
            self.logger.debug((term.format("[+] Loading plugin...", term.Color.GREEN)))

            if pluginsDeployed.plugins.__contains__(listPlugins):
                completeModulePath = pluginsDeployed.plugins.get(listPlugins)
                pluginModule = completeModulePath[:completeModulePath.rfind(".")]
                module = __import__(pluginModule)
                components = completeModulePath.split('.')
                for comp in components[1:]:
                    module = getattr(module, comp)
                if self.socksHost is not None and self.socksPort is not None and self.useLocalTorInstance:
                    reference = module(torNodesFound)
                    reference.setSocksProxySettings(self.socksHost, self.socksPort)
                    reference.runPlugin()
                else:
                     reference = module(torNodesFound)
                reference.runPlugin()
                self.logger.debug((term.format("[+] Done!", term.Color.GREEN)))
            else:
                self.logger.warn((term.format("[-] The plugin specified is unknown... Check the available plugins with -L/--list-plugins option", term.Color.RED)))

        except ImportError, importErr:
            print "Unexpected error:", sys.exc_info()
            self.logger.warn((term.format("[-] Error loading the class. Your plugin class should be located in 'plugins' package and registered in pluginsDeployed.py. Check the available plugins with -L/--list-plugins option", term.Color.RED)))
        except AttributeError, attrErr:
            print "Unexpected error:", sys.exc_info()
            self.logger.warn((term.format("[-] Error loading the class. Your plugin class should be located in 'plugins' package and registered in pluginsDeployed.py. Check the available plugins with -L/--list-plugins option", term.Color.RED)))


    '''
    def loadAndExecute(self, listPlugins, torNodesFound):
        #Load and execute external rutines (plugins)
        #simplePlugin:simplePrinter,argName1=arg1,argName2=arg2,argNameN=argN;anotherSimplePlugin:anotherSimpleExecutor,argName1=arg1,argName2=arg2,argNameN=argN
        if listPlugins is None:
            self.logger.warn((term.format("[-] You should specify a list of plugins with the option -P/--use-plugins", term.Color.YELLOW)))
            return
        plugins = listPlugins.split(";")
        for plugin in plugins:
            pluginModule, pluginClass = plugin.split(":")
            if pluginModule is None or pluginClass is None:
                self.logger.info((term.format("[-] Format "+ listPlugins +" invalid. Check the documentation to use plugins in Tortazo", term.Color.YELLOW)))
                return
            try:
                module = __import__("plugins."+pluginModule)
                pluginArguments = pluginClass.split(',')
                pluginClassName = pluginArguments[0]
                pluginArguments.remove(pluginClassName)
                components = ("plugins."+pluginModule+"."+pluginClassName).split('.')
                self.logger.debug((term.format("[+] Loading plugin...", term.Color.GREEN)))
                for comp in components[1:]:
                    module = getattr(module, comp)
                reference = module()
                reference.setNodes(torNodesFound)
                self.logger.debug((term.format("[+] Done!", term.Color.GREEN)))
                self.logger.debug((term.format("[+] Parsing the arguments for the plugin...", term.Color.GREEN)))
                pluginArgumentsToSet = {}
                for arg in pluginArguments:
                    argumentItem = arg.split('=')
                    argumentName = argumentItem[0]
                    argumentValue = argumentItem[1]
                    self.logger.debug((term.format("[+] Argument Name %s with value %s" %(argumentName, argumentValue), term.Color.GREEN)))
                    if argumentValue is None:
                        self.logger.warn((term.format("[-] Error: Argument Name %s without value... " %(argumentName), term.Color.RED)))

                    pluginArgumentsToSet[argumentName] = argumentValue
                reference.setPluginArguments(pluginArgumentsToSet)
                reference.runPlugin()
            except ImportError, importErr:
                print importErr
                self.logger.warn((term.format("[-] Error loading the class. Your plugin class should be located in 'plugins' package. Check if "+pluginModule+"."+pluginClass+" exists", term.Color.RED)))

    '''
if __name__ == "__main__":
    '''
    Start the main program.
    '''
    Cli.run()
