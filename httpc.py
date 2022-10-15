import socket
import argparse
import sys
from urllib.parse import urlparse
import re

header_loc_regex = 'Location:(.*)\n'
html_status_code = 'HTTP\/[\d.]+\s(\d{3})'

def parse_commands(args):
    """Given a dict of command line arguments, return a dict with the HTTP req elements"""
    request = {}
    parsed_url = urlparse(args.URL)
    request['host'] = parsed_url.hostname
    # Default web port is 80
    request['port'] = 80 if parsed_url.port is None else parsed_url.port
    request['path'] = parsed_url.path
    if parsed_url.query != '':
        request['path'] += '?' + parsed_url.query
    request['type'] = args.request.upper()
    # If headers in arguments, join them in string dividing by line breaks
    request['headers'] = '\n' + '\n'.join(args.h) if args.h != '' else ''
    request['verbose'] = args.v
    if args.d:
        request['data'] = '\n' + '\n'.join(args.d) if args.d != '' else ''
    elif args.f:
        filepath ='\n' + '\n'.join(args.f)
        filepath2 = filepath.split('\n')[1]
        file = open(filepath2, "r")
        request['data'] = "\n"+file.read()
        file.close()



    return request


def send_request(req: dict):
    """Sends either GET or POST req to the specified server"""
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    status_code = '3'
    try:
        conn.connect((req['host'], req['port']))
        while status_code.startswith('3'):
            if req['type'].casefold() == "get".casefold():
                req_msg = f"{req['type']} {req['path']} HTTP/1.1\nHost: {req['host']}{req['headers']}\n\n"
                # print("REQUEST:\n" + req_msg)  # For testing purposes
            elif req['type'].casefold() == "post".casefold():
                req_msg = f"{req['type']} {req['path']} HTTP/1.1\nHost: {req['host']}{req['headers']}\nContent-Length:{(len(str(req['data'])))}\n{req['data']}\n"
                # print("REQUEST:\n" + req_msg)  # For testing purposes
            else:
                print("""Can not recognize request type keyword
                Please use either get or send""")

           # print("REQUEST:\n" + req)  # For testing purposes
            req_msg = req_msg.encode("utf-8")
            conn.sendall(req_msg)  # Sends req
            response = conn.recv(1024)  # Receive response, read up to 1024 bytes
            response = response.decode("utf-8")

            # If redirect
            status = re.search(html_status_code, response)
            status_code = status.group(1)
            # If response status is 3xx
            if status_code.startswith('3'):
                # Redirect to location in header. Recursive function
                new_location = re.search(header_loc_regex, response)
                if new_location:
                    parsed_relocation = urlparse(new_location.group(1))
                    req['path'] = parsed_relocation.path

        if not request['verbose']:
            response = response.split('\r\n\r\n')[1]  # Get just response body
        sys.stdout.write(response)
    finally:
        conn.close()


help_msg = """
httpc is a curl-like application but supports HTTP protocol only. 
Usage:
    httpc command [arguments]
The commands are:
    get executes a HTTP GET req and prints the response. 
    post executes a HTTP POST req and prints the response. 
    help prints this screen.
Use "httpc --help [command]" for more information about a command.
"""

request_help_msg = """
For GET requests: 
usage: httpc get [-v] [-h key:value] URL
Get executes a HTTP GET request for a given URL.
-v Prints the detail of the response such as protocol, status, and headers. 
-h key:value Associates headers to HTTP Request with the format 'key:value'.

For POST requests:
usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL
Post executes a HTTP POST request for a given URL with inline data or from file.
-v Prints the detail of the response such as protocol, status, and headers. 
-h key:value Associates headers to HTTP Request with the format 'key:value'. 
-d string Associates an inline data to the body HTTP POST request.
-f file Associates the content of a file to the body HTTP POST request.
Either [-d] or [-f] can be used but not both.
"""


parser = argparse.ArgumentParser(description=help_msg, add_help=False)
parser.add_argument("request", help=request_help_msg, choices=['post', 'get'])
parser.add_argument("URL", help="URL for request")
parser.add_argument('-H', '--help', action='help', help="Show help message")
parser.add_argument("-v", help="Return verbose response", action="store_true", default=False)
parser.add_argument("-h", help="Headers for request", nargs='*', default='')
parser.add_argument("-d", "--d", help="inline data for post request", nargs='*', default='')
parser.add_argument("-f", help="file for post request", nargs='*', default='')
arguments = parser.parse_args()

if arguments.request.casefold() == "get".casefold():

    if arguments.f or arguments.d:
        print("-d and -f arguments are only for Post request")
        exit(1)
else:
    if arguments.f == '' and arguments.d == '':
        print("Pass and argument for Post request, Have a look at -v and -f arguments")
    if arguments.f != '' and arguments.d != '':
        print("both -f and -d if arguments can not exist together")
        exit(1)
print("Arguments: ---->>>>> : " + str(arguments))  # For testing purposes



# if parser.f:
#     print("filename: {}".format(parser.f))
request = parse_commands(arguments)
send_request(request)
