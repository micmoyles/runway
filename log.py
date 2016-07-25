#!/usr/bin/python

"""
Logging utilities.
"""

__revision__ = "$Rev: 9064 $"

import sys, os, socket, traceback
from sys import stderr
from time import time, localtime, strftime
from math import floor

# priorities (these are ordered)

LOG_EMERG     = 0       #  system is unusable
LOG_ALERT     = 1       #  action must be taken immediately
LOG_CRIT      = 2       #  critical conditions
LOG_ERR       = 3       #  error conditions
LOG_WARNING   = 4       #  warning conditions
LOG_NOTICE    = 5       #  normal but significant condition
LOG_INFO      = 6       #  informational
LOG_DEBUG     = 7       #  debug-level messages

# facilities
facility = LOG_LOCAL4 = 20      #  reserved for local use

_levelnames = {
    LOG_EMERG : 'EMERGENCY',
    LOG_CRIT : 'CRITICAL',
    LOG_ERR : 'ERROR',
    LOG_WARNING : 'WARNING',
    LOG_INFO : 'INFO',
    LOG_DEBUG : 'DEBUG',
    'EMERGENCY' : LOG_EMERG,
    'CRITICAL' : LOG_CRIT,
    'ERROR' : LOG_ERR,
    'WARN' : LOG_WARNING,
    'WARNING' : LOG_WARNING,
    'INFO' : LOG_INFO,
    'DEBUG' : LOG_DEBUG,
}

class Logger(object):
    def __init__(self, handlers):
        self.time = 0.0
        self.seconds = 0.0
        self.handlers = handlers

    @property
    def timestamp(self):
        t = time()
        if t is not self.time:
            # within a second? (we dont use int(round()) here as will kill psyco)
            if self.time <= t <= self.seconds:
                # time didnt go backwards and we are still within a second since last seconds
                s = self._timestampsecs
            else:               
                # slow case
                ct = localtime(t)
                s = self._timestampsecs = strftime("%Y-%m-%d %H:%M:%S", ct)
                self.seconds = floor(t) + 1.0

            s += ".%03d" % ((t * 1000) % 1000)
            self._timestamp = s
            self.time = t
        else:
            s = self._timestamp
        return s
    
    def format(self, level, args):
        return "%-8s %s" % (_levelnames.get(level, "NOTSET"), " ".join([str(a) for a in args]))

    # inlined for performance
    def debug(self, *args):
        level = LOG_DEBUG
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)

    def info(self, *args):
        level = LOG_INFO
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)

    def warning(self, *args):
        level = LOG_WARNING
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)

    def error(self, *args):
        level = LOG_ERR
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)

    def exception(self, *args):
        level = LOG_ERR
        args = args + (traceback.format_exc(),)
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)


    def critical(self, *args):
        level = LOG_CRIT
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)
    
    def emergency(self, *args):
        level = LOG_EMERG
        msg = self.format(level, args)
        for handle in self.handlers:
            if level <= handle.level:
                handle.report(self, level, msg)

    def cleanup(self):
        for handle in self.handlers:
            handle.cleanup()
        self.handlers = None

class FileHandler(object):
    def __init__(self, level, filename):
        self.level = level
        self.file = open(filename, "a", 1024 * 8)

    def report(self, logger, level, msg):
        f = self.file
        f.write(logger.timestamp + " " + msg + "\n")
        f.flush()

    def cleanup(self):
        self.file.close()
        
class ConsoleHandler(object):
    _colormap = {
            LOG_DEBUG:   '\033[1;36m',
            LOG_INFO:    '\033[1;32m',
            LOG_WARNING: '\033[1;33m',
            LOG_ERR:     '\033[1;31m',
            LOG_CRIT:    '\033[1;35m',
            LOG_EMERG:   '\033[1;35m'
        }

    _coloroff = '\033[0m'

    def __init__(self, level):
        self.level = level

    def report(self, logger, level, msg):
        msg = self._colormap[level] + logger.timestamp + " " + sys.argv[0] + " " + msg + self._coloroff        
        print >>stderr, msg

    def cleanup(self):
        pass

