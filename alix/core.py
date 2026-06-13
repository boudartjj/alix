#!/usr/bin/env python3
"""
Alix Core Module - A microservices framework using Redis for message brokerage
Provides functionality to register, configure, start/stop microservices and handle messaging
"""

import sys
import traceback
import threading
import redis
import time
import json
import importlib

# ============================================================================
# INTERNAL HELPER FUNCTIONS - Redis Configuration Management
# ============================================================================

def _save(name, channel, module, modulePath, description):
    """Helper: Save microservice configuration to Redis"""
    _saveJSON({'name': name, 'module': module, 'modulePath': modulePath, 'channel': channel, 'description': description})

def _saveJSON(svc):
    """Helper: Serialize and store microservice config as JSON in Redis"""
    name = svc['name']
    r = redis.StrictRedis()
    r.set('alix:config:' + name, json.dumps(svc))

def _load(name):
    """Helper: Retrieve and deserialize microservice config from Redis"""
    r = redis.StrictRedis()
    return json.loads(r.get('alix:config:' + name).decode('utf-8'))

def _delete(name):
    """Helper: Remove microservice configuration from Redis"""
    r = redis.StrictRedis()
    r.delete('alix:config:' + name)

# ============================================================================
# CONFIGURATION FILE MANAGEMENT
# ============================================================================

def exportConfig(name, path):
    """
    Export microservice configuration from Redis to a JSON file

    args:
        name: name of the microservice
        path: file path where config will be saved

    example:
        alix.exportConfig('myMicroservice', '/home/alix/myMicroservice.config')
    """
    with open(path, 'w') as f:
        json.dump(_load(name), f)

def importConfig(path):
    """
    Import microservice configuration from a JSON file to Redis

    args:
        path: config file path to import

    example: 
        alix.importConfig('/home/alix/myMicroservice.config')
    """
    with open(path, 'r') as f:
        _saveJSON(json.load(f))

# ============================================================================
# MICROSERVICE REGISTRATION AND LIFECYCLE
# ============================================================================

def register(name, channel, module, modulePath, description=''):
	"""
	Register a new microservice with its configuration
	
	args:
		name: name of the microservice
		channel: Redis channel the microservice listens on (* for wildcard)
		module: Python module name for the microservice
		modulePath: File system path to the module
		description: Human-readable description of the microservice

	example:
		alix.register('myMicroservice', 'myMicroservice:myMessage', 'my_ms', '/home/alix', 'this is a short description')
	"""
	_save(name, channel, module, modulePath, description)

# ============================================================================
# MICROSERVICE PROPERTY GETTERS AND SETTERS
# ============================================================================

def getModule(name):
    """Get the Python module name for a microservice"""
    return _load(name).get('module')

def setModule(name, moduleName):
    """Update the Python module name for a microservice"""
    svc = _load(name)
    svc['module'] = moduleName
    _saveJSON(svc)

def getModulePath(name):
    """Get the file system path to the microservice module"""
    return _load(name).get('modulePath')

def setModulePath(name, modulePath):
    """Update the file system path to the microservice module"""
    svc = _load(name)
    svc['modulePath'] = modulePath
    _saveJSON(svc)

def getChannel(name):
    """Get the input channel name the microservice listens on"""
    return _load(name).get('channel')

def setChannel(name, channel):
    """Update the input channel name for the microservice"""
    svc = _load(name)
    svc['channel'] = channel
    _saveJSON(svc)

def getOutputChannel(name):
    """Get the output channel where processed messages are sent"""
    return _load(name).get('outputChannel')

def setOutputChannel(name, channel):
    """Update the output channel for processed messages"""
    svc = _load(name)
    if(len(channel.strip()) > 0):
        svc['outputChannel'] = channel
    else:
        svc['outputChannel'] = None
    _saveJSON(svc)

def getDescription(name):
    """Get the description of a microservice"""
    return _load(name).get('description')

def setDescription(name, description):
    """Update the description of a microservice"""
    svc = _load(name)
    svc['description'] = description
    _saveJSON(svc)

# ============================================================================
# MICROSERVICE PARAMETER MANAGEMENT
# ============================================================================

def getParams(name):
    """Get all custom parameters for a microservice (returns dictionary)"""
    svc = _load(name)
    if not 'params' in svc.keys():
        svc['params'] = {}
        _saveJSON(svc)
    return _load(name).get('params')	

