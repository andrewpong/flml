#!/usr/bin/env python

# KiriKiri .XP3 archive extraction tool
#
#   Extracts an .XP3 archive to a directory of files, including any
# subdirectory structure.  Does aggressive error-checking, so some
# assertions may have to be disabled with nonstandard XP3 files.
#
#   Optionally handles Fate Stay Night encryption.
#
# Last modified 2006-07-08, Edward Keyes, ed-at-insani-dot-org

import sys, os, zlib
from array import array
from cStringIO import StringIO
from insani import *


if len(sys.argv) not in (3,4) :
   print 'Please give an XP3 archive filename and a desired output directory on the\ncommand line.  Append an optional encryption type.'
   sys.exit(0)


def read_entry(infile) :
# Reads a file entry and creates a data structure from it.
   result = {}
   assert_string(infile,'File',ERROR_ABORT)
   entrylength = read_unsigned(infile,LONG_LENGTH)
   assert_string(infile,'info',ERROR_ABORT)
   infolength = read_unsigned(infile,LONG_LENGTH)
   result['encrypted'] = read_unsigned(infile)
   result['origsize'] = read_unsigned(infile,LONG_LENGTH)
   result['compsize'] = read_unsigned(infile,LONG_LENGTH)
   filenamelength = read_unsigned(infile,SHORT_LENGTH)
   result['filepath'] = u''
   for i in xrange(filenamelength) :
      result['filepath'] += unichr(read_unsigned(infile,SHORT_LENGTH))
   assert (infolength == filenamelength*2+22)
   assert_string(infile,'segm',ERROR_ABORT)
   numsegments = read_unsigned(infile,LONG_LENGTH) // 28   # 28 bytes per seg.
   result['segments'] = []
   compsize = origsize = 0
   for i in xrange(numsegments) :
      segment = {}
      segment['compressed'] = read_unsigned(infile)
      segment['offset'] = read_unsigned(infile,LONG_LENGTH)
      segment['origsize'] = read_unsigned(infile,LONG_LENGTH)
      segment['compsize'] = read_unsigned(infile,LONG_LENGTH)
      compsize += segment['compsize']
      origsize += segment['origsize']
      result['segments'].append(segment)
   assert (compsize == result['compsize'])
   assert (origsize == result['origsize'])
   assert_string(infile,'adlr',ERROR_ABORT)
   assert (read_unsigned(infile,LONG_LENGTH) == 4)
   result['adler'] = read_unsigned(infile)      
   assert (entrylength == filenamelength*2+numsegments*28+62)
   return result


def decrypt(outfile, encryption) :
# Performs standard types of XP3 decryption on a file.
   if encryption == 'fate_trial' :
      outfile.seek(0)
      data = array('B',outfile.read())
      for i in xrange(len(data)) :
         data[i] ^= 0x0052
      if len(data)>30 :
         data[30] ^= 0x0001
      if len(data)>55355 :
         data[55355] ^= 0x0020
      outfile.seek(0)
      outfile.write(data.tostring())
   elif encryption == 'fate_full' :   # Not 100% sure about these values.
      outfile.seek(0)
      data = array('B',outfile.read())
      for i in xrange(len(data)) :
         data[i] ^= 0x0036
      if len(data)>19 :
         data[19] ^= 0x0001
      outfile.seek(0)
      outfile.write(data.tostring())
   else :
      print 'WARNING: File is encrypted but no known encryption type specified'
      print 'Known types include: fate_trial, fate_full'


arcfile=open(sys.argv[1],'rb')
filesize=os.stat(sys.argv[1]).st_size
dirname=sys.argv[2]
if (len(sys.argv)==4) :
   encryption = sys.argv[3]
else :
   encryption = 'none'

# Read header and index structure
assert_string(arcfile,'XP3\x0D\x0A \x0A\x1A\x8B\x67\x01',ERROR_ABORT)
indexoffset = read_unsigned(arcfile,LONG_LENGTH)
assert (indexoffset < filesize)
arcfile.seek(indexoffset)
assert_string(arcfile,'\x01',ERROR_WARNING)
compsize = read_unsigned(arcfile,LONG_LENGTH)
origsize = read_unsigned(arcfile,LONG_LENGTH)
assert (indexoffset+compsize+17 == filesize)
uncompressed = arcfile.read(compsize).decode('zlib')
assert (len(uncompressed) == origsize)
indexbuffer = StringIO(uncompressed)

# Read through the index structure, extracting each file
while (indexbuffer.tell() < origsize) :
   entry = read_entry(indexbuffer)
   print 'Extracting %s (%d -> %d bytes)' % \
         (entry['filepath'].encode(sys.getfilesystemencoding()),
          entry['compsize'], entry['origsize'])
   pathcomponents = entry['filepath'].split(u'/')
      # Paths inside the XP3 use forward slashes as separators
   filepath = dirname
   for elem in pathcomponents:
      if not os.path.isdir(filepath) :   # Create directory if it's not there
         os.mkdir(filepath)              # Won't do this for the final filename
      filepath=os.path.join(filepath,elem.encode(sys.getfilesystemencoding()))
   outbuffer = StringIO()
   adler = zlib.adler32('')  # Initialize checksum for incremental updates
   for segment in entry['segments'] :
      arcfile.seek(segment['offset'])
      if (segment['compressed']) :
         data = zlib.decompress(arcfile.read(segment['compsize']))
      else :
         data = arcfile.read(segment['compsize'])
      assert (len(data) == segment['origsize'])
      outbuffer.write(data)
      adler = zlib.adler32(data,adler)
   if entry['encrypted'] :
      decrypt(outbuffer,encryption)
   if (((adler + 0x0100000000L) & 0x00FFFFFFFFL) != entry['adler']) :
      # Convert to unsigned 32-bit integer
      print 'Checksum error, but continuing...'
   try :
      # Why worry about exceptions?  There's a known problem with archives
      # including a "do not copy this!" file with a huge filename that many
      # filesystems will choke on.  We still want to continue if we hit that.
      outfile = open(filepath,'wb')
      outfile.write(outbuffer.getvalue())
      outfile.close()
   except IOError :
      print 'Problems writing %s, but continuing...' % filepath

indexbuffer.close()
arcfile.close()
