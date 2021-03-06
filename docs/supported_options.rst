.. _supported_options:

*******************
Supported Switches in Tortazo.
*******************

The following list is a summary of the core switches supported by Tortazo v1.1 and their usage.

=================
Simple Switches.
=================
The following is a list of single switches which doesn’t receive any value. These switches allows to activate features in Tortazo.

Common Switches for all modes
=============================
* **-v  /  --verbose**: Activates the debug mode. Shows debug, info and error messages. It’s very useful to see a full trace of actions performed by Tortazo and is recommended to use. However, in some cases this option shows many traces, for example, the plugin “BruterPlugin” uses Paramiko library to execute Brute Force attacks against relays and hidden services with an SSH Server up and running and Paramiko shows a very detailed information about every connection when the debug mode is active.
* **-U  / --use-localinstance**: Tortazo can start a new instance of TOR automatically using the switch “-T  /  --tor-localinstance”. Use the switch “-U  /  --use-localinstance” if you want to use the socks proxy and other settings defined in the instance started by Tortazo.

Switches for Gathering Information
=============================
* **-b  /  --brute**: Deprecated in v1.1. Replaced by the plugin “BruterPlugin”. Actually this switch is not supported
* **-d  /  --use-mirrors**: By default, Tortazo uses the authoritative directories of TOR and with this option, Tortazo will perform a connection with the mirrors of the authoritative directories to get the last consensus available.
* **-s  /  --use-shodan**: Allows to use ShodanHQ service to gather information about every relay found (up and running) in the descriptors downloaded from the TOR authorities or their mirrors up and running or stored in database. The switch “-k  /  --shodan-key” must be specified.
* **-c  /  --use-circuit-nodes**: Instructs to Tortazo to connect to a local instance of TOR through the control port of that instance instead of connect with authoritative directories or their mirrors. Any TOR client (i.e. TorBrowser) will connect with the authoritative directories to download the last consensus and build new virtual circuits with the TOR relays included in the descriptors. Tortazo use the information downloaded by that TOR instance (client) and will perform the actions specified by the other switches used. Note that the TOR instance should use the property “UseMicrodescriptors” with the value “0” in the “torrc” file used to start the instance. This is important to Tortazo, because in this way, the TOR instance will download the “Server Descriptors” from the authoritative directories instead of the “Micro Descriptors”. In recent versions of TOR, by default the client will download the “Micro Descriptors” with much less information about the relays in the network, this default behaviour should be overwritten and allows Tortazo to get as much information as he can from the descriptors downloaded. 

Switches for Database Mode
=============================
* **-D  /   --use-database**: Tortazo always stores in a SQLite database every scan performed against the relays found in the descriptors downloaded. This switch uses the records stored in database and avoids performing connections to the TOR authoritative directories. The option “-s  /  --scan-identifier” allows to specify the number of scan and recover the records associated with that scan identifier. The database is located in “<TORTAZO_DIR>/db/tortazo.db”.
* **-C  /  --clean-database**:  Deletes every record stored in the database.

Switches for Botnet Mode
=============================
* **-o  /  --open-shell**: This option is used in “Botnet Mode”, which is activated with the switch “-z   /  --zombie-mode” and allows to create a new interactive shell with the bot entered by the user.

Switches for Plugins management
=============================
* **-L / --list-plugins**: List of plugins loaded in Tortazo. Shows author, description, version, etc.


=================
Valued Switches.
=================
The following is a list of valued switches which receive arguments.

Common Switches for all modes
=============================
* **-T <path_to_torrc>  /  --tor-localinstance <path_to_torrc>**: Start a new local TOR instance with the "torrc" file specified. Usually, the user will specify the switch “-U  /  --use-localinstance” too.

