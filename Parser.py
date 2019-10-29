#
# @(#) $Id: Parser.py,v 1.7 2003/08/25 19:00:45 ivm Exp $
#
# $Author: ivm $
#
# $Log: Parser.py,v $
# Revision 1.7  2003/08/25 19:00:45  ivm
# Reverted back to not-converting floating points from string to numeric
#
# Revision 1.6  2003/02/25 15:35:32  ivm
# *** empty log message ***
#
# Revision 1.5  2000/08/14 20:15:17  ivm
# Accept continuation lines in config file. Line with no '=' in
# it is treated as a continuation of previous line.
#
# Revision 1.4  2000/02/22 19:12:32  ivm
# Fixed bug with parseWords call
#
# Revision 1.3  2000/02/22 19:04:45  ivm
# Added maxWords parameter to Parser.parseWords()
#
# Revision 1.1  2000/01/27 20:55:55  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:04  ivm
# Added modules to FBSNG
#
# Revision 1.4  1998/07/24 17:29:45  ivm
# Treat tabs, spaces and new-line characters as white space
#
# Revision 1.3  1998/07/22 20:28:29  ivm
# Add parseConfig() method for parsing configuration files.
#
# Revision 1.1  1998/07/09 15:51:49  ivm
# Initial deposit of Parser.py Selector.py SockStream.py
#
# Revision 1.5  1998/07/06  23:04:34  ivm
# Add comments and cleaned out debug output
#
# Revision 1.4  1998/07/06  22:34:42  ivm
# Add parseWords method
#
# Revision 1.3  1998/07/06  18:23:59  ivm
# *** empty log message ***
#
#
# Parser is a collection of functions which can be used for parsing 
# strings like
#
#       name = word1 word2 word3 ...
#
# or just
#
#       word1 word2 word3
#
# Here, words are space delimited strings of characters. Quotes (' or ")
# may be used for words with spaces in the middle. If single quotes are
# used, then double quotes may appear in the word and wise versa.
#
# Examples of words:
#       abcd
#       a_b_c_d
#       'aa bb cc'
#       "this word has a ' quote in the middle"
#
# Comments in text
# ----------------
#
# If a word is unquoted AND begins with '#', this word and the rest of the line
# are ignored. Examples:
#
#       'this word is single word with # in the middle'
#       first second head#tail  --> Those are three words: 'first', 'second' and
#                                   'head#tail', because the last word does
#                                   not *begin* with pound.
#       first '#tail' -->           are two words: 'first' and '#tail'
#                                   because '#tail' is quoted
#       first #second -->           is inly one word 'first', the rest is 
#                                   treated as comment
#
# If a word appears to be integer number representation, it will be
# returned as integer, not string if such conversion is requested.
# 
# The methods are:
#
#       parseWords(string, cvtInts = 1) 
#               Parses list of words, returns list of strings and/or numbers. 
#               If cvtInts == 0, does not try to convert strings to integers
#               For example:
#
#               parseWords('aa bb cc "dd ee" 3') returns:
#               ['aa','bb','cc','dd ee',3]
#               parse('x') returns ['x']
#
#       wordsToDict(strOrWords, defValue = None, cvtInts = 1)
#               Converts string in format
#                       key:value key:value ...
#               into dictionary. Spaces around ':' are not allowed.
#               If a value is missing for a key, defValue is used.
#               List of words returned by parseWords can be supplied as
#               strOrWords. In this case, each word will be parsed as
#               "key:value".
#
#       parseLine(string, cvtInts = 1)
#               Designed to parse line of configuration file of the form:
#                       name = word1 word2 ...
#               Returns tuple (name, list-of-words). If the line does not
#               have '=' inside, or it is commented out by '#',
#               returns (None, None)
#               For example:
#
#               parseLine('command = /bin/ls file1 file2') returns:
#               ('command',['/bin/ls','file1','file2'])
#
#       parseFile(file, cvtInts = 1)
#               Calls parseLine for each line in the file. Returns 
#               Python dictionary with all parsed parameters.
#               The argument (file) can be either string with file
#               name to read, or standard Python file object.
#               For example, for file:
#               
#               This is comment line because it has no equal sign
#               queue = short
#               user = ivm acpmaps
#               comment = 'this is my command file' # debug
#               command = ls /tmp
#
#               it returns dictionary:
#
#               {       'queue' :       ['short'],
#                       'user'  :       ['ivm','acpmaps'],
#                       'comment':      ['this is my command file'],
#                       'command':      ['ls','/tmp']
#               }
#
#       parseConfig(file)
#               Modification of parseFile() taylored for parsing configuration
#               files:
#               - it always tries to convert to integers
#               - if value list consists of only one element, return this
#                 element instead of list of one element.
#
#               For example:
#
#               If the file is:
#               a = b
#               c = 1 2 x
#
#               parseFile(file, 0) will return
#               { 'a': ['b'], 'c': ['1','2','x'] }
#
#               parseConfig(file) will return
#               { 'a':'b', 'c':[1,2,'x']}
#

