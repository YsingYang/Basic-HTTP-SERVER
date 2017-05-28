from http.server import BaseHTTPRequestHandler, HTTPServer


# My handler
class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by return a fixed 'page'.'''

    Page = '''\
    <html>
        <body>
            <table>
                <tr> <td>Header</td> <td>Value</td>  </tr>
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
    #处理GET请求
    def do_GET(self):
        page = self.create_page()
        self.send_page(page)

        #send header


        #self.wfile.write(bytes(self.Page, 'UTF-8'))
        #python 3 这里改成wfile.write, 同时需要转换个字节流, 不能使用str进行传输

    def create_page(self):
        values = {
            'date_time' : self.date_time_string(),
            'client_host' : self.client_address[0], # ip_address
            'client_port' : self.client_address[1], # port
            'command' : self.command, #?
            'path' : self.path
        }
        page = self.Page.format(**values) # pagetype?
        #format 其实跟占位符差不多关系, 实际就是将占位符中的元素替换成参数元素
        return page

    def send_page(self, page):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, 'UTF-8'))


if __name__ == '__main__':
    serverAddr = ('', 8081)
    print('开始监听')
    server = HTTPServer(serverAddr,RequestHandler)
    print('开始循环')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
         pass
    server.server_close()
