# Copyright (c) 2010 Derek Murray <derek.murray@cl.cam.ac.uk>
# Copyright (c) 2010 Anil Madhavapeddy <anil@recoil.org>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import with_statement
from optparse import OptionParser
import socket
import cherrypy
import sys
import os

def set_port(port):
    cherrypy.config.update({'server.socket_port': port})

def set_config(filename):
    cherrypy.config.update(filename)

def main(default_role=None):

    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    
    if cherrypy.config.get('server.socket_port') is None:
        cherrypy.config.update({'server.socket_port': 8000})
    
    parser = OptionParser()
    parser.add_option("-r", "--role", action="store", dest="role", help="Server role", metavar="ROLE", default=default_role)
    parser.add_option("-p", "--port", action="callback", callback=lambda w, x, y, z: set_port(y), default=cherrypy.config.get('server.socket_port'), type="int", help="Server port", metavar="PORT")
    parser.add_option("-c", "--config", action="callback", callback=lambda w, x, y, z: set_config(y), help="Configuration file", metavar="FILE")
    parser.add_option("-m", "--master", action="store", dest="master", help="Master URI", metavar="URI", default=None)
    parser.add_option("-w", "--workerlist", action="store", dest="workerlist", help="List of workers", metavar = "FILE", default=None)
    parser.add_option("-s", "--staticbase", action="store", dest="staticbase", help="Path to base for static content (for masters)", metavar="PATH", default=None)
    parser.add_option("-j", "--journaldir", action="store", dest="journaldir", help="Path to the job journal directory (for masters)", metavar="PATH", default=None)
    parser.add_option("-b", "--blockstore", action="store", dest="blockstore", help="Path to the block store directory", metavar="PATH", default=None)
    parser.add_option("-H", "--hostname", action="store", dest="hostname", help="Hostname the master and other workers should use to contact this host", default=None)
    parser.add_option("-l", "--lib", action="store", dest="lib", help="Path to standard library of Skywriting scripts (for workers)", metavar="PATH", default=os.path.join(os.path.dirname(__file__), '../../sw/stdlib'))
    parser.add_option("-x", "--ignore-blocks", action="store_true", dest="ignore_blocks", help="Flag to instruct the workers not to send existing blocks", default=False)
    (options, _) = parser.parse_args()
   
    if options.role == 'master':
        from skywriting.runtime.master import master_main
        master_main(options)
    elif options.role == 'worker':
        from skywriting.runtime.worker import worker_main
        if not cherrypy.config.get('server.socket_port'):
            parser.print_help()
            print >> sys.stderr, "Must specify port for worker with --port\n"
            sys.exit(1)
        worker_main(options)
    elif options.role == 'interactive':
        from skywriting.runtime.interactive import interactive_main
        interactive_main(options)
    else:
        raise
    
if __name__ == '__main__':
    main()