def getParam(name, param):
    """Get a single parameter value for a microservice"""
    paramValue = None
    params = getParams(name)
    if param in params: paramValue = params.get(param)
    return paramValue

def setParam(name, param, value):
    """Set a custom parameter for a microservice"""
    svc = _load(name)
    if not 'params' in svc.keys():
        svc['params'] = {}
    svc['params'][param] = value
    _saveJSON(svc)

def delParam(name, param):
    """Delete a custom parameter from a microservice"""
    svc = _load(name)
    if 'params' in svc and param in svc['params']: del svc['params'][param]
    _saveJSON(svc)

def listParams(name):
    """List all parameter names for a microservice"""
    params = getParams(name)
    return [*params.keys()]

# ============================================================================
# MICROSERVICE CLONING AND MANAGEMENT
# ============================================================================

def clone(sourceName, destinationName):
    """Create a copy of a microservice with all its configuration and parameters"""
    register(destinationName, getChannel(sourceName), getModule(sourceName), getModulePath(sourceName), getDescription(sourceName))
    params = getParams(sourceName)
    svc = _load(destinationName)
    svc['params'] = params
    _saveJSON(svc)

def rename(sourceName, destinationName):
    """Rename a microservice (creates new with old name, then deletes original)"""
    clone(sourceName, destinationName)
    unregister(sourceName)

def unregister(name):
    """Stop and completely remove a microservice from the system"""
    stop(name)
    _delete(name)

# ============================================================================
# MICROSERVICE EXECUTION CONTROL
# ============================================================================

