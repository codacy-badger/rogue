#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue base module - Node Classes
#-----------------------------------------------------------------------------
# File       : pyrogue/_Node.py
# Created    : 2017-05-16
#-----------------------------------------------------------------------------
# This file is part of the rogue software platform. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the rogue software platform, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------
import sys
from collections import OrderedDict as odict
import logging
import re
import inspect
import pyrogue as pr
import Pyro4
import functools as ft
import parse
import collections
import string
import itertools

def logInit(cls=None,name=None):
    """Init a logging pbject. Set global options."""
    logging.basicConfig(
        #level=logging.NOTSET,
        format="%(levelname)s:%(name)s:%(message)s",
        stream=sys.stdout)

    msg = 'pyrogue'
    if cls: msg += "." + cls.__class__.__name__
    if name: msg += "." + name
    return logging.getLogger(msg)


class NodeError(Exception):
    """ Exception for node manipulation errors."""
    pass

class Node(object):
    """
    Class which serves as a managed obect within the pyrogue package. 
    Each node has the following public fields:
        name: Global name of object
        description: Description of the object.
        hidden: Flag to indicate if object should be hidden from external interfaces.
        classtype: text string matching name of node sub-class
        path: Full path to the node (ie. node1.node2.node3)

    Each node is associated with a parent and has a link to the top node of a tree.
    A node has a list of sub-nodes as well as each sub-node being attached as an
    attribute. This allows tree browsing using: node1.node2.node3
    """


    def __init__(self, *, name, description="", expand=True, hidden=False):
        """Init the node with passed attributes"""

        # Name cannot contain whitespace
        if any(char in name for char in string.whitespace):
            raise NodeError(f'Node name \"{name}\" cannot contain whitespace')
        
        # Public attributes
        self._name        = name
        self._description = description
        self._hidden      = hidden
        self._path        = name
        self._depWarn     = False
        self._expand      = expand

        # Tracking
        self._parent = None
        self._root   = None
        self._nodes  = odict()
        self._bases  = None

        # Setup logging
        self._log = logInit(self,name)

    @Pyro4.expose
    @property
    def name(self):
        return self._name

    @Pyro4.expose
    @property
    def description(self):
        return self._description

    @Pyro4.expose
    @property
    def hidden(self):
        return self._hidden

    @Pyro4.expose
    @hidden.setter
    def hidden(self, value):
        self._hidden = value

    @Pyro4.expose
    @property
    def path(self):
        return self._path

    @Pyro4.expose
    @property
    def expand(self):
        return self._expand

    def __repr__(self):
        return self.path

    def __getattr__(self, name):
        if name in self._nodes:
            return self._nodes[name]
        else:
            raise AttributeError('{} has no attribute {}'.format(self, name))

    def __dir__(self):
        return(super().__dir__() + list(self._nodes.keys()))


    def add(self,node):
        """Add node as sub-node"""

        # Special case if list (or iterable of nodes) is passed
        if isinstance(node, collections.Iterable) and all(isinstance(n, Node) for n in node):
            for n in node:
                self.add(n)
            return

        # Fail if added to a non device node (may change in future)
        if not isinstance(self,pr.Device):
            raise NodeError(f'Attempting to add node with name {node.name} to non device node {self.name}.')

        # Fail if root already exists
        if self._root is not None:
            raise NodeError(f'Error adding node with name {node.name} to {self.name}. Tree is already started.')

        # Error if added node already has a parent
        if node._parent is not None:
            raise NodeError(f'Error adding node with name {node.name} to {self.name}. Node is already attached.')
        

        # Extract node name and indicies (if any)
        name = [s.replace(']', '') for s in node.name.split('[')]
        name = name[0] + [int(x) for x in name[1:]]

        d = self._nodes

        for i,k in enumerate(name):
            if not (isinstance(d, _NodeDict)):
                # If we hit somethign that is not a dict, its an object we already placed
                raise NodeError(f'Error adding node with name {node.name} to {self.name}. Name collision.')
            
            if isinstance(d, _NodeDict) and k not in d:
                # create a new dict at this level if it doesnt yet exist
                d[k] = _NodeDict()

            # if not last, iterate down
            if i < len(path)-1:
                d = d[k]
            else:
                # If we've put an empty dict here we can overwrite it with the node
                if len(d[k]) == 0:
                    d[k] = node
                else:
                    raise NodeError(f'Error adding node with name {node.name} to {self.name}. Name collision.')

    def addNode(self, nodeClass, **kwargs):
        self.add(nodeClass(**kwargs))

    def addNodes(self, nodeClass, name, offset, dims, strides, **kwargs):
        dims = list(dims) if isinstance(dims, Iterable) else [dims]
        strides = list(strides) if isinstance(dims, Iterable) else [strides]

        if len(dims) == 1:
            # If down to 1 dimension, add the nodes
            for d in range(dims[0]):
                self.add(nodeClass(name=f'{name}[{d}]', offset = offset+(d*strides[0]), **kwargs))
        else:
            # Recurse
            for d in range(dims[0]):
                self.addNodeArray(nodeClass, f'{name}[{d}]', offset+d*strides[0], dims[1:], strides[1:])

        
    @Pyro4.expose
    @property
    def nodeList(self):
        return([k for k,v in self._nodes.items()])

    @Pyro4.expose
    def getNodes(self,typ,exc=None,hidden=True):
        """
        Get a ordered dictionary of nodes.
        pass a class type to receive a certain type of node
        class type may be a string when called over Pyro4
        """
        return odict([(k,n) for k,n in self._nodes.items() \
            if (n._isinstance(typ) and ((exc is None) or (not n._isinstance(exc))) and (hidden or n.hidden == False))])

    @Pyro4.expose
    @property
    def nodes(self):
        """
        Get a ordered dictionary of all nodes.
        """
        return self._nodes

    @Pyro4.expose
    @property
    def variables(self):
        """
        Return an OrderedDict of the variables but not commands (which are a subclass of Variable
        """
        return self.getNodes(typ=pr.BaseVariable,exc=pr.BaseCommand,hidden=True)

    @Pyro4.expose
    @property
    def visableVariables(self):
        """
        Return an OrderedDict of the variables but not commands (which are a subclass of Variable
        """
        return self.getNodes(typ=pr.BaseVariable,exc=pr.BaseCommand,hidden=False)

    @Pyro4.expose
    @property
    def variableList(self):
        """
        Get a recursive list of variables and commands.
        """
        lst = []
        for key,value in self._nodes.items():
            if isinstance(value,pr.BaseVariable):
                lst.append(value)
            else:
                lst.extend(value.variableList)
        return lst

    @Pyro4.expose
    @property
    def deviceList(self):
        """
        Get a recursive list of devices
        """
        lst = []
        for key,value in self._nodes.items():
            if isinstance(value,pr.Device):
                lst.append(value)
            else:
                lst.extend(value.deviceList)
        return lst

    @Pyro4.expose
    @property
    def commands(self):
        """
        Return an OrderedDict of the Commands that are children of this Node
        """
        return self.getNodes(pr.BaseCommand,hidden=True)

    @Pyro4.expose
    @property
    def visableCommands(self):
        """
        Return an OrderedDict of the Commands that are children of this Node
        """
        return self.getNodes(pr.BaseCommand,hidden=False)

    @Pyro4.expose
    @property
    def devices(self):
        """
        Return an OrderedDict of the Devices that are children of this Node
        """
        return self.getNodes(pr.Device,hidden=True)

    @Pyro4.expose
    @property
    def visableDevices(self):
        """
        Return an OrderedDict of the Devices that are children of this Node
        """
        return self.getNodes(pr.Device,hidden=False)

    @Pyro4.expose
    @property
    def parent(self):
        """
        Return parent node or NULL if no parent exists.
        """
        return self._parent

    @Pyro4.expose
    @property
    def root(self):
        """
        Return root node of tree.
        """
        return self._root

    @Pyro4.expose
    def node(self, path):
        return attrHelper(self._nodes,path)

    @Pyro4.expose
    @property
    def isDevice(self):
        return isinstance(self,pr.Device)

    @Pyro4.expose
    @property
    def isVariable(self):
        return (isinstance(self,pr.BaseVariable) and (not isinstance(self,pr.BaseCommand)))

    @Pyro4.expose
    @property
    def isCommand(self):
        return isinstance(self,pr.BaseCommand)

    def find(self, *, recurse=True, typ=None, **kwargs):
        """ 
        Find all child nodes that are a base class of 'typ'
        and whose properties match all of the kwargs.
        For string properties, accepts regexes.
        """
    
        if typ is None:
            typ = pr.Node

        found = []
        for node in self._nodes.values():
            if isinstance(node, typ):
                for prop, value in kwargs.items():
                    if not hasattr(node, prop):
                        break
                    attr = getattr(node, prop)
                    if isinstance(value, str):
                        if not re.match(value, attr):
                            break

                    else:
                        if inspect.ismethod(attr):
                            attr = attr()
                        if not value == attr:
                            break
                else:
                    found.append(node)
            if recurse:
                found.extend(node.find(recurse=recurse, typ=typ, **kwargs))
        return found

    def callRecursive(self, func, nodeTypes=None, **kwargs):
        # Call the function
        getattr(self, func)(**kwargs)

        if nodeTypes is None:
            nodeTypes = [pr.Node]

        # Recursively call the function
        for key, node in self._nodes.items():
            if any(isinstance(node, typ) for typ in nodeTypes):
                node.callRecursive(func, nodeTypes, **kwargs)

    # this might be useful
    def makeRecursive(self, func, nodeTypes=None):
        def closure(**kwargs):
            self.callRecursive(func, nodeTypes, **kwargs)
        return closure

    def _isinstance(self,typ):
        if isinstance(typ,str):
            if self._bases is None:
                self._bases = pr.genBaseList(self.__class__)
            return typ in self._bases
        else: return isinstance(self,typ)

    def _rootAttached(self,parent,root):
        """Called once the root node is attached."""
        self._parent = parent
        self._root   = root
        self._path   = parent.path + '.' + self.name

    def _exportNodes(self,daemon):
        for k,n in self._nodes.items():
            daemon.register(n)
            n._exportNodes(daemon)

    def _getDict(self,modes):
        """
        Get variable values in a dictionary starting from this level.
        Attributes that are Nodes are recursed.
        modes is a list of variable modes to include.
        """
        data = odict()
        for key,value in self._nodes.items():
            nv = value._getDict(modes)
            if nv is not None:
                data[key] = nv

        if len(data) == 0:
            return None
        else:
            return data

    def _getDepWarn(self):
        ret = []

        if self._depWarn:
            ret += [self.path]

        for key,value in self._nodes.items():
            ret += value._getDepWarn()

        return ret

    def _setDict(self,d,writeEach,modes=['RW']):
        for key, value in d.items():
            nlist = nodeMatch(self._nodes,key)

            if nlist is None or len(nlist) == 0:
                self._log.error("Entry {} not found".format(key))
            else:
                for n in nlist:
                    n._setDict(value,writeEach,modes)

    def _setTimeout(self,timeout):
        pass

class PyroNode(object):
    def __init__(self, *, root, node, daemon):
        self._root   = root
        self._node   = node
        self._daemon = daemon

    def __repr__(self):
        return self._node.path

    def __getattr__(self, name):
        ret = self.node(name)
        if ret is None:
            return self._node.__getattr__(name)
        else:
            return ret

    def __dir__(self):
        return(super().__dir__() + self._node.nodeList)

    def _convert(self,d):
        ret = odict()
        for k,n in d.items():

            if isinstance(n,dict):
                ret[k] = PyroNode(root=self._root,node=Pyro4.util.SerializerBase.dict_to_class(n),daemon=self._daemon)
            else:
                ret[k] = PyroNode(root=self._root,node=n,daemon=self._daemon)

        return ret

    def attr(self,attr,**kwargs):
        return self.__getattr__(attr)(**kwargs)

    def addInstance(self,node):
        self._daemon.register(node)

    def node(self, path):
        ret = self._node.node(path)
        if ret is None: 
            return None
        elif isinstance(ret,odict) or isinstance(ret,dict):
            return self._convert(ret)
        else:
            return PyroNode(root=self._root,node=ret,daemon=self._daemon)

    def getNodes(self,typ,exc=None,hidden=True):
        excPass = str(exc) if exc is not None else None
        return self._convert(self._node.getNodes(str(typ),excPass,hidden))

    @property
    def nodes(self):
        return self._convert(self._node.nodes)

    @property
    def variables(self):
        return self._convert(self._node.variables)

    @property
    def visableVariables(self):
        return self._convert(self._node.visableVariables)

    @property
    def commands(self):
        return self._convert(self._node.commands)

    @property
    def visableCommands(self):
        return self._convert(self._node.visableCommands)

    @property
    def devices(self):
        return self._convert(self._node.devices)

    @property
    def visableDevices(self):
        return self._convert(self._node.visableDevices)

    @property
    def parent(self):
        return PyroNode(root=self._root,node=self._node.parent,daemon=self._daemon)

    @property
    def root(self):
        return self._root

    def addListener(self, listener):
        self.root._addRelayListener(self.path, listener)

    def __call__(self,arg=None):
        self._node.call(arg)


class _NodeDict(dict):
    """ A sliceable dict """
    def __getitem__(self, key):
        if isinstance(key, tuple):
            #multi-dimensional slice
            keys = itertools.islice(self.keys(), key[0].start, key[0].stop, key[0].step)
            key = key[1:]
            if len(key) == 1:
                key = key[0]
            return {k: _NodeDict.__getitem__(dict.get(self, k), key) for k in keys}

        if isinstance(key, slice):
            # Single dimensional slice
            keys = itertools.islice(self.keys(), key.start, key.stop, key.step)
            return {k: self[k] for k in keys}

        # base case - normal lookup
        return dict.get(self, key)

def flattenDict(d, func):
    for elem in getattr(d, func)():
        if isinstance(elem, dict):
            for x in flattenDict(elem, func):
                yield x
        else:
            yield elem
    
def nodeMatch(nodes, expr):
    """
    Return a list of nodes which match the given name. The name can either
    be a single value or a list accessor:
        value
        value[9]
        value[0:1]
        value[*]
    """

    # First check to see if unit matches a node name
    # needed when [ and ] are in a variable or device name
    if expr in nodes:
        return [nodes[expr]]

    idx = expr.index('[')
    name, slices = expr[:idx], expr[idx:]

    # First find all nodes that match the name regex
    nameNodes = self.find(recurse=False, typ=Node, name=name)

    slices = slices.replace('*', ':')

    ret = []

    for n in nameNode:
        if isinstance(n, Node):
            ret.append(n)
        elif isinstance(n, list):
            d = eval(f'{n.name}{slice}')
            ret.append(list(flattenDict(d, 'values')))

    return ret
    