Switches for Gathering Information
=============================
* **-n  <number_of_relays> /  --servers-to-attack <number_of_relays>**: The number of relays returned by the TOR authoritative directories usually is very large. The user uses this switch to specify the limit, a maximum number of relays which will be used by Tortazo. The default value is “10” if it’s not specified. Note that 10 relays is a very low value, the user should use this switch and specify a higher value.
* **-t  <number_of_threads>/  --theads<number_of_threads>**: Deprecated in v1.1. Replaced by the plugin “BruterPlugin”. Actually this switch is not supported.
* **-m <os>  /  --mode <os>**: Filter the platform (operative system) of the relay to attack. The accepted values are: "windows", "linux", "darwin", "freebsd", "openbsd", "bitrig","netbsd". Not case-sensitive.
* **-f  <password_file>  /  --passwords-file <password_file>**: Deprecated in v1.1. Replaced by the plugin “BruterPlugin”. Actually this switch is not supported.
* **-k <shodan_key_file>  /  --shodan-key <shodan_key_file>**:  Used with the “-s  /  --use-shodan” to perform queries with Shodan using the IP address of the relays found. This switch receives a text file, which contain a unique line with the developer key used by the Shodan API to perform queries. More info: https://developer.shodan.io/ 
* **-l  <list_of_ports>  /  --list-ports <list_of_ports>**: Comma-separated list of ports to scan with Nmap. The scan internally will use the Nmap switch “-p” to specify this list of ports.
* **-a <nmap_arguments>  /  --scan-arguments <nmap_arguments>**: Specify the arguments used by Nmap to perform every scan on the relays founded.
* **-e <relay_fingerprint>  /  --exit-node-fingerprint**: Specify an fingerprint to filter the exit nodes received in the dataset (Data from descriptors or Data in the local database.) If the fingerprint is not equals to any relay, Tortazo will finish without any result. This option should be used to perform direct attacks against a known exit node.
* **-i <controller_port>  /  --controller-port <controller_port>**: If the user want to perform connections against a TOR local instance to get and parse descriptors, should use the switch “-c  /  --use-circuit-nodes” as you’ve seen above. However, if the local instance uses a non-default controller port, this switch allows specifying it.

Switches for Database Mode
=============================
* **-S  <scan_identifier>  /  --scan-identifier <scan_identifier>**: Specify the scan identifier in the Scan table. Tortazo will use the relays related with the scan identifier specified with this switch. This switch should be used with the switch “-D  /  --use-database”.

Switches for Botnet Mode
=============================
* **-z <excluded_bots>  /  --zombie-mode <excluded_bots>**: Tortazo supports the Botnet mode over SSH. In this mode, Tortazo will read the file “tortazo_botnet.bot” located in “<TORTAZO_DIR>/tortazo_botnet.bot” where every line of the file is a SSH server compromised using the “BruterPlugin” against relays with SSH servers with usernames and passwords easy to guess. This switch enables the Botnet Mode and allows selecting the nicknames that will be excluded. (Nicknames included in the tortazo_botnet.bot). For instance, “-z Nickname1,Nickname2” excludes the bots with nicknames “Nickname1” and “Nickname2” and  “-z all” allows to include all nicknames in the Botnet Mode. In this mode, Tortazo will not perform any kind of query against the TOR authoritative directories, instead will try to execute parallel commands against the bots loaded. The user usually would like to specify the command to execute against the bots using the switch “-r <command>  /  --run-command <command>” or open an interactive shell with the switch “-o  /  --open-shell”.
* **-r <command> / --run-command <command>**: Execute a command across the hosts of the botnet. Requieres the -z/--zombie-mode. example: --run-command "uname -a; uptime" 

Switches for Plugins management
=============================
* **-P <plugin_name>  /  --use-plugin <plugin_name>**: Loads the interpreter for the specified plugin. The name of the plugin must be registered in Tortazo and the interpreter loaded will contain the functions and elements available in the plugin. This elements allows the interaction with the plugin and are easily accessible by IPython interpreter.
* **-A <plugin_args>  /  --plugin-arguments <plugin_args>**: Arguments to execute the specified plugin with the switch -P / --use-plugin. List of key/value pairs separated by colon. Used to overwrite the values of the config file for the project located in config/config.py. Example= nessusHost=127.0.0.1,nessusPort=8834,nessusUser=adastra,nessusPassword=adastra

Switches for Repository Mode
=============================
* **-R <serviceType> / --onion-repository <serviceType>**: Start Tortazo in Onion Repository Mode. The valid values are: HTTP, SSH, FTP and ONIONUP. The value "ONIONUP" tries to use the online service https://onionup.com/ to check if the onion addresses generated have an hidden service up and running.
* **-W <Number of workers> / --workers-repository <Number of workers>**: Number of processes used to process the ONION addresses generated.
* **-V <chars>  /   --validchars-repository <chars>**: Valid characters to use in the generation process of onion addresses. Default: All characters between a-z and digits between 2-7
* **-O <partialOnionAddress>  /   --onionpartial-address <partialOnionAddress>**: Partial address of a hidden service. Used in Onion repository mode.