def wordsToDict(strOrWords, defValue = None, cvtInts = 1):
        dict = {}
        if type(strOrWords) == type(''):
                words = parseWords(strOrWords, cvtInts = 0)
        else:
                words = strOrWords
        for w in words:
                if not w:       continue
                inx = w.find(':')
                if inx < 0:
                        k = w
                        v = defValue
                else:
                        k = w[:inx]
                        v = w[inx+1:]
                        if cvtInts:
                                try:    v = int(v)
                                except: pass
                dict[k] = v
        return dict             

def     parseLine(str, cvtInts = 1):
        name = None
        rest = str
        ipound = str.find('#')
        ieq = str.find('=')
        if ieq > 0 and (ipound > ieq or ipound < 0):
                name = str[:ieq].strip()
                rest = str[ieq+1:].strip()
        words = parseWords(rest, cvtInts = cvtInts)
        return name, words

def     _findAny(str, chars):
        inx = -1
        for c in chars:
                i = str.find(c)
                if inx < 0 or (i > 0 and i < inx):
                        inx = i
        return inx

def     _stripHead(str, chars):
        i = 0
        for c in str:
                if c in chars:  i = i + 1
                else:           break
        return str[i:]

def     getWord(str, delim = ' \t\n'):
        str = _stripHead(str, delim)
        inx = _findAny(str,delim)
        if inx < 0:     return str, ''
        rest = _stripHead(str[inx:], delim)
        return str[:inx], rest
        
def     parseFile(file, cvtInts = 1):
        needToClose = 0
        if type(file) == type(''):
                file = open(file,'r')
                needToClose = 1
        dict = {}
        str = file.readline()
        while str:
                name, list = parseLine(str, cvtInts)
                if name != None:
                        dict[name] = list
                str = file.readline()
        if needToClose:
                file.close()
        return dict

def     parseConfig(file):
        dict = parseFile(file)
        for name, lst in list(dict.items()):
                if len(lst) == 1:
                        dict[name] = lst[0]
        return dict

def     parseWords(str, maxWords = -1, cvtInts = 1):
        words = []
        rest = str.strip()
        while rest and (maxWords < 0 or len(words) < maxWords):
                if rest[0] == "'":
                        word, rest = getWord(rest[1:], "'")
                elif rest[0] == '"':
                        word, rest = getWord(rest[1:], '"')
                else:
                        word, rest = getWord(rest)
                        if len(word) > 0 and word[0] == '#':
                                break   # comment
                if cvtInts:
                        try:    word = int(word)
                        except ValueError:
                                pass
                rest = rest.strip()
                words.append(word)
        if maxWords < 0:
                return words
        else:
                return words, rest

if __name__ == '__main__':
        import sys
        line = sys.stdin.readline()
        while line:
                print('Parse Line ->', parseLine(line))
                print('Parse Words(3) ->', parseWords(line, 3))
                line = sys.stdin.readline()
