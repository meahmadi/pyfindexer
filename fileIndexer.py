# -*- coding: utf-8 -*
from __future__ import unicode_literals
import sys,getopt
import time
import logging
import os
import ast
import re
import codecs
from miette import DocReader
from stat import *


from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler,FileSystemEventHandler

from docx import opendocx, getdocumenttext
import atexit,signal

from pyHarir import PyHarir

GENERAL = "General"
CLASS = "FileIndexItem"
CURDIR = "$:"
encoding = None

def logline(log):
    global logger
    logger.write(log)
    logger.write("\n")
    logger.flush()

def logChanges():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[2] if len(sys.argv) > 2 else '.'
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def repairPath(fpath):
    fpath = fpath.replace("\\","/")
    fpath = fpath.replace("//","/")
    return fpath

class Indexer(object):
    def __init__(self,paths,dbpath,rootIndex,lastAccessTime):
        global filesQueue,harir
        
        self.dbpath = dbpath
        self.queue = filesQueue
        self.paths = paths
        
        
        self.harir = PyHarir(self.dbpath)
        harir = self.harir

        if lastAccessTime == 0:
            lastAccessTime = self.harir.value("FILEINDEXER","Config","lastAccessTime")
            lastAccessTime = ast.literal_eval(lastAccessTime) if lastAccessTime is not None else 0
        
        self.toCrawlPaths = []
        p = self.harir.value("FILEINDEXER","Config","InitializedPaths")
        oldPaths = p.split(";") if p is not None else []
        for p in self.paths:
            fpath = os.path.abspath(p)
            url = self.urlOf(fpath)
            if rootIndex and p not in oldPaths:
                self.queue.append({"type":"walktree","event":None,"url":url,"src_path":fpath})
                self.toCrawlPaths.append(p)
            else:
                lastChangedFiles = self.filesLaterThan(fpath, lastAccessTime, [".docx",".doc",".html",".txt",".tex"])
                for f in lastChangedFiles:
                    furl = self.urlOf(f) 
                    self.queue.append({"type":"modified","event":None,"url":furl,"src_path":f})

    def filesLaterThan(self,rootfolder, acctime, suffixes):
        def conditions(name,time,suff):
            try:
                return (os.stat(name).st_mtime>time) and ( (len(suff) == 0) or (os.path.splitext(name)[-1] in suff ))
            except:
                return False 
        return (os.path.join(dirname, filename) 
         for dirname, dirnames, filenames in os.walk(unicode(rootfolder))
         for filename in filenames
         if conditions(os.path.join(dirname,filename), acctime,suffixes))
        
    def nodeOf(self,url):
        nodes = self.harir.findMatch(CLASS,"lurl",url)
        return nodes[0][0] if len(nodes)>0 else None

    def urlOf(self,fpath):
        global currentDrive,CURDIR
        fpath = repairPath(fpath)
        url = fpath
        if currentDrive is not None and fpath.startswith(currentDrive):
            url = CURDIR+fpath[2:]
        return url

    def readRawFile(self,path):
        global encoding
        logline("\t\treading raw:%s"%path)
        try:
            data = open(path, 'rb').read()
            if encoding is None:
                try:
                    from chardet import detect
                except ImportError:
                    detect = lambda x: {'encoding': 'utf-8'}
                encoding = detect(data)['encoding']
            data = data.decode(encoding)
            return data
        except:
            logline( "Unexpected error while reading raw file:%s"% sys.exc_info()[0])

    def unescapeXml(self,content):
        def replaceEntities(s):
            s = s.group(1)
            if s[0] == "#": 
                return charref(s[1:])
            else: return entityref(s)
        r_unescape = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")
        return r_unescape.sub(replaceEntities, content)
    def unescape(s):
        return r_unescape.sub(replaceEntities, s)
    def readDocxContent(self,path):
        logline("\t\treading docx:%s"%path)
        document = opendocx(path)
        paratextlist = getdocumenttext(document)
        #return '\n\n'.join([paratext.encode("utf-8") for paratext in paratextlist])
        return '\n\n'.join(paratextlist)
    
    def updateFileProperties(self,fpath,node):
        global roots
        try:
            st = os.stat(fpath)
        except:
            self.harir.delete(node)
            return
    
        self.harir.setValue("FILEINDEXER","Config","lastAccessTime", str(time.time()))
        
        url = self.urlOf(fpath)
        dirname,filename = os.path.split(fpath)
        
        
        logline("\t%s"%filename)

        register = dirname not in roots 

        if register:
            if node is None:
                node = self.harir.createNode()
            #self.harir.setValue(node,GENERAL,"name", filename)
            self.harir.setValue(node,CLASS,"fileName",filename)
            self.harir.setValue(node,CLASS,"lurl",url)

        if os.path.isdir(fpath):
            if(len(os.listdir(fpath))>0):
                self.queue.append({"type":"walktree","event":None,"url":url,"src_path":fpath})
            if register:
                self.harir.setValue(node,CLASS, "indexState", "-1")
        elif os.path.isfile(fpath):
            format = ".".join(filename.split(".")[1:])
            self.harir.setValue(node,CLASS,"format",format)
            lastIndexTime = self.harir.value(node,CLASS,"lastIndexTime")
            if ast.literal_eval('0' if lastIndexTime is None else lastIndexTime) < st[ST_MTIME]:
                try:
                    indexed = False;
                    if format == "docx":
                        content = self.readDocxContent(fpath)
                        self.harir.setValue(node,CLASS, "fileContent", content)
                        indexed = True
                    if format == "doc":
                        doc = DocReader(fpath)
                        content = doc.read()
                        self.harir.setValue(node,CLASS, "fileContent", content)
                        indexed = True
                    if format in ["html","htm","xml"]:
                        content = self.readRawFile(fpath)
                        content = self.unescapeXml(content)
                        content = re.sub('<[^>]*>', '', content)
                        self.harir.setValue(node,CLASS, "fileContent", content)
                        indexed = True
                    if format in ["txt","tex"]:
                        content = self.readRawFile(fpath)
                        self.harir.setValue(node,CLASS, "fileContent", content)
                        indexed = True
                    if format in ["zip","7z","gz","rar"]:
                        pass
                    if format in ["pdf"]:
                        pass
                    if format in ["pptx"]:
                        pass
                    if format in ["xlsx"]:
                        pass
                    if indexed:
                        self.harir.setValue(node,CLASS, "lastIndexTime", str(time.time()))
                        self.harir.setValue(node,CLASS, "indexState", "1")

                except:
                    self.harir.setValue(node,CLASS, "indexState", "-1")
        if register:
            relativedir = dirname.replace("\\","/").replace("//","/")
            currentroot = ""
            for root in roots:
                if relativedir.upper().startswith(root.upper()):
                    relativedir = relativedir[len(root):]
                    currentroot = root
                    break
            
            self.harir.setValue(node,CLASS,"rootPath",currentroot)
            guidex = re.search("^([/]?([0-9a-fA-F]{32,32}/[0-9]+))", relativedir)
            if guidex is not None:
                self.harir.setValue(node,CLASS,"fileId",guidex.group(2))
                self.harir.setValue(node,CLASS,"url",relativedir[len(guidex.group(1)):])
            else:
                guidex = re.search("^([/]?([0-9a-fA-F]{32,32}))", relativedir)
                if guidex is not None:
                    self.harir.setValue(node,CLASS,"fileId",guidex.group(2))
                    self.harir.setValue(node,CLASS,"url",relativedir[len(guidex.group(1)):])
                else:
                    idex = re.search("^([/]?([\{]?[0-9a-fA-F]{8,8}\-[0-9a-fA-F]{4,4}\-[0-9a-fA-F]{4,4}\-[0-9a-fA-F]{4,4}\-[0-9a-fA-F]{12,12}[\}]?))", relativedir)
                    if idex is not None:
                        self.harir.setValue(node,CLASS,"fileId",idex.group(2))
                        self.harir.setValue(node,CLASS,"url",relativedir[len(idex.group(1)):])
                    else:
                        idex = re.search("^([/]?([0-9]+))[/$]", relativedir)
                        if idex is not None:
                            self.harir.setValue(node,CLASS,"fileId",idex.group(2))
                            self.harir.setValue(node,CLASS,"url",relativedir[len(idex.group(1)):])

            self.harir.setValue(node,CLASS,"modified",str(st[ST_MTIME]))
            self.harir.setValue(node,CLASS,"created",str(st[ST_CTIME]))
            self.harir.setValue(node,CLASS,"accessed",str(st[ST_ATIME]))
        self.harir.commit()
        
    def schedule(self):
        global harir
        
        for i in range(5):
            if(len(self.queue)>0):
                self.checkEvent(self.queue.pop())
            else:
                if len(self.toCrawlPaths)>0:
                    self.harir.setValue("FILEINDEXER","Config","InitializedPaths",';'.join(self.toCrawlPaths))
                    self.harir.commit()
                    self.toCrawlPaths = []
                break
    def checkEvent(self,ev):
        url = ev["url"]
        ev_type = ev["type"]
        fpath = ev["src_path"]
        event = ev["event"]
        
        node = self.nodeOf(url)
       
        logline("%s:%s"%(ev_type,node))
        if ev_type=="walktree":
            for f in os.listdir(fpath):
                pathname = os.path.join(fpath,f)
                if os.path.isdir(pathname) and len(os.listdir(pathname))==0:
                    continue
                pathurl = self.urlOf(pathname)
                node = self.nodeOf(pathurl)
                self.updateFileProperties(pathname, node)
        elif ev_type=="deleted":
            if os.path.isdir(fpath):
                    self.harir.deleteConditions("`attr`='%s->lurl' and `value` like '@string:%s%%'"%(CLASS,url))
            if node is not None:
                self.harir.delete(node)
        elif ev_type=="modified":
            self.updateFileProperties(fpath, node)
        elif ev_type=="created":
            self.updateFileProperties(fpath, node)
        elif ev_type=="moved":
            if node is not None:
                self.harir.delete(node)
                
            dst_fpath = os.path.abspath(event.dest_path)
            dst_url = self.urlOf(dst_fpath)
            dstNode = self.nodeOf(dst_url)
            self.updateFileProperties(dst_fpath, node)
        else:
            logline("%s %s"%(event.event_type,node))