def start(name):
    """Start a microservice by dynamically loading and instantiating its module"""
    module_name = getModule(name)
    module_path = getModulePath(name)

    print(f'Starting service {name} with module {module_name} at path {module_path}')

    # Build full path to the Python module file
    file_path = f"{module_path}/{module_name}.py"

    # Load the module dynamically using modern Python importlib
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ModuleNotFoundError(f"Module {module_name} not found at {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # Instantiate the MicroService class and start it
    svc = module.MicroService({'name' : name})
    svc.start()

    print(f'Service {name} started with module {module_name} at path {module_path}')
    return svc

def stop(name):
    """Send a stop command to a running microservice via Redis"""
    r = redis.StrictRedis()
    r.publish('alix:cmd:' + name, 'stopService')

def stopAll():
    """Stop all registered microservices"""
    services = list()
    for svc in services:
        stop(svc['name'])

def startAll():
    """Start all registered microservices"""
    services = list()
    for svc in services:
        start(svc['name'])
    print(f'Started {len(services)} services')

def status(name):
    """Query and return the current status of a microservice"""
    r = redis.StrictRedis()
    r.set('alix:status:' + name, 'stopped')
    r.publish('alix:cmd:' + name, 'status')
    time.sleep(0.1)
    status = r.get('alix:status:' + name).decode('utf-8')
    return status

def list():
    """Retrieve and return a list of all registered microservices with their configurations"""
    services = []
    r = redis.StrictRedis()
    servicesKeys = r.keys('alix:config:*')
    for key in servicesKeys:
        config  = json.loads(r.get(key).decode('utf-8'))
        services.append(config)
    return services

def sendMessage(channel, message):
    """Publish a message to a Redis channel for message broking"""
    r = redis.StrictRedis()
    r.publish(channel, message)

def _getErrorMesssage():
    """Helper: Format the current exception into a readable error message"""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return repr(traceback.format_exception(exc_type, exc_value, exc_traceback))

# ============================================================================
# ALIX MICROSERVICE BASE CLASS - Main threading framework for microservices
# ============================================================================

class Alix(threading.Thread):
    """
    Base class for Alix microservices. Extends threading.Thread to handle:
    - Message reception and processing
    - Redis pubsub communication
    - Service lifecycle management (start/stop)
    - Parameter configuration
    """
    
    def __init__(self, kwargs={}):
        """Initialize a microservice with its name and configuration"""
        threading.Thread.__init__(self)
        self._active = False
        self.name = kwargs['name']
        self.channel = getChannel(self.name)
        print(f'{self.name} initialized')

    def isActive(self):
        """Check if the microservice is currently running"""
        return self._active

    def run(self):
        """Main execution method - starts message listener and processor threads"""
        print(f'{self.name} starting')
        self._active = True
        self._sendMessage('starting')

        # Create and start the message processing thread
        tProcess = threading.Thread(target = self._run)
        tProcess.start()
        
        # Create and start the command listening thread
        tListner = threading.Thread(target = self._listen)
        tListner.start()

        # Create and start the main loop thread
        mainloopThread = threading.Thread(target = self.mainLoop)
        mainloopThread.start()

        self._sendMessage('started')

    def stop(self):
        """Stop the microservice gracefully"""
        print(f'{self.name} stopping')
        self._sendMessage('stopping')
        self._active = False

    def getParam(self, param):
        """Get a custom parameter value for this microservice instance"""
        return getParam(self.name, param)

    def setParam(self, param, value):
        """Set a custom parameter value for this microservice instance"""
        setParam(self.name, param, value)

    def _listen(self):
        """Listen thread: Monitor command channel for stop/status commands"""
        self._sendMessage( 'listen on')
        r = redis.StrictRedis()
        p = r.pubsub()
        p.subscribe('alix:cmd:' + self.name)

        print(f'{self.name} listening on channel alix:cmd:{self.name}')

        # Continuously check for incoming commands while active
        while self.isActive():
            event = p.get_message(timeout=1)
            if event and event['type'] == 'message':
                cmd = event['data']
                if cmd == 'stop':
                    self.stop()
                elif cmd == 'status':
                    r.set('alix:status:' + self.name, 'running')
                    self._sendMessage('active')
        p.close()
        self._sendMessage('listen off')

    def _ping(self):
        """Ping responder: Monitor global ping channel and respond with status"""
        self._sendMessage('ping on')
        r = redis.StrictRedis()
        p = r.pubsub()
        p.subscribe('alix:ping')

        while self.isActive():
            event = p.get_message()
            if event and event['type'] == 'message':
                self._sendMessage('running')
        p.close()
        self._sendMessage('ping off')

    def _sendMessage(self, message):
        """Send a message to this microservice's status channel"""
        sendMessage('alix:msg:' + self.name, message)

    def sendMessage(self, channel, message):
        """Send a message to a Redis channel and log the action"""
        sendMessage(channel, message)
        # Log the message transmission with timestamp and metadata
        self._sendMessage(json.dumps({'timestamp': time.strftime('%Y%m%d%H%M%S', time.gmtime()), 'Type': 'message sent', 'name': self.name , 'message': message}))

    def _run(self):
        """
        Main processing thread: Listen on subscribed channel and process incoming messages
        - Receives messages from input channel
        - Calls onMessage() for custom message handling
        - Sends processed output to output channel if configured
        - Handles errors and logs them
        """
        self._sendMessage('running')
        r = redis.StrictRedis()
        p = r.pubsub()
        # Subscribe to the channel with pattern matching (psubscribe)
        p.psubscribe(self.channel)
        
        while self.isActive():
            event = p.get_message(timeout=1)
            if event: 
                # Log all received events with timestamp
                self._sendMessage(json.dumps({'timestamp': time.strftime('%Y%m%d%H%M%S', time.gmtime()), 'Type': 'message received', 'name': self.name , 'message': str(event)}))
            
            # Process pattern-matched messages
            if event and event['type'] == 'pmessage':
                try: 
                    # Decode and process the message
                    message = event['data'].decode('utf-8')
                    output = self.onMessage(message)
                    
                    # Send output if message was processed and output channel is configured
                    if output is not None and getOutputChannel(self.name) is not None:
                        sendMessage(getOutputChannel(self.name), output)
                except Exception as e:
                    # Log any processing errors to the error channel
                    strNow = time.strftime('%Y%m%d%H%M%S', time.gmtime()) 
                    sendMessage('alix:err:' + self.name, json.dumps({'timestamp':strNow, 'serviceName':self.name, 'message': message, 'errorMessage': _getErrorMesssage()}))

        p.close()
        self._sendMessage('not running')

    def mainLoop(self):
        """
        Override this method in subclasses to implement custom main loop logic (if needed) instead of onMessage)
        This method can be used for microservices that require continuous processing rather than message-driven behavior    
        """

        pass

    def onMessage(self, message):
        """
        Override this method in subclasses to implement custom message handling logic
        
        args:
            message: The incoming message as a string
            
        returns:
            Output to send to the output channel (or None to skip output)
        """
        return None
