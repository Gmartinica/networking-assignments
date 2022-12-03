import sys
from datetime import datetime


def create_request(req: dict):
    """Returns either GET or POST request based on dict input"""
    # If GET request
    req_msg = ""
    if req['type'].casefold() == "get".casefold():
        req_msg = f"{req['type']} {req['path']} HTTP/1.0\nHost: {req['host']}{req['headers']}\n\n"
    # If post request, send content length and data
    elif req['type'].casefold() == "post".casefold():
        req_msg = f"{req['type']} {req['path']} HTTP/1.0\nHost: {req['host']}{req['headers']}\nContent-Length:{(len(str(req['data'])))}\n\n{req['data']}\n"
    else:
        print("""Can not recognize request type keyword
        Please use either get or send""")

    req_msg = req_msg.encode("utf-8")
    return req_msg


def read_response(res: str, verbose=False, out_file=None):
    """Given HTTP response, output to terminal or to file"""
    if not verbose:
        response = res.split('\r\n\n')[1]  # Get just response body
    if not out_file:
        sys.stdout.write(res)
    # Write output to file
    else:
        try:
            out = open(out_file, "a")  # append mode
            out.write("-----------------------------\n")
            out.write(response)
            out.write("\n______________________________\n")
            out.close()

        except IOError:
            # dd-mm-YY_H.M.S
            outFilename = datetime.now().strftime("%d-%m-%Y_%H.%M.%S.txt")
            try:
                out = open(outFilename, "a")  # append mode
                out.write("-----------------------------\n")
                out.write(response)
                out.write("\n______________________________\n")
                out.close()
            except IOError:
                print("Could not create the output file")


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