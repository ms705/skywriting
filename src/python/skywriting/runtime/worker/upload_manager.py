# Copyright (c) 2010 Derek Murray <derek.murray@cl.cam.ac.uk>
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
import tempfile
import shutil
from skywriting.runtime.master import deferred_work
import cherrypy
import logging
import os

class UploadSession:
    
    def __init__(self, id):
        self.id = id
        self.current_pos = 0
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as output_file:
            self.output_filename = output_file.name
        
    def save_chunk(self, start_index, body_file):
        assert self.current_pos == start_index
        with open(self.output_filename, 'ab') as output_file:
            shutil.copyfileobj(body_file, output_file)
            self.current_pos = output_file.tell()
    
    def commit(self, block_store, size):
        assert os.path.getsize(self.output_filename) == size
        block_store.store_file(self.output_filename, self.id, can_move=True)
    
    
    
class UploadManager:
    
    def __init__(self, block_store, deferred_work):
        self.block_store = block_store
        self.current_uploads = {}
        self.current_fetches = {}
        self.deferred_work = deferred_work
        
    def start_upload(self, id):
        self.current_uploads[id] = UploadSession(id)
        
    def handle_chunk(self, id, start_index, body_file):
        session = self.current_uploads[id]
        session.save_chunk(start_index, body_file)
        
    def commit_upload(self, id, size):
        session = self.current_uploads[id]
        session.commit(self.block_store, size)
        del self.current_uploads[id]
        
    def get_status_for_fetch(self, session_id):
        return self.current_fetches[session_id]
        
    def fetch_refs(self, session_id, refs):
        self.current_fetches[session_id] = 408
        self.deferred_work.do_deferred(lambda: self.fetch_refs_deferred(session_id, refs))
        
    def fetch_refs_deferred(self, session_id, refs):
        cherrypy.log.error('Fetching session %s' % session_id, 'UPLOAD', logging.INFO)
        try:
            self.block_store.retrieve_filenames_for_refs_eager(refs)
            self.current_fetches[session_id] = 200
            for ref in refs:
                self.block_store.pin_ref_id(ref.id)
        except:
            self.current_fetches[session_id] = 500
        cherrypy.log.error('Finished session %s, status = %d' % (session_id, self.current_fetches[session_id]), 'UPLOAD', logging.INFO)
