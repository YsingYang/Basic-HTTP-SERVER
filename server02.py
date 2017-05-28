from http.server import BaseHTTPRequestHandler, HTTPServer

import sys, os, subprocess

#-------------------------------------------
class ServerException(Exception):
    '''For internal error reporting'''
    pass
#-------------------------------------------

#-------------------------------------------
# 将handle基类抽象出来
class baseCase(object):
    '''Parent for case handlers'''
    #将原先在Handler类的方法放在此处, 为什么这样设计?
    def handleFile(self, handler, fullPath):
        try:
            with open(fullPath, 'rb') as reader:
                content = reader.read()
            handler.sendContent(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: '{1}'".format(fullPath, msg)
            handler.handlError(msg)

    def indexPath(self, handler):
        return os.path.join(handler.fullPath, 'index.html')

    def test(self, handler):
        assert False, 'Not implemented'

    def action(self, handler):
        assert  False, 'Not implemented'

#-------------------------------------------



#-------------------------------------------
class caseNoFile(baseCase):
    '''File or directory does not'''
    def test(self, handler):
        return not os.path.exists(handler.fullPath)

    def action(self, handler):
        raise ServerException("'{0}' not found in path".format(handler.fullPath))

#-------------------------------------------
class caseCGIFile(baseCase):

    def runCGI(self, handler):
        cmd = 'python3 ' + handler.fullPath
        childStdout = os.popen(cmd)
        data = childStdout.read()
        childStdout.close()
        handler.sendContent(data)


    def test(self, handler):
        return os.path.isfile(handler.fullPath) and handler.fullPath.endswith('.py')
    #是否存在后缀名为.py的文件
    def action(self, handler):
        self.runCGI(handler)



#-------------------------------------------

class caseIndexFile(baseCase):

    def test(self, handler):
        return os.path.isdir(handler.fullPath)\
            and os.path.isfile(self.indexPath(handler))

    def action(self, handler):
        self.handleFile(handler, self.indexPath(handler))
#--------------------------------------------

class caseNoIndexFile(baseCase):
    ListingPage = '''\
        <html>
            <body>
                <ul>
                    {0}
                </ul>
            </body>
        </html>
        '''
    def listDir(self, handle, fullPath):
        try:
            entries = os.listdir(fullPath)#传入的是一个存在的path
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            #bullets为目录文件, 生成当前目录下文件列表
            page = self.ListingPage.format('\n'.join(bullets))
            #相当于list.join
            handle.sendContent(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)#读取路径, 而不是fullpath
            handle.handleError(msg)


    def test(self, handler):#有相应目录但没有index.html
        return os.path.isdir(handler.fullPath)\
            and not os.path.isfile(self.indexPath(handler))

    #做出相应的action
    def action(self, handler):
        self.listDir(handler, handler.fullPath)



#-------------------------------------------
class caseFileExist(baseCase):
    def test(self, handler):
        return os.path.isfile(handler.fullPath)#如果路径存在, 且为文件

    def action(self, handler):
        self.handleFile(handler, handler.fullPath)

#-------------------------------------------

class caseError(baseCase):
    def test(self, handler):
        return True

    def action(self, handler):
        raise ServerException("Unknown Object {0}".format(handler.fullPath))



# My handler
class RequestHandler(BaseHTTPRequestHandler):
    '''Handle HTTP requests by return a fixed 'page'.'''

    Error_Page = '''\
    <html>
        <body>
            <h1>Error accessing {path}</h1>
            <p>{msg}</p>
        </body>
    </html>
    '''

    #处理GET请求

    #存入相应的object对象. 里面的不是函数!!!
    Cases = [caseNoFile(), caseCGIFile(), caseFileExist(), caseIndexFile(), caseNoIndexFile(), caseError()]

    def do_GET(self):
        try:
            self.fullPath = os.getcwd() + self.path
            #os.getcwd()  方法用于返回当前工作目录,

            # self.path = 指的是网页后/指定的文件

            for case in self.Cases:
                if(case.test(self)):
                    case.action(self)
                    break
                    #记得加上break, 不然最后一个casehandle扔会处理


        #handle exception
        except Exception as msg:
            self.handleError(msg)



    def handleError(self, msg):
        content = self.Error_Page.format(path = self.path, msg = msg)
        self.sendContent(content, 404)
        #发送相应状态码

    def sendContent(self, content, status = 200):
        print('Sending Content')
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        if type(content) == bytes:
            self.wfile.write(content)
        else:
            self.wfile.write(bytes(content, 'UTF-8'))




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
