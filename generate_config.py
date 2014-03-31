#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, urllib2, codecs
from BeautifulSoup import BeautifulSoup # sudo apt-get install python-beautifulsoup
from optparse import OptionParser

def write_config(xmltv, mode, timespan, config):
	url = "" # enter URL of webpage from where you're parsing channel names and URLs for EPG
	soup = BeautifulSoup(urllib2.urlopen(url).read());
	data = str(soup.find(id='')) # enter div id where channel names are stored
	wgfile = codecs.open(config, 'w+', 'UTF-8')
	config = '<!--?xml version="1.0"?-->'
	config += '\n<settings>'
	config += '\n\t<filename>'+xmltv+'</filename>'
	config += '\n\t<mode>'+mode+'</mode>'
	config += '\n\t<postprocess grab="y" run="n">mdb</postprocess>'
	config += '\n\t<logging>off</logging>'
	config += '\n\t<retry time-out="5">4</retry>'
	config += '\n\t<timespan>'+str(timespan)+'</timespan>'
	config += '\n\t<update>f</update>\n'
	for match in re.findall('', data): # enter regex for parsing channel names and URLs for EPG
		config += '\t<channel update="i" site="" site_id="'+match[0]+'" xmltv_id="'+match[1]+'">'+match[2].replace('&', '&amp;amp;')+'</channel>\n'
		# enter site name where you're parsing data
		# match[0] is site_id which is pointing to website you're parsing
		# match[1] is xmltv_id which is the identification string in your playlist
		# match[3] is channel name
	config += '\n</settings>'
	wgfile.write(config.decode('UTF-8'))
	wgfile.close()

def main():
	par = OptionParser(usage="%prog [options]", description="Generate EPG channel list from URL and config file for WebGrab++")
	par.add_option('-f', '--file', action='store', dest='file', default='guide.xml', help=u'xml output file with full path [default: %default]')
	par.add_option('-m', '--mode', action='store', dest='mode', default='n,v,m', help=u'mode for guide [default: %default]')
	par.add_option('-t', '--timespan', type='int', default=0, help=u'timespan for epg in days [default: %default]')
	par.add_option('-c', '--config', action='store', dest='config', default='WebGrab++.config.xml', help=u'config output with full path [default: %default]')
	opt, args = par.parse_args()
	write_config(opt.file, opt.mode, opt.timespan, opt.config)

if __name__ == '__main__':
	main()
