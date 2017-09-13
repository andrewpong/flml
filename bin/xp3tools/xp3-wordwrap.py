#!/usr/bin/env python

# Kirikiri Word-wrapper
#
#    To enable the use of English text word-wrapping in the game engine,
# you need patched versions of some .tjs system files, plus you need to
# preprocess your scripts with this program to add appropriate wrapping
# hints to the text.
#
# Last modification: 2006-07-08, Edward Keyes, ed-at-insani-dot-org

import string, re, sys


if len(sys.argv) != 3 :
   print 'Please give an input .ks script file and an output file on the command line.'
   sys.exit(0)

infile = open(sys.argv[1],'rb')
outfile = open(sys.argv[2],'wb')

# Some handy regular expressions used below, precompiled for speed
separatebybrackets = re.compile(r'[^\[]+|\[[^\]]*\]\s*')
   # Split into '[foo bar]' pieces and intervening text.
separateintowords = re.compile(r'[^ \-]+(?:[ \-]+|$)|\s+')
   # Splits regular text by whitespace and hyphens.
matchlinecommand = re.compile(r'\[line(\d+)\]')
   # A [line] command.  Also captures the value for later use.

line = infile.readline()
scriptsection = False
while line != '' :
   line = line.rstrip()   # Strip linefeeds and trailing spaces
   if (not scriptsection) and (line!='' ) and (line[0] not in ('@','*',';')) :
      pieces = []
      # Split by bracketed commands...
      for match in separatebybrackets.finditer(line) :
         if match.group()[0] == '[' :
            pieces.append(match.group())
         else :
            # ... and then into words for non-bracketed text
            for submatch in separateintowords.finditer(match.group()) :
               pieces.append(submatch.group())
      newpieces = []
      # Now concatenate [line] commands back into regular text if not spaced
      addtoprevious = False
      for piece in pieces :
         if matchlinecommand.match(piece) :
            if newpieces[-1][-1] in (' ','-') :
               newpieces.append(piece)
            else :
               newpieces[-1] += piece
            addtoprevious = True
         else :
            if addtoprevious and (newpieces[-1][-1] not in (' ','-')) :
               newpieces[-1] += piece
            else :
               newpieces.append(piece)
            addtoprevious = False
      line = ''
      # Now reconstruct new line with [wrap] commands embedded.
      for piece in newpieces :
         if (piece[0]!='[') or matchlinecommand.match(piece) :
            wraptext = piece
            for match in matchlinecommand.finditer(piece) :
               wraptext = re.sub(r'\[line'+match.group(1)+r'\]',
                                 '--'*int(match.group(1)), wraptext, 1)
               # Replace line commands by that number of dashes in wrap hint
            wraptext = wraptext.rstrip()
            wraptext = wraptext.replace('"','-')   # To avoid quoted quotes
            line += '[wrap text="' + wraptext + '"]' + piece
         else :
            line += piece
   else :
      if line == '@iscript' :
         scriptsection = True
      elif line == '@endscript' :
         scriptsection = False
   outfile.write(line+'\x0D\x0A')   # Force Windows linefeeds
   line = infile.readline()

infile.close()
outfile.close()