class MyEventHandler(FileSystemEventHandler):
    def __init__(self):
        global filesQueue
        FileSystemEventHandler.__init__(self)
        self.queue = filesQueue
        

    def on_any_event(self,event):
        global event_handler,indexer,roots
        fpath = os.path.abspath(event.src_path)
        fpath = repairPath(fpath)
        url = indexer.urlOf(fpath)
        
        if (fpath in roots) or (event.src_path in roots):
            logline("Root") 
        else:
            filesQueue.append({"type":event.event_type,"event":event,"url":url,"src_path":fpath})
        
    
def indexInDb(paths, dbpath, rootIndex=True,lastAccessTime=0):
    global event_handler,observer,filesQueue,indexer
    try:
        event_handler = MyEventHandler()
        
        indexer = Indexer(paths,dbpath,rootIndex, lastAccessTime)
        
        observer = Observer()
        for path in paths: 
            observer.schedule( event_handler, path, recursive=True )
        
        observer.start()
        while True:
            indexer.schedule()
            if(len(filesQueue)==0):
                time.sleep(1)
        
    except:
        logline( "Unexpected error:%s"% sys.exc_info()[0])
        onExit()
        raise
    finally:
        onExit()
        
        
@atexit.register
def onExit():
    global observer,harir
    if event_handler is not None:
        harir.closeDb()
    if observer is not None:
        observer.stop()
