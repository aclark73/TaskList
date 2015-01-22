from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):
    '''
        The various request details are stored in instance variables:

    - client_address is the client IP address in the form (host,
    port);

    - command, path and version are the broken-down request line;

    - headers is an instance of mimetools.Message (or a derived
    class) containing the header information;

    - rfile is a file object open for reading positioned at the
    start of the optional input data part;

    - wfile is a file object open for writing.

    IT IS IMPORTANT TO ADHERE TO THE PROTOCOL FOR WRITING!

    The first thing to be written must be the response line.  Then
    follow 0 or more header lines, then a blank line, and then the
    actual data (if any).  The meaning of the header lines depends on
    the command executed by the server; in most cases, when data is
    returned, there should be at least one header line of the form

    Content-type: <type>/<subtype>

    where <type> and <subtype> should be registered MIME types,
    e.g. "text/html" or "text/plain".
    '''
    
    def do_GET(self):
        with open('issues.json') as f:
            self.wfile.writeln("Content-type: text/json")
            self.wfile.writeln()
            for line in f:
                self.wfile.write(line)

def run(HandlerClass = RequestHandler,
         ServerClass = HTTPServer, protocol="HTTP/1.0", port=8181):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the first command line
    argument).

    """
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