if sys.platform != "win32":
    from syslog import syslog, openlog as syslog_open, closelog as syslog_close

    class SyslogHandler1(object):
        " /dev/log "
        def __init__(self, level, address="/dev/log", facility=LOG_LOCAL4, 
                     reliable=True, prefix=sys.argv[0]):
            self.level = level
            self.prefix = prefix
            self.retries = 0
            self.address = address
            self.reliable = reliable
            self.facility = facility

            self.connect()

        def report(self, logger, level, msg):
            msg = '<%d>%s-%s\000' % ((self.facility << 3) | level, self.prefix, msg)
            try:
                self.socket.send(msg)
            except:
                if self.retries < 100:
                    # XXX would be nice to retry again after some time interval
                    # - but lets keep ourselves independent from twisted
                    # scheduling for now (ie wait for subzero)
                    self.recover()
                
        def cleanup(self):
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except:
                pass

        def connect(self):
            try:
                self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                self.socket.connect(self.address)

            except socket.error, data:
                if data[0] == 91:
                    self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self.socket.connect(self.address)
                else:
                    raise data

            if not self.reliable:
                self.socket.setblocking(0)

        def recover(self):
            self.cleanup()

            try:
                self.connect()
                self.retries = 0
            except:
                # XXX arghh - error recovery on error recovery?
                self.retries += 1

    class SyslogHandler2(object):
        " UDP socket"
        def __init__(self, level, address=('localhost', 514), 
                     facility=LOG_LOCAL4, prefix="PYTHON"):
            self.level = level
            self.prefix = prefix
            self.address = address
            self.facility = facility
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        def report(self, logger, level, msg):
            msg = '<%d>%s-%s\000' % ((self.facility << 3) | level, self.prefix, msg)
            try:
                self.socket.sendto(msg, self.address)
            except:
                pass

        def cleanup(self):
            self.socket.shutdown(2)
            self.socket.close()

    class SyslogHandler3(object):
        " using library"
        def __init__(self, level, prefix="PYTHON"):
            self.level = level
            self.prefix = prefix
            syslog_open(prefix, LOG_LOCAL4)

        def report(self, logger, level, msg):
            syslog(level, '%s-%s' % (self.prefix, msg))

        def cleanup(self):
            syslog_close()

else:
    SyslogHandler3 = SyslogHandler2 = SyslogHandler1 = None

class TwistedLogObserver(object):
    def __init__(self, info, error):
        self.info = info
        self.error = error

    def report(self, eventDict):
        #print 'eventDict=', eventDict
        edm = eventDict['message']
        if not edm:
            if eventDict['isError'] and eventDict.has_key('failure'):
                text = eventDict['failure'].getTraceback()
            elif eventDict.has_key('format'):
                text = eventDict['format'] % eventDict
            else:
                # we don't know how to log this
                return
        else:
            text = ' '.join(map(str, edm))

        lines = text.split('\n')
        while lines[-1:] == ['']:
            lines.pop()

        if eventDict['isError']:
            log = self.error
        else:
            log = self.info

        firstLine = 1
        for line in lines:
            if firstLine:
                firstLine=0
            else:
                line = '\t%s' % line
            log('[%s] %s' % (eventDict['system'], line))

logging = None
twistedobserver = None

def setup(prefix=sys.argv[0], 
          level=LOG_INFO,
          consolelog=False,
          SyslogHandler=SyslogHandler1,
          facility=LOG_LOCAL4): 
    " set up logging, safe to call multiple times "

    global logging
    if logging is not None:
        # will be collected
        logging.cleanup()
        logging = None

    # create some handlers to use
    handlers = []

    # override level with environment variable
    if os.environ.get('DEBUG'):
        level = LOG_DEBUG

    # log to file

    # if CONSOLELOG set, use console log, else use syslogger
    if consolelog or os.environ.get('CONSOLELOG'):
        handlers.append(ConsoleHandler(level))    
        # We never run production strategies on Windows nor on MacOSX,
        # therefore, we need not spit out a warning on these platforms when we
        # find that the system logger does not exist.  The console logging and
        # warning below is only important for strategies running on production
        # servers.
    if sys.platform.startswith('linux'):
        try:
            handler = SyslogHandler(level, prefix=prefix)
            handler.facility = facility
            handlers.append(handler)
        except Exception, e:
            print >> sys.stderr, 'WARNING: Unable to enable syslog handler', str(e)

    logger = Logger(handlers)

    # set up globals
    global debug, info, warning, error, exception, critical, emergency
    logging   = logger
    debug     = logging.debug
    info      = logging.info
    warning   = logging.warning
    error     = logging.error
    exception = logging.exception
    critical  = logging.critical
    emergency = logging.emergency



# hack alert: below is so we can work without explicit call to setup

def _logWithoutSetup(name):
    def log(*args):
        assert logging is None
        setup()
        globals()[name](*args)
    return log

debug     = _logWithoutSetup("debug")
alert     = _logWithoutSetup("alert")
info      = _logWithoutSetup("info")
warning   = _logWithoutSetup("warning")
error     = _logWithoutSetup("error")
exception = _logWithoutSetup("exception")
critical  = _logWithoutSetup("critical")
emergency = _logWithoutSetup("emergency")

