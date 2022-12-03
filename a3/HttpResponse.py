from datetime import datetime
import os


def status_phrase(code):
    if code == 200:
        return 'OK'
    if code == 201:
        return 'Created'
    if code == 202:
        return 'Accepted'
    if code == 204:
        return 'No Content'
    if code == 400:
        return 'Bad Request'
    if code == 403:
        return 'Forbidden'
    if code == 404:
        return 'Not Found'
    if code == 500:
        return 'Internal Server Error'


def write_file(path, body):
    path = path + ".txt"
    status = 201  # Default is file created
    if os.path.isfile(path):
        status = 200
    try:
        file = open(path, 'w')
        file.write(body)
        file.close()
    except FileNotFoundError:
        status = 404
        print("File was not found")
    except IOError:
        status = 500
        print("Unable to create/write file.")
    return status


def is_valid_path(basedir, path, request_type, verbose=False):
    requested_path = os.path.realpath(basedir + path)
    if verbose:
        print("REQUEST PATH: " + basedir + path)
        print("Real path: " + requested_path)
        print("Is path file====>>> " + str(os.path.isfile(requested_path)))
        print("Is dir file====>>> " + str(os.path.isdir(requested_path)))
    valid = True
    if request_type == "get":
        if not (os.path.isfile(requested_path + ".txt") or os.path.isdir(requested_path)):
            valid = False
    return basedir == os.path.commonpath((basedir, requested_path)) and valid


def create_response(data, path, verbose=False):
    first_line = data.split(' ')[:2]
    method = first_line[0]
    request_path = first_line[1]
    now = datetime.utcnow()
    date = f"{now.strftime('%a %d %b %Y %H:%M:%S')} GMT"
    response = ""
    if verbose:
        print(f"Date is {date}")
        print("+++++ Request is +++++")
        print(data)
        print("+++++")

    try:
        if verbose:
            print("____________>>>>>>>>>>>>>>" + str(is_valid_path(path, request_path, method)))
        if is_valid_path(path, request_path, method, verbose):
            print("{{{{{{{{{}}}}}}}}}}}}}}}}}}}}}")

            if method.casefold() == "get".casefold():
                status = 200
                bar = data.split(' ')[1]

                if os.path.isfile(path + bar + ".txt"):
                    wanted_file = path + bar + ".txt"
                    f = open(wanted_file, "r")
                    content = f.read()
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(content)}\r\n\n{content}\r\n\r\n"
                elif os.path.isdir(path + bar):
                    content = os.listdir(path + bar)
                    if verbose:
                        print("Contents of directory are:")
                        print(content)
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nConnection: close\r\nContent-Length: {len(str(content))}\r\n\n{content}\r\n\r\n"
                else:
                    status = 400
                    response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"

            elif method.casefold() == "post".casefold():
                body = data.split('\n\n')[1]
                path = path + request_path
                status = write_file(path, body)
                response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"
        else:
            status = 403
            if not os.path.isdir(os.path.realpath(path + request_path)):
                status = 400
            response = f"HTTP/1.0 {status} {status_phrase(status)}\r\nDate: {date}\r\nConnection: close\r\n\r\n"
    except Exception as e:
        print("Error: ", e)
    return response.encode("utf-8")


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


port_help = """
Specifies the port number that the server will listen and serve at.
Default is 8080.
"""

directory_help = """
Specifies the directory that the server will use to read/write requested
files. 
Default is the current directory when launching the application.
"""