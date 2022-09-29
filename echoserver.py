import socket
import argparse
import sys
from urllib.parse import urlparse


def run_client(request, url):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.connect((url.hostname, 80))
        request = f"{request} {url.path} HTTP/1.1\nHost: {url.hostname}\n\n"
        print(request)
        request = request.encode("utf-8")
        conn.sendall(request)
        # MSG_WAITALL waits for full request or error
        response = conn.recv(len(request), socket.MSG_WAITALL)
        sys.stdout.write("Replied: " + response.decode("utf-8"))
    finally:
        conn.close()


help_msg = """
httpc is a curl-like application but supports HTTP protocol only. 
Usage:
    httpc command [arguments]
The commands are:
    get executes a HTTP GET request and prints the response. 
    post executes a HTTP POST request and prints the response. 
    help prints this screen.
Use "httpc --help [command]" for more information about a command.
"""

# Usage: python httpc.py --host host --port port
parser = argparse.ArgumentParser(description=help_msg, add_help=False)
# parser.add_argument("--host", help="server host", default="localhost")
# parser.add_argument("--port", help="server port", type=int, default=80)
parser.add_argument("request", help="Type of request", choices=['post', 'get'])
parser.add_argument("URL", help="URL for request")
parser.add_argument('-H', '--help', action='help', help="Show help message")
parser.add_argument("-v", help="Return verbose response", action="store_true", default=False)
args = parser.parse_args()

parsed_url = urlparse(args.URL)
formatted_request = args.request.upper()
run_client(formatted_request, parsed_url)
