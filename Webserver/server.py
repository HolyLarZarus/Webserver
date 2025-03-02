from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import os
import subprocess

class base_case(object):
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            mime_type = handler.get_mime_type(full_path)
            handler.send_content(content, mime_type)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'
    
class case_existing_file(base_case):
    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class case_no_file(base_case):
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.path))

class case_always_fail(base_case):
    def test(self, handler):
        return True

    def act(self, handler):
        raise Exception("Unknown object '{0}'".format(handler.path))

class case_directory_index_file(base_case):
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

class case_directory_no_index_file(base_case):
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
              not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_cgi_file(base_case):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        handler.run_cgi(handler.full_path)

class Handler(BaseHTTPRequestHandler):
    MIME_TYPES = {
        'html': 'text/html',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'txt': 'text/plain',
        'py': 'text/plain',
        '': 'application/octet-stream'  
    }
    Listing_Page = '''\
                <html>
            <head>
            </head>
            <body>
                <ul>
                    {0}
                </ul>
            </body>
            </html>
        '''
    Page = '''\
            <html>
            <body>
            <table>
            <tr>  <td>Header</td>         <td>Value</td>          </tr>
            <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
            <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
            <tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
            <tr>  <td>Command</td>        <td>{command}</td>      </tr>
            <tr>  <td>Path</td>           <td>{path}</td>         </tr>
            </table>
            </body>
            </html>
            '''
    Error_Page = """
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """
    Cases = [
        case_no_file(),
        case_cgi_file(),  
        case_existing_file(),
        case_directory_index_file(),
        case_directory_no_index_file(),
        case_always_fail()
    ]

    def get_mime_type(self, full_path):
        ending = os.path.splitext(full_path)[1].lstrip('.')
        return self.MIME_TYPES.get(ending, self.MIME_TYPES[''])
    
    def run_cgi(self, full_path):
        try:
            cmd = ["python", full_path]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True  # Für Textausgabe
            )
            stdout, stderr = proc.communicate()
            
            if proc.returncode != 0:
                raise Exception(f"CGI script error: {stderr}")
                
            self.send_content(stdout.encode('utf-8'))
            
        except Exception as e:
            self.handle_error(f"CGI execution failed: {str(e)}")

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content.encode('utf-8'), 404)

    def do_GET(self):
        try:
            self.full_path = os.path.join(os.getcwd(), self.path.lstrip("/"))
            
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        except Exception as msg:
            self.handle_error(str(msg))

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            # Erstelle klickbare Links für jedes Element
            bullets = [
                f'<li><a href="{os.path.join(self.path, e)}">{e}</a></li>'
                for e in entries if not e.startswith('.')
            ]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page.encode('utf-8'))
        except OSError as msg:
            self.handle_error(f"Verzeichnis kann nicht gelistet werden: {msg}")
        
    def create_page(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        return self.Page.format(**values)

    def send_content(self, content, mime_type='text/html', status=200):
        self.send_response(status)
        self.send_header("Content-type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), Handler)
    print("Server starting on port 8000...")
    server.serve_forever()