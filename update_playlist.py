#!/usr/bin/env python
# -*- coding: utf-8 -*-import re, urllib2, codecs
import re, urllib2, codecs, operator
from BeautifulSoup import BeautifulSoup # sudo apt-get install python-beautifulsoup
from optparse import OptionParser

channelsIN = dict()
channelsXML = dict()

# The piece of code below is taken FROM m3u2hts.py - Generate TVHeadend 3.x channel/tag configuration files from BY (c) 2012 Gregor Rudolf
def read_m3u(infile, removenum, channumbering, inputcodec):
	PROGNUM = re.compile(r"(\d+) - (.*)")  # #EXTINF:0,1 - SLO 1 -> #1 - num, 2 - ime
	CHAN_NUMBERING_GENERATE = 0
	CHAN_NUMBERING_DURATION = 1
	CHAN_NUMBERING_NAMES = 2
	instream = codecs.open(infile, "Ur", encoding=inputcodec)
	chancnt = 0
	tagcnt = 0
	chname = ''
	chtags = None
	chlanguage = None
	chnumber = None
	chxmltv = None
	chicon = None
	for line in instream.readlines():
		line = line.strip()
		if line.startswith("#EXTINF:"):
			#EXTINF:duration,channel number - channel name
			buff = line[8:].split(',')
			m = PROGNUM.search(buff[1])
			if removenum and m:
					chname = m.group(2)
			else:
					chname = buff[1]
			if m and channumbering == CHAN_NUMBERING_NAMES:
					chnumber = m.group(1)
			elif channumbering == CHAN_NUMBERING_DURATION:
					chnumber = buff[0]
		elif line.startswith('#EXTTV:'):
			#EXTTV:tag[,tag,tag...];language;XMLTV id[;icon URL]
			buff = line[7:].split(';')
			chtags = buff[0].split(',')
			chlanguage = buff[1]
			chxmltv = buff[2]
			chicon = buff[3] if len(buff) > 3 else None
		elif line.startswith('udp://@'):
			chancnt += 1
			if channumbering == CHAN_NUMBERING_GENERATE: chnumber = chancnt
			if ':' in line[7:]:
				chip, chport = line[7:].rsplit(':', 1)
			else:
				continue
			if chname in channelsIN:
					print "%s already exists" % chname
					chname = chname + '.'
			channelsIN[chname] = {'num': chancnt, 'number': chnumber, 'name': chname, 'tags': chtags, 'lang': chlanguage,
													 'ip': chip, 'port': chport, 'xmltv': chxmltv, 'icon': chicon}
			chname = ''
			chtags = None
			chlanguage = None
			chnumber = None
			chxmltv = None
			chicon = None
		else:
				continue
# --m3u2hts.py

def read_csv(inputfile, inputcodec):
	instream = codecs.open(inputfile, "Ur", encoding=inputcodec)
	chname = None
	for line in instream.readlines():
		line = line.strip().split(',')
		if line[0].isdigit():
			if len(line) is 10:
				channelsIN[line[1]] = {'num': line[0], 'name': line[1], 'tags': line[3], 'lang': line[4],
														 'ip': line[5].split(':')[0], 'port': line[5].split(':')[1], 'xmltv': line[6], 'icon': line[9]}
			else:
				channelsIN[line[1]] = {'num': line[0], 'name': line[1], 'tags': line[3]+','+line[4], 'lang': line[5],
														 'ip': line[6].split(':')[0], 'port': line[6].split(':')[1], 'xmltv': line[7], 'icon': line[10]}
			chname = None
		else:
			continue
				
def read_data():
	url = "" # enter URL of webpage from where you're parsing channel names and URLs for EPG
	soup = BeautifulSoup(urllib2.urlopen(url).read());
	data = str(soup.find(id='')) # enter div id where channel names are stored
	for match in re.findall('', data): # enter regex for parsing channel names and URLs for EPG
		channelsXML[match[2]] = {'xmltv': match[0], 'name':match[2]}
		# match[0] is XMLTV identification string
		# match[2] is channel name
		# change these settings to your type of data
		
def write_playlist(output_file, file_type, codec):
	for channel in sorted(channelsIN.values(), key=lambda channel: channel['name']):
		if not channel['xmltv']:
			continue
		else:
			for chanel in sorted(channelsXML.values(), key=lambda chanel: chanel['name']):
				if (channel['name'].strip() == chanel['name'].decode('UTF-8').strip()):
					channel['xmltv'] = chanel['xmltv']
				tanimotoVal = None
	playlist = codecs.open(output_file, 'w+', codec)
	if file_type == 'm3u':
		playlist.write('#EXTM3U\n#EXTNAME:Updated Playlist'+'\n\n');
		for channel in sorted(channelsIN.values(), key=lambda channel: float(channel['num'])):
			playlist.write('#EXTINF:'+str(channel['num'])+','+channel['name']+'\n');
			playlist.write('#EXTTV:'+(",".join(channel['tags']) if isinstance(channel['tags'], list) else channel['tags'])+';'+channel['lang']+';'+channel['xmltv']+(';'+channel['icon'] if channel['icon'] else '')+'\n');
			playlist.write('udp://@'+channel['ip']+':'+str(channel['port'])+'\n\n');
	elif file_type == 'csv':
		playlist.write('Channel,Name,Locked,Group,Language,Ip,Epg 1,Epg 2,Epg 3,Logo\n');
		for channel in sorted(channelsIN.values(), key=lambda channel: float(channel['num'])):
			playlist.write(str(channel['num'])+','+channel['name']+',0,'+(",".join(channel['tags']) if isinstance(channel['tags'], list) else channel['tags'])+','+channel['lang']+','+channel['ip']+':'+channel['port']+','+channel['xmltv']+',,,'+(channel['icon'] if channel['icon'] else '')+'\n');
	playlist.close();

def main():
	par = OptionParser(usage="%prog [options]", description="Update each channel's XMLTV id from website")
	par.add_option('-o', '--output', action='store', dest='output', help=u'm3u output file with full path')
	# Options below are from m3u2hts.py
	par.add_option('-d', '--deletenum', action='store_true', help=u'remove program numbers from names')
	par.add_option('-n', '--numbering', type='int', default=0, help=u'program numbers are generated(0), determined from duration(1) or extracted from program names(2)')
	par.add_option('-c', '--codec', action='store', dest='codec', default='UTF-8', help=u'input file encoding [default: %default]')
	opt, args = par.parse_args()
	if len(args) == 1:
		read_csv(args[0], opt.codec)
		file_format = args[0].rsplit('.', 1)[1]
		if file_format == 'm3u':
			read_m3u(args[0], opt.deletenum, opt.numbering, opt.codec)
		elif file_format == 'csv':
			read_csv(args[0], opt.codec)
		read_data()
		if opt.output:
			file_format = opt.output.rsplit('.', 1)[1]
			write_playlist(opt.output, file_format, opt.codec)
		else:
			write_playlist(args[0], file_format, opt.codec)
	else:
		par.print_help()

if __name__ == '__main__':
    main()
