# @(#) $Id: config.py,v 1.9 2003/08/22 18:38:42 ivm Exp $
#
# Config.py -- uniform configuration file access class. Reads 
# (configuration) file in format:
#
# %set <type> [<name>|<pattern>]
# param1 = value [...] # comment
# param2 = value [...]
#
# <pattern> can be either standard Regular Expression, or
# a range specification in format:
#
#       <head><<number1>-<number2>>
#
# In this case, the pattern will match any string which looks like:
#
#       <head><number>
#
# as long as the number1 <= number <= number2 and <head> is the same.
#
# If number1 is padded with leading zeros so that is has the same
# length as number2, the number must have the same length.
#
# For example:
# Pattern              Set name               Match ?
# -------------------  -------------------    -------
# abc<1-100>           abc7                   yes
# abc<1-100>           abc00007               yes
# abc<1-100>           xyz100                 no
# abc<001-100>         abc7                   no
# abc<001-100>         abc007                 yes
# abc<001-100>         abc00007               no
#
# ConfigFile class interface:
#
# Constructor:
# ------------
#       ConfigFile(file-name)   - opens the configuration file and reads all the
#                                 information into internal data structure. Makes
#                                 the information ready to be retrieved by
#                                 other class methods
#
#       getValue(set-name, client-id, field-name) - returns value of the configuration
#                                 parameter specified by triplet 
#                                 <type, client-id, field-name>. If the field is not
#                                 defined for <type, client-id>, but has a value for
#                                 <type, '***'>, then the default (***) value is
#                                 returned.
#
#       getValueList(set-name, client-id, field-name) - same as getValue(),
#                                 but always returns list, even if value is a single
#                                 item. In such case, it returns list of single item.
#
#       names(set-name, client-id)      - returns list of field names defined for i
#                                 <set, client-id>, including those defined for 
#                                 <set, '***'>. 
#                                 This method can be used when field names are unknown:
#                               
#                                       cfg=ConfigFile('zoo.cfg')
#                                       for t in cfg.names('food','lion'):
#                                               print "Lion's dish for %s is %s" % (t,
#                                                       cfg.getValue('food','lion',t)
#
#       ids(set-name)           - returns list of client ids for defined for given set:
#                                 
#                                       for species in cfg.ids('food'):
#                                               print "Species: %s" % species
#                                 
#
#
#                               
#
# $Log: config.py,v $
# Revision 1.9  2003/08/22 18:38:42  ivm
# Implemented floating point values in config
# Fixed typo in Selector.unsubscribeObject
#
# Revision 1.8  2003/02/25 15:35:32  ivm
# *** empty log message ***
#
# Revision 1.7  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.6  2000/08/22 14:22:19  ivm
# Added serialize.com
#
# Revision 1.5  2000/08/14 20:15:18  ivm
# Accept continuation lines in config file. Line with no '=' in
# it is treated as a continuation of previous line.
#
# Revision 1.4  2000/06/23 15:40:11  ivm
# Implemented new format of relative time
#
# Revision 1.3  2000/06/09 16:37:17  ivm
# Use '***' instead of 'default'.
# Do not return '***' from ids()
#
# Revision 1.2  2000/02/22 19:12:33  ivm
# Fixed bug with parseWords call
#
# Revision 1.1  2000/01/27 20:55:56  ivm
# Initial deposit into FCSLIB
#
# Revision 1.1  2000/01/25 21:27:06  ivm
# Added modules to FBSNG
#
# Revision 1.10  1999/10/20 21:18:35  ivm
# Fixed futil for Linux
# Fixed ConfigFile::getValueList() returning None
#
# Revision 1.9  1999/08/16 18:40:30  ivm
# Added getValueList()
#
# Revision 1.8  1999/04/01 21:03:14  ivm
# Fixed bug with id starting with '#'
#
# Revision 1.7  1998/10/29 15:32:56  ivm
# Added documentation for methods
#
# Revision 1.6  1998/10/27 16:49:55  ivm
# Added ids() method
#
# Revision 1.5  1998/10/22 19:34:46  ivm
# Added ConfigFile.names() method
#
# Revision 1.4  1998/07/30 21:08:12  ivm
# Fixed problem with comments before and in between sets
#
# Revision 1.3  1998/07/30 15:10:23  ivm
# Add getValue() method
#
# Revision 1.2  1998/07/28 21:03:58  ivm
# *** empty log message ***
#
# Revision 1.1  1998/07/28 19:02:42  ivm
# Config.py -- configuration file access class
#
#
#
import Parser
import string
import re

