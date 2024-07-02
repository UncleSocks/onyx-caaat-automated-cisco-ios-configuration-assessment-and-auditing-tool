import re
import os
from argparse import ArgumentParser
from maskpass import askpass
from ssh import ssh_send
from strings import logo, onyx_description, onyx_epilog


def arguments():
    
    argument_parser = ArgumentParser(prog = "ONYX", description = onyx_description(), epilog = onyx_epilog())
    argument_parser.add_argument('-v', '--version', type = int, default = None, help = "Cisco IOS version (15|17)")
    argument_parser.add_argument('-o', '--output', type = str, default = None, help = "HTML report filename with .html extension")
    argument_parser.add_argument('-t', '--type', type=str, default=None, help="Cisco hardware type (e.g., IOS, ASA)")
    argument = argument_parser.parse_args()

    return argument


def argument_checks(version_argument, html_agrument):

    def version_argument_check(version_argument):
        if version_argument == 15 or version_argument == 17:
            return
        else:
            raise ValueError('Error 0004 - Invalid IOS version, use -h for more information.')
    
    
    def html_argument_check(html_agrument):
        name, extension= os.path.splitext(html_agrument)

        if extension.lower() == ".html":
            return
        else:
            raise ValueError('Error 0005 - HTML filename has no or incorrect file extension, use -h for more information.')
        
    
    def argument_identifier(version_argument, html_agrument):
        if version_argument and html_agrument:
            version_argument_check(version_argument)
            html_argument_check(html_agrument)
        
        elif version_argument and html_agrument is None:
            version_argument_check(version_argument)
        
        elif version_argument is None and html_agrument:
            html_argument_check(html_agrument)
    
    argument_identifier(version_argument, html_agrument)


def user_input():
        
        logo()
        
        if (ip_address := os.environ.get("CAAAT_TARGET")) is None:
            ip_address = input("Target > ")

        if (username := os.environ.get("CAAAT_USERNAME")) is None:
            username = input("Username > ")

        if (password := os.environ.get("CAAAT_PASSWORD")) is None:
            password = askpass("Password > ")

        if (enable_password := os.environ.get("CAAAT_ENABLE_PASSWORD")) is None:
            enable_password = askpass("Enable # ")

        target_info = {'IP Address':ip_address, 'Username':username, 
                    'Password':password, 'Enable Password':enable_password}
        
        return target_info


def ios_version_check(connection):
    command = "show running-config | include version"
    command_output = ssh_send(connection, command)

    regex_pattern_ios_version_search = re.search(r'version\s+(?P<version>15|17)\S*(?=\n|\Z)', command_output)

    if regex_pattern_ios_version_search:
        version = regex_pattern_ios_version_search.group('version')
        if version == "15":
            ios_version = 15
        else:
            ios_version = 17

    else:
        version = None

    return ios_version


def cisco_type_check(connection):
    command = "show version | include Cisco"
    command_output = ssh_send(connection, command)

    regex_pattern_cisco_type_search = re.search(r'Cisco\s+(?P<type>IOS|Adaptive\s+Security\s+Appliance)\s+Software.*', command_output)

    if regex_pattern_cisco_type_search:
        cisco_type_match = regex_pattern_cisco_type_search.group('type')
        if cisco_type_match == "IOS":
            cisco_type = "ios"
        else:
            cisco_type = "asa"

    else:
        cisco_type = None
        
    return cisco_type