/**
 *-----------------------------------------------------------------------------
 * Title      : Rogue EPICS V4 Interface:
 * ----------------------------------------------------------------------------
 * File       : module.cpp
 * Created    : 2018-02-26
 * ----------------------------------------------------------------------------
 * Description:
 * Python module setup
 * ----------------------------------------------------------------------------
 * This file is part of the rogue software platform. It is subject to 
 * the license terms in the LICENSE.txt file found in the top-level directory 
 * of this distribution and at: 
 *    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
 * No part of the rogue software platform, including this file, may be 
 * copied, modified, propagated, or distributed except according to the terms 
 * contained in the LICENSE.txt file.
 * ----------------------------------------------------------------------------
**/

#include <boost/python.hpp>
#include <rogue/protocols/epicsV4/module.h>
namespace rpe = rogue::protocols::epicsV4;

#ifdef DO_EPICSV4

//#include <rogue/protocols/epicsV4/Value.h>
//#include <rogue/protocols/epicsV4/Variable.h>
//#include <rogue/protocols/epicsV4/Command.h>
//#include <rogue/protocols/epicsV4/Server.h>
//#include <rogue/protocols/epicsV4/Pv.h>
//#include <rogue/protocols/epicsV4/Master.h>
//#include <rogue/protocols/epicsV4/Slave.h>

namespace bp  = boost::python;

void rpe::setup_module() {

   // map the IO namespace to a sub-module
   bp::object module(bp::handle<>(bp::borrowed(PyImport_AddModule("rogue.protocols.epicsV4"))));

   // make "from mypackage import class1" work
   bp::scope().attr("epicsV4") = module;

   // set the current scope to the new sub-module
   bp::scope io_scope = module;

   //rpe::Value::setup_python();
   //rpe::Variable::setup_python();
   //rpe::Command::setup_python();
   //rpe::Server::setup_python();
   //rpe::Pv::setup_python();
   //rpe::Master::setup_python();
   //rpe::Slave::setup_python();
}

#else

void rpe::setup_module() {}

#endif