class   ConfigFile:
        RangeRE = re.compile('(?P<head>.*)<(?P<begin>\d+)-(?P<end>\d+)>')
        StrNumRE = re.compile('(?P<head>[^0-9]*)(?P<num>\d+)')
        
        def __init__(self, file = None):
                self.Dict = {}
                if file:        self.readConfig(file)

        def getUpdate(self):
                return ConfigFile(self.File)

        def readConfig(self, file):
                self.File = file
                self.reReadConfig()
                #print self.Dict

        def reReadConfig(self):
                f = open(self.File, 'r')
                l = f.readline()
                self.Dict = {}
                curSet = None
                while l:
                        words = string.split(l)
                        if len(words) > 0 and words[0] == '%set':
                                l = self.readSet(words[1:], f)
                        else:
                                l = f.readline()
                f.close()

        def readSet(self, setname, f):
                if len(setname) >= 1:
                        client_type = setname[0]
                        client_id = '***'
                        if len(setname) >= 2 and setname[1][0] != '#':
                                client_id = setname[1]
                        if client_type not in self.Dict:
                                self.Dict[client_type] = {}
                        set = {}
                        l = f.readline()
                        while l:
                                w = Parser.parseWords(l)
                                if len(w) > 0 and w[0] == '%set':
                                        break
                                name, values = Parser.parseLine(l)
                                #print 'line:<%s> name:<%s> values:<%s>' % (l, name, values) 
                                l = f.readline()
                                if name != None:
                                        while l:
                                                lst = Parser.parseWords(l)
                                                if len(lst) > 0 and lst[0] == '%set':
                                                        break
                                                if not l[0] in [' ','\t']:
                                                        n1, lst = Parser.parseLine(l)
                                                        #print 'cont: ', n1, lst
                                                        if n1 != None:
                                                                break
                                                values = values + lst
                                                l = f.readline()
                                        set[name] = values
                        self.Dict[client_type][client_id] = set
                else:
                        l = f.readline()
                return l

        def rangeMatch(self, ptrn, theid):
                ptmatch = self.RangeRE.match(ptrn)
                if ptmatch == None or ptmatch.end() != len(ptrn):
                        return 0
                idmatch = self.StrNumRE.match(theid)
                if idmatch == None or idmatch.end() != len(theid):
                        return 0
                if ptmatch.group('head') != idmatch.group('head'):
                        return 0
                n1 = ptmatch.group('begin')
                n2 = ptmatch.group('end')
                n = idmatch.group('num')
                nn = string.atoi(n)
                if nn < string.atoi(n1) or nn > string.atoi(n2):
                        return 0
                return len(n1) != len(n2) or len(n) == len(n1)

        def idMatch(self, ptrn, theid):
                if self.rangeMatch(ptrn, theid):
                        return 1
                match = re.match(ptrn, theid)
                return match != None and match.group() == theid                 

        def __getitem__(self, type_id_name):
                c_type, c_id, p_name = type_id_name
                values = None
                try:
                        type_set = self.Dict[c_type]
                        if c_id in type_set:
                                try:    values = type_set[c_id][p_name]
                                except KeyError:
                                        pass
                        if values == None:
                                for ptrn, dict in list(type_set.items()):
                                        # if ptrn looks like <string><<number>-<number>>
                                        if ptrn != '***' and self.idMatch(ptrn, c_id) and \
                                                        p_name in dict:
                                                values = dict[p_name]
                                                break
                        if values == None:
                                values = type_set['***'][p_name]
                except KeyError:
                        pass
                if type(values) == type([]) and len(values) == 1:
                        return values[0]
                else:
                        return values

        def getValue(self, typ, id, name, deflt = None):
                v = self[(typ, id, name)]
                if v == None: v = deflt
                return v

        def getValueList(self, typ, id, name, deflt = None):
                v = self.getValue(typ, id, name, deflt)
                if v == None:   return None
                if type(v) != type([]): v = [v]
                return v

        def getValueDict(self, typ, id, name, defValue = None, cvtInts = 1):
                lst = self.getValueList(typ, id, name)
                if lst == None: return None
                dict = Parser.wordsToDict(lst, defValue, cvtInts)
                return dict
                        
        def names(self, typ, id):
                lst = []
                if typ in self.Dict:
                        found = 0
                        tdct = self.Dict[typ]
                        if id in tdct:
                                found = 1
                                lst = list(tdct[id].keys())
                        if not found:
                                for k, dct in list(tdct.items()):
                                        if k != '***' and self.idMatch(k, id):
                                                found = 1
                                                lst = list(dct.keys())
                                                break
                        if not found and '***' in tdct:
                                lst = list(tdct['***'].keys())
                return lst

        def ids(self, typ):
                lst = []
                if typ in self.Dict:
                        for k in list(self.Dict[typ].keys()):
                                if k != '***':
                                        lst.append(k)
                return lst

        def types(self):
                return list(self.Dict.keys())

        def hasSet(self, setType, setID = None):
                if setType not in self.Dict:
                        return 0
                if setID == None:       return 1
                return setID in self.Dict[setType]

def writeConfigFile(cfgdict, f):
        # writes configuration described by cfgdict to a file
        # cfgdict is in form:
        # set_type -> 
        #       { set_id or '' ->
        #               { field -> value or [values] or dict }
        do_close = 0
        if type(f) == type(''):
                f = open(f, 'w')
                do_close = 1
        for set_type, sets in list(cfgdict.items()):
                ids = list(sets.keys())
                ids.sort()
                for set_id in ids:
                        set_dict = sets[set_id]
                        f.write('%%set %s %s\n' % (set_type, set_id))
                        for fn, fv in list(set_dict.items()):
                                valstr = ''
                                if type(fv) == type(''):
                                        valstr = fv
                                elif type(fv) == type(1):
                                        valstr = '%d' % fv
                                elif type(fv) == type(1.0):
                                        valstr = '%f' % fv
                                elif type(fv) == type([]):
                                        for x in fv:
                                                valstr = valstr + '%s ' % x
                                elif type(fv) == type({}):
                                        for k, v in list(fv.items()):
                                                if v or type(v) == type(1):
                                                        valstr = valstr + '%s:%s ' % (k, v)
                                                else:
                                                        valstr = valstr + '%s ' % k
                                f.write('%s = %s\n' % (fn, valstr))
                        f.write('\n')
        if do_close:    f.close()
        
if __name__ == '__main__':
        import sys
        cfg = ConfigFile(sys.argv[1])
        print(cfg.names(sys.argv[2], sys.argv[3]))


                                
                                
                                
                                
                        
                                                
