/**
 *-----------------------------------------------------------------------------
 * Title      : RSSI Client Class
 * ----------------------------------------------------------------------------
 * File       : Client.h
 * Created    : 2017-01-07
 * Last update: 2017-01-07
 * ----------------------------------------------------------------------------
 * Description:
 * UDP Client
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
#ifndef __ROGUE_PROTOCOLS_RSSI_CLIENT_H__
#define __ROGUE_PROTOCOLS_RSSI_CLIENT_H__
#include <boost/thread.hpp>
#include <stdint.h>

namespace rogue {
   namespace protocols {
      namespace rssi {

         class Transport;
         class Application;
         class Controller;

         //! RSSI Client Class
         class Client {

               //! Transport module
               boost::shared_ptr<rogue::protocols::rssi::Transport> tran_;

               //! Application module
               boost::shared_ptr<rogue::protocols::rssi::Application> app_;

               //! Client module
               boost::shared_ptr<rogue::protocols::rssi::Controller> cntl_;

            public:

               //! Class creation
               static boost::shared_ptr<rogue::protocols::rssi::Client> create (uint32_t segSize);

               //! Setup class in python
               static void setup_python();

               //! Creator
               Client(uint32_t segSize);

               //! Destructor
               ~Client();

               //! Get transport interface
               boost::shared_ptr<rogue::protocols::rssi::Transport> transport();

               //! Application module
               boost::shared_ptr<rogue::protocols::rssi::Application> application();

               //! Get state
               bool getOpen();

               //! Get Down Count
               uint32_t getDownCount();

               //! Get Drop Count
               uint32_t getDropCount();

               //! Get Retran Count
               uint32_t getRetranCount();

               //! Get locBusy
               bool getLocBusy();

               //! Get locBusyCnt
               uint32_t getLocBusyCnt();

               //! Get remBusy
               bool getRemBusy();

               //! Get remBusyCnt
               uint32_t getRemBusyCnt();
               
               //! Get maxRetran
               uint32_t getMaxRetran();
               
               //! Get remMaxBuffers
               uint32_t getRemMaxBuffers();           

               //! Get remMaxSegment
               uint32_t getRemMaxSegment();    

               //! Get retranTout
               uint32_t getRetranTout();

               //! Get cumAckTout
               uint32_t getCumAckTout();               
               
               //! Get nullTout
               uint32_t getNullTout();
               
               //! Get maxCumAck
               uint32_t getMaxCumAck();

               //! Get segmentSize
               uint32_t getSegmentSize();               

               //! Set timeout in microseconds for frame transmits
               void setTimeout(uint32_t timeout);

               //! Stop connection
               void stop();

         };

         // Convienence
         typedef boost::shared_ptr<rogue::protocols::rssi::Client> ClientPtr;

      }
   }
};

#endif

