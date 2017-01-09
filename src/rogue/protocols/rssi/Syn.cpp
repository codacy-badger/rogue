/**
 *-----------------------------------------------------------------------------
 * Title      : RSII Syn Class
 * ----------------------------------------------------------------------------
 * File       : Syn.h
 * Created    : 2017-01-07
 * Last update: 2017-01-07
 * ----------------------------------------------------------------------------
 * Description:
 * RSSI Syn
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
#include <rogue/protocols/rssi/Syn.h>
#include <boost/make_shared.hpp>
#include <rogue/common.h>
#include <stdint.h>

namespace rpr = rogue::protocols::rssi;
namespace bp  = boost::python;

//! Class creation
rpr::SynPtr rpr::Syn::create (uint8_t * data, uint32_t size) {
   rpr::SynPtr r = boost::make_shared<rpr::Syn>(data,size);
   return(r);
}

// Setup python
void rpr::Syn::setup_python () { }

//! Return required size
uint32_t rpr::Syn::size() {
   return(24);
}

//! Creator
rpr::Syn::Syn ( uint8_t * data, uint32_t size) : rpr::Header(data,size) { }

//! Destructor
rpr::Syn::~Syn() { }

//! Init header contents
void rpr::Syn::init() {
   memset(data_,0,8);
   data_[0] = 24;
   data_[5] = 0x18;
}

//! Get chk flag
bool rpr::Syn::getChk() {
   return(data_[5] & 0x04);
}

//! Set chk flag
void rpr::Syn::setChk(bool state) {
   data_[5] &= 0x0B;
   if ( state ) data_[5] |= 0x04;
}

//! Get MAX Outstanding Segments
uint8_t rpr::Syn::getMaxOutstandingSegments() {
   return(data_[4]);

}

//! Set MAX Outstanding Segments
void rpr::Syn::setMaxOutstandingSegments(uint8_t max) {
   data_[4] = max;
}

//! Get MAX Segment Size
uint16_t rpr::Syn::getMaxSegmentsSize() {
   uint16_t * val = (uint16_t *)&(data_[6]);
   return(le16toh(*val));
}

//! Set MAX Segment Size
void rpr::Syn::setMaxSegmentSize(uint16_t size) {
   uint16_t * val = (uint16_t *)&(data_[6]);
   *val = htole16(size);
}

//! Get Retransmission Timeout
uint16_t rpr::Syn::getRetransmissionTimeout() {
   uint16_t * val = (uint16_t *)&(data_[8]);
   return(le16toh(*val));
}

//! Set Retransmission Timeout
void rpr::Syn::setRetransmissionTimeout(uint16_t to) {
   uint16_t * val = (uint16_t *)&(data_[8]);
   *val = htole16(to);
}

//! Get Cumulative Acknowledgement Timeout
uint16_t rpr::Syn::getCumulativeAckTimeout() {
   uint16_t * val = (uint16_t *)&(data_[10]);
   return(le16toh(*val));
}

//! Set Cumulative Acknowledgement Timeout
void rpr::Syn::setCumulativeAckTimeout(uint16_t to) {
   uint16_t * val = (uint16_t *)&(data_[10]);
   *val = htole16(to);
}

//! Get NULL Timeout
uint16_t rpr::Syn::getNullTimeout() {
   uint16_t * val = (uint16_t *)&(data_[12]);
   return(le16toh(*val));
}

//! Set NULL Timeout
void rpr::Syn::setNullTimeout(uint16_t to) {
   uint16_t * val = (uint16_t *)&(data_[12]);
   *val = htole16(to);
}

//! Get Max Retransmissions
uint8_t rpr::Syn::getMaxRetransmissions() {
   return(data_[15]);
}

//! Set Max Retransmissions
void rpr::Syn::setMaxRetransmissions(uint8_t max) {
   data_[15] = max;
}

//! Get MAX Cumulative Ack
uint8_t rpr::Syn::getMaxCumulativeAck() {
   return(data_[14]);
}

//! Set Max Cumulative Ack
void rpr::Syn::setMaxCumulativeAck(uint8_t max) {
   data_[14] = max;
}

//! Get Timeout Unit
uint8_t rpr::Syn::getTimeoutUnit() {
   return(data_[16]);
}

//! Set Timeout Unit
void rpr::Syn::setTimeoutUnit(uint8_t unit) {
   data_[16] = unit;
}

//! Get Connection ID
uint32_t rpr::Syn::getConnectionId() {
   uint32_t * val = (uint32_t *)&(data_[18]);
   return(le32toh(*val));
}

//! Set Timeout Unit
void rpr::Syn::setConnectionId(uint32_t id) {
   uint32_t * val = (uint32_t *)&(data_[18]);
   *val = htole32(id);
}

