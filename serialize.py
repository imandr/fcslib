#
# @(#) $Id: serialize.py,v 1.4 2002/08/16 17:58:07 ivm Exp $
#
# $Log: serialize.py,v $
# Revision 1.4  2002/08/16 17:58:07  ivm
# Make suze serialized long ends with L even in Python 2.x
#
# Revision 1.3  2002/05/07 15:25:20  ivm
# Fixed some bugs
# Added Long type to serialize
#
# Revision 1.2  2000/10/24 16:04:01  ivm
# Added true string serialization/deserialization
#
# Revision 1.1  2000/08/22 14:22:19  ivm
# Added serialize.com
#
#

def serializeString(s):
        r = repr(s)
        return '"%d:%s' % (len(r),r)

def serializeTuple(x):
        str = ''
        for y in x:
                if str: str = str + ' '
                str = str + serialize(y)
        return str

def serializeList(x):
        str = ''
        for y in x:
                if str: str = str + ' '
                str = str + serialize(y)
        return str

def serializeDict(x):
        str = ''
        for k, v in list(x.items()):
                if str: str = str + ' '
                str = str + ('%s %s ' % (serialize(k),serialize(v)))
        return str

def serializeObject(x):
        cls = x.__class__
        return '%s %s %s' % (cls.__module__, cls.__name__,
                serialize(x.__dict__))

def serialize(x):
        if type(x) == type(''):
                return serializeString(x)
        elif type(x) == type(1):
                return '%d ' % x
        elif type(x) == type(1):
                str = '%s' % x
                if str[-1] != 'L':      str = str + 'L'
                return str + ' '
        elif type(x) == type(1.0):
                return '%g ' % x
        elif x is None:
                return 'N'
        elif type(x) == type(()):
                return '(%s)' % serializeTuple(x)
        elif type(x) == type([]):
                return '[%s]' % serializeList(x)
        elif type(x) == type({}):
                return '{%s}' % serializeDict(x)
        else:
                return '<%s>' % serializeObject(x)

def deserialize(str):
        return _parse(str)
                
def _parse(str):
        # returns object, rest
        # generates SyntaxError, (reason, unparsed text)
        str = str.strip()
        c = str[0]
        if c == '(':
                t, rest = _parse_list_or_tuple(str[1:],')')
                return tuple(t), rest
        elif c == '{':
                d, rest = _parse_dict(str[1:])
                return d, rest
        elif c == 'N':
                return None, str[1:]
        elif c == '"':
                s, rest = _parse_string(str[1:])
                return s, rest
        elif c == '[':
                l, rest = _parse_list_or_tuple(str[1:],']')
                return l, rest
        elif c == '<':
                o, rest = _parse_object(str[1:])
                return o, rest
        else:
                n, rest = _parse_number(str)
                return n, rest
                
def _parse_number(str):
        # integer or floating point number
        l = len(str)
        i = str.find(' ')
        if i >= 0:
                l = i
        x = str[:l].strip()
        rest = str[l:]
        if len(x) > 1 and x[-1] == 'L':
                n = eval(x)
                return n, rest.strip()
        try:    n = int(x)
        except: pass
        else:   return n, rest
        try:    n = float(x)
        except: raise SyntaxError('Unrecognized input',str)
        return n, rest.strip()

def _parse_string(str):
        i = str.find(':')
        if i < 0:
                raise SyntaxError('String length not found', str)
        try:
                l = int(str[:i])
        except:
                raise SyntaxError('Wrong format of string lenght', str)
        return eval(str[i+1:i+1+l]), str[i+1+l:]

def _parse_list_or_tuple(str, end):
        lst = []
        str = str.strip()
        while str:
                if str[0] == end:
                        str = str[1:].strip()
                        break
                else:
                        x, rest = _parse(str)
                        lst.append(x)
                        str = rest.strip()
        return lst, str

def _parse_dict(str):
        dict = {}
        str = str.strip()
        while str:
                if str[0] == '}':
                        str = str[1:].strip()
                        break
                k, str = _parse(str)
                v, str = _parse(str)
                dict[k] = v
                str = str.strip()
        return dict, str

class   _Clay:
        pass

def _parse_object(str):
        str = str.strip()
        i = str.find(' ')
        if i < 0:
                raise SyntaxError('Can not find module name for object', str)
        mod = str[:i]
        str = str[i+1:].strip()
        i = str.find(' ')
        if i < 0:
                raise SyntaxError('Can not find class name for object', str)
        cls = str[:i]
        str = str[i+1:].strip()
        if str[0] != '{':
                raise SyntaxError('Can not find object dictionary', str)
        dict, str = _parse_dict(str[1:])
        env = {}
        try:
                exec('from %s import %s' % (mod, cls), env)
        except ImportError:
                raise SystemError("Failed to import class %s from module %s" % \
                        (cls, mod))
        o = _Clay()
        o.__class__ = env[cls]
        o.__dict__ = dict
        return o, str
        
if __name__ == '__main__':
        import time
        dict = {}
        for i in range(1000):
                dict['%d' % i] = (1,2,3)
        t = time.time()
        str = serialize(dict)
        t1 = time.time()
        print(str)
        print(len(str), t1 - t)
        d1, rest = deserialize(str)
        t2 = time.time()
        print(t2 - t1)
        if dict == d1:
                print('ok')
