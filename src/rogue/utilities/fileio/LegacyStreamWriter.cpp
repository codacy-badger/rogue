/**
 *-----------------------------------------------------------------------------
 * Title         : Data file writer utility.
 * ----------------------------------------------------------------------------
 * File          : LegacyStreamWriter.h
 * Author        : Ryan Herbst <rherbst@slac.stanford.edu>
 * Created       : 09/28/2016
 * Last update   : 09/28/2016
 *-----------------------------------------------------------------------------
 * Description :
 *    Class to coordinate data file writing.
 *    This class supports multiple stream slaves, each with the ability to
 *    write to a common data file. The data file is a series of banks.
 *    Each bank has a channel and frame flags. The channel is per source and the
 *    lower 24 bits of the frame flags are used as the flags.
 *    The bank is preceeded by 2 - 32-bit headers to indicate bank information
 *    and length:
 *
 *       headerA:
 *          [31:0] = Length of data block in bytes
 *       headerB
 *          31:24  = Channel ID
 *          23:o   = Frame flags
 *
 *-----------------------------------------------------------------------------
 * This file is part of the rogue software platform. It is subject to 
 * the license terms in the LICENSE.txt file found in the top-level directory 
 * of this distribution and at: 
    * https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
 * No part of the rogue software platform, including this file, may be 
 * copied, modified, propagated, or distributed except according to the terms 
 * contained in the LICENSE.txt file.
 *-----------------------------------------------------------------------------
**/
#include <rogue/utilities/fileio/LegacyStreamWriter.h>
#include <rogue/utilities/fileio/StreamWriterChannel.h>
#include <rogue/interfaces/stream/Frame.h>
#include <rogue/GeneralError.h>
#include <stdint.h>
#include <boost/thread.hpp>
#include <boost/make_shared.hpp>
#include <boost/lexical_cast.hpp>
#include <fcntl.h>
#include <rogue/GilRelease.h>

namespace ris = rogue::interfaces::stream;
namespace ruf = rogue::utilities::fileio;
namespace bp  = boost::python;

//! Class creation
ruf::LegacyStreamWriterPtr ruf::LegacyStreamWriter::create () {
   ruf::LegacyStreamWriterPtr s = boost::make_shared<ruf::LegacyStreamWriter>();
   return(s);
}

//! Setup class in python
void ruf::LegacyStreamWriter::setup_python() {
   bp::class_<ruf::LegacyStreamWriter, ruf::LegacyStreamWriterPtr, boost::noncopyable >("LegacyStreamWriter",bp::init<>())
      .def("create",         &ruf::LegacyStreamWriter::create)
      .staticmethod("create")
      .def("open",           &ruf::StreamWriter::open)
      .def("close",          &ruf::StreamWriter::close)
      .def("setBufferSize",  &ruf::StreamWriter::setBufferSize)
      .def("setMaxSize",     &ruf::StreamWriter::setMaxSize)
      .def("getChannel",     &ruf::StreamWriter::getChannel)
      .def("getSize",        &ruf::StreamWriter::getSize)
      .def("getFrameCount",  &ruf::StreamWriter::getFrameCount)
      .def("waitFrameCount", &ruf::StreamWriter::waitFrameCount)
   ;
}

//! Creator
ruf::LegacyStreamWriter::LegacyStreamWriter() : StreamWriter() {
}

//! Deconstructor
ruf::LegacyStreamWriter::~LegacyStreamWriter() { 
   this->close();
}



ruf::StreamWriterChannelPtr ruf::LegacyStreamWriter::getDataChannel() {
  return getChannel(LegacyStreamWriter::RawData);
}

ruf::StreamWriterChannelPtr ruf::LegacyStreamWriter::getYamlChannel() {
  return getChannel(LegacyStreamWriter::YamlData);
}


//! Write data to file. Called from StreamWriterChannel
void ruf::LegacyStreamWriter::writeFile ( uint8_t channel, boost::shared_ptr<rogue::interfaces::stream::Frame> frame) {
   ris::FrameIteratorPtr iter;
   uint32_t value;
   uint32_t size;

   rogue::GilRelease noGil;
   boost::unique_lock<boost::mutex> lock(mtx_);

   if ( fd_ >= 0 ) {
      size = frame->getPayload() + 4;

      // Check file size
      checkSize(size);

      // First write size
      intWrite(&size,4);

      // Create EVIO header
      value  = frame->getFlags() & 0xFFFFFF;
      value |= (channel << 24);
      intWrite(&value,4);

      iter = frame->startRead(0,size-4);
      do {
         intWrite(iter->data(),iter->size());
      } while (frame->nextRead(iter));

      // Update counters
      frameCount_ ++;
      lock.unlock();
      cond_.notify_all();
   }
}