def signal_term_handler(signal, frame):
    onExit()
    sys.exit(0)        

if __name__ == "__main__":
    #fileIndexer.py index --db dbpath --indexroot --fromtime --roots
    
    filesQueue = []
    roots = []
    event_handler = None
    observer = None
    harir = None
    indexer = None
    
    curpath = os.path.realpath(__file__)
    currentDrive = curpath[:2] if ( len(curpath)>1 and curpath[1]==':' ) else None
    
    signal.signal(signal.SIGTERM, signal_term_handler)
    
    #sys.argv = ["fileindexer.py","index","--db","test.db","--roots","dist","--indexroots"]
   
    myopts, args = getopt.getopt(sys.argv[2:],"",["db=","indexroots","fromtime=","roots=","log=","names=","contents=","query="])
   
    action = sys.argv[1] if len(sys.argv)>1 else 'help'
    
    if action=="help":
        print "fileIndexer Command    Options"
        print " Commands: help,log,index,search,cleardb"
        print "     help: show this help"
        print "     cleardb: cleardatabase"
        print "                   [--db (database for index to), default=fileindices.db]"
        print "     log: monitor directory for changes and write changes"
        print "        fileIndexer log [directory for looking changes,default=current]"
        print "     index:will monitor multiple directories for changes and write changes to database"
        print "        fileIndexer index [--log (logfile), default=indexer.log]"
        print "                          [--roots (comma separated roots), default=current]"
        print "                          [--db (database for index to), default=fileindices.db]"
        print "                          [--indexroots (will index roots from base to bottom), default=false]"
        print "                          [--fromtime (year/month/day/hour/minute/second/milisec to index changes from that time), default=index from last index time in db]"
        print "      search: will search for something"
        print "          fileIndexer search [--db (database for index to), default=fileindices.db]"
        print "                             [--names (string for search in filenames)]"
        print "                             [--contents (string for search in file contents)]"
        print "                             [--query (query file containing lines of name: or content:)]"
    
    if action=="cleardb":
        dbpath = 'fileindices.db'
        for n,v in myopts:
            if n=="--db":
                dbpath = v
        harir = PyHarir(dbpath)
        harir.clearDb()
        harir.closeDb()
    if action=="log":
        logChanges();
    
    
    if action=="search":
        dbpath = 'fileindices.db'
        query = " 0 "
        for n,v in myopts:
            if n=="--db":
                dbpath = v
            if n=="--names":
                query = query + " and ( attr='FileIndexItem->fileName' and value like '%%%s%%') "%v
            if n=="--contents":
                query = query + " and ( attr='FileIndexItem->fileContent' and value like '%%%s%%') "%v
            if n=="--query":
				try:
					data = open(v, 'rb').read()
					if encoding is None:
						try:
							from charset import detect
						except ImportError:
							detect = lambda x: {'encoding': 'utf-8'}
						encoding = detect(data)['encoding']
					data = data.decode(encoding)
				except:
					logline( "Unexpected error while reading raw file:%s"% sys.exc_info()[0])			
				queryf = data.split("\n")
				for line in queryf:
					line = line.strip()
					if line.startswith("name:"):
						nameq = line[5:] 
						query = query + "or ( attr='FileIndexItem->fileName' and value like '%%%s%%') "%nameq
					if line.startswith("content:"):
						contentq = line[8:]
						query = query + " or ( attr='FileIndexItem->fileContent' and value like '%%%s%%') "%contentq
            harir = PyHarir(dbpath)
            results = harir.findConditions(query)
            for result in results:
                lurl = harir.value(result[0],"FileIndexItem","lurl")
                if lurl is None:
                    continue
                if lurl.startswith(CURDIR):
                    lurl = currentDrive + lurl[2:]
                print (lurl if lurl is not None else '')

    if action=="index":
        roots = ['.']
        dbpath = 'fileindices.db'
        rootIndex = False
        lastAccessTime = 0

        logfile = myopts["--log"] if "--log" in [x[0] for x in myopts] else "indexer.log"
        logger = codecs.open(logfile, "w+", "utf-8")
        print "loging into ",logfile

        logline("\n-----------------------")
        logline("Application Started...")
        logline("ARGS:"%sys.argv)
        logline("\tChecking one by one")
        
        for o,v in myopts:
            logline("\t...%s=%s"%(o,v))
            if o=="--roots":roots = v.split(",") 
            if o=="--db":dbpath = v
            if o=="--indexroots": rootIndex = True
            if o=="--fromtime" :
                vals = [int(vi) for vi in v.split("/")] 
                lastAccessTime = time.mktime(vals)
                
        roots = [repairPath(root) for root in roots]
        logline("roots:%s"%"\n\t\t".join(roots))
        logline("dbpath:%s"%dbpath)
        logline("indexroot:%s"%rootIndex)
        logline("fromTime:%d"%lastAccessTime)
                
        indexInDb(roots,dbpath,rootIndex, lastAccessTime)
