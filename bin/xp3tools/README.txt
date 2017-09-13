          XP3 / KIRIKIRI TOOLSET DOCUMENTATION

          Edward Keyes, ed-at-insani-dot-org
          Last modified: 2006-07-08


I'M-TOO-BUSY-TO-READ-DOCUMENTATION SUMMARY

* xp3-extract.exe <file.xp3> <to_where> to extract XP3 archives

* xp3-repack.exe <from_where> <newfile.xp3> to repack them

* xp3-wordwrap.exe <script.ks> <newscript.ks> to word-wrap scripts

* To make the wordwrapping work, you will need to do something with the
  three .tjs files included in this tool set.  You'll need to read below
  to find out exactly what, when you're ready to do this.

* The "library.zip" file is part of the Python library.  Don't unpack it.


RUNNING THE COMMANDS

The utilities were written in Python, and precompiled binaries for the
Windows platform have been included, along with the appropriate DLLs and
support files (which are mostly packed up in library.zip and are accessed
directly by the executables, so you don't have to do anything).  If you are
running on a different platform or prefer running directly from the source,
the Python code has also been included.  The command-line options are the
same in both cases.

     xp3-extract.exe <file.xp3> <to_where> [encryption]

This command unpacks an XP3 archive to a new (or existing) directory.  It
will create subdirectories as needed if the archive contains them.  The
XP3 archive allows unicode filenames, and hopefully your operating system
does too, otherwise you may get some errors with Japanese characters.

The optional encryption parameter specifies what to do with files tagged
as encrypted.  The toolset currently implements at least the "fate_trial"
and "fate_full" encryption schemes for the trial and full commercial
versions of Fate Stay Night.  If you run across a game which seems to use
a different encryption scheme and want the toolset updated to include it,
please contact me with an example archive or few.

     xp3-repack.exe <from_where> <newfile.xp3> [encryption]

This is the opposite command from xp3-extract, taking a directory of files
(including subdirectories) and packing them into a new XP3 archive.
Compression will be used when it saves more than 5% of a file's size,
otherwise they will be stored uncompressed for speed of access.

The optional encryption parameter specifies whether all of the files should
be encrypted by the specified method; if not specified, files will be left
unencrypted.

     xp3-wordwrap.exe <script.ks> <newscript.ks>

While the standard Kirikiri engine can display English text, it does not know
how to word-wrap automatically, since Japanese text doesn't require it.  To
enable this, it is necessary to patch several Kirikiri system files (see
below) and to preprocess your script files with the xp3-wordwrap tool to add
wordwrapping hint commands.

The preprocessing tends to destroy the editability of your script, so it is
recommended that you keep separate copies of your files and only process
them when you create a patch.  You don't need to process .ks files which
don't contain text requiring word-wrapping.


HOW TO TRANSLATE A GAME

The script files are usually stored in the "scenario" directory in an XP3
archive, as .ks files.  These files are in the Shift-JIS character encoding
and are editable with a normal text editor.  They consist of a mix of actual
script text and formatting/presentation commands, usually denoted by square
brackets.  Some of them, such as the "first.ks" file, may be pure commands
and not contain any script text.

Additional Japanese phrases for the user interface can also be scattered
through .tjs files in the "system" directory.  The most fruitful thing to
do is to just search in this directory and in "scenario" for any strings
you run across while exploring the game, to find out which files to edit.

Images may need to be translated as well, and they are present in other
subdirectories.  Many games will just use standard JPEG and PNG image formats,
but some may use Kirikiri-specific formats like TLG, requiring an additional
conversion step before editing.  Beta tools exist for the TLG5 image format,
but I've not included them in this toolset, and the TLG6 format is also being
used in some games but is presently unexamined.  If you run across a game
using one of these that you want to translate, contact me for assistance.


WHAT TO DO WITH THE .TJS FILES

To enable the word-wrapping, some additional functionality needs to be
integrated into the Kirikiri system files.  Specifically, modifications
need to be made to:

     HistoryLayer.tjs
     MainWindow.tjs
     MessageLayer.tjs

which are typically stored in the "system" subdirectory of an XP3 archive.

Premodified versions of those files are included in this toolset, taken from
the game "Until We Meet Again".  If you're feeling lucky and/or lazy, you
can just toss these files into your patch as is and cross your fingers.

However, if your game is using a somewhat different version of the Kirikiri
engine, this may cause problems.  The better approach is to manually edit
the three corresponding files in your game to insert the modified sections.
All modifications are denoted by "insani" comment strings, so you can search
for them, find the parallel sections in your game files, and copy-and-paste
to match.  There are just a couple of modified sections per file, so this
shouldn't take you very long, and is recommended instead of the just-try-it
method.


HELPFUL TIPS

Usually as part of its startup script, a Kirikiri game will look for files
named "patch.xp3", "patch2.xp3", etc. and use the contents to override files
in the main archive(s).  You can use this to distribute your own patches
without needing to modify the original archives at all, and it's great for
maintaining multiple versions of your patch for testing purposes.

Note that when constructing a patch archive, it should be flat (without
subdirectories), even if the files you override are in a subdirectory: the
engine goes solely by the bare filename, so also make sure your names are
globally unique if you add new files.

While you're editing the .tjs files, you may also want to play with the
margin settings defined there.

Sometimes files will be marked as encrypted in an archive even though they
are actually not.  In other words, examine them to see if they're okay first
before getting worried about the warning messages you get from xp3-extract.


POSSIBLE TROUBLE SPOTS

Unicode filenames can be a point of trouble.  The tools make a good effort
to use the encoding provided by your operating system, but XP3 archives use
16-bit unicode filenames internally.  In some cases I've seen a filesystem
mangle the unicode slightly so that the filenames read back are not bit-for-
bit identical to the ones originally used when the archive was extracted.
Just bear this in mind if your patch provokes some inexplicable "missing
file" errors even though you're sure you've included those files.

Some archives purposefully include a small "do not copy this data" text
file with a huge name.  While the tools will attempt to extract this file
normally, many operating systems will choke on large filenames, and this
will provoke an error message.  The extraction will continue regardless in
this case, but that (probably useless) file will be skipped.

Some games do not come with separate XP3 archive files, but instead
incorporate one directly into their executable.  The tools are unfortunately
not intelligent enough to deal with this situation yet.  If you're handy with
a hex editor you can copy-and-paste the XP3 file out of the executable.  Look
for probably the final instance of the signature string:

     XP3\x0D\x0A\x20\x0A\x1A\x8B\x67\x01

to denote the start of the embedded archive.  Or if you have no idea what I
just said, you can just contact me and I can do it for you.

I'm not completely sure whether the encryption options for the full Fate
Stay Night game are correct, since I do not own a copy myself for proper
testing.  It should be pretty close, at least.

The word-wrapping code may do odd things in unanticipated cases, and won't
handle cases of programmatically-generated text well (such as a variable for
the name of the protagonist).  If you run across a case where it is failing,
please contact me for a fix or consider manually editing the wrapping hints
to match what should be happening.
