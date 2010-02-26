'''
Created on 8 Feb 2010

@author: dgm36
'''
from cherrypy._cperror import HTTPError
from mrry.mercator.master.workflow import build_workflow
import simplejson
import cherrypy

class MasterRoot:
    
    def __init__(self):
        self.ping = PingReceiver()
        self.workflow = WorkflowsRoot(None)

class PingReceiver:
    
    @cherrypy.expose
    def index(self):
        update = simplejson.loads(cherrypy.request.body.read())
        cherrypy.engine.publish('ping', update)

class WorkflowsRoot:
    
    def __init__(self, scheduler):
        pass
    
    @cherrypy.expose
    def index(self):
        if cherrypy.request.method == 'POST':
            workflow_description = simplejson.loads(cherrypy.request.body.read())
            workflow = build_workflow(workflow_description)
            cherrypy.engine.publish('create_workflow', workflow)
            return simplejson.dumps(workflow.id)
        raise HTTPError(405)
    
    @cherrypy.expose
    def default(self, workflow_id, job_id):
        if cherrypy.request.method == 'POST':
            job_result = simplejson.loads(cherrypy.request.body.read())
            cherrypy.engine.publish('job_completed', workflow_id, job_id, job_result)
            return
        raise HTTPError(405)