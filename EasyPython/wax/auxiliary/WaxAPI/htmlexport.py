#---------------------------------------------------------------------------
# htmlexport.py
#   Export a module to HTML (hierarchial class listing)
#
#   NOTE:
#       This code is sloppy, but it gets the job done :)
#
#   TODO:
#       - 
#
#---------------------------------------------------------------------------

from types import ClassType, InstanceType, MethodType
from string import ascii_lowercase
import os

#
# Alternate names for __***__ properties
#
name_mapping = {
  '__init__': ('[constructor]', 'Usage: classname(arguments)'),

  '__neg__': ('[operator \'-\']', 'Usage: -a'),
  '__not__': ('[operator \'!\']', 'Usage: !a'),
  '__abs__': ('[operator \'abs\']', 'Usage: abs(a)'),
  '__pos__': ('[operator \'+\']', 'Usage: +a'),
  '__invert__': ('[operator \'~\']', 'Usage: ~a'),
  '__inv__': ('[operator \'~\']', 'Usage: ~a'),
  '__int__': ('[operator \'int\']', 'Usage: int(a)'),
  '__long__': ('[operator \'long\']', 'Usage: long(a)'),
  '__float__': ('[operator \'float\']', 'Usage: float(a)'),
  '__oct__': ('[operator \'oct\']', 'Usage: oct(a)'),
  '__hex__': ('[operator \'hex\']', 'Usage: hex(a)'),

  '__add__': ('[operator \'+\']', 'Usage: a + b'),
  '__sub__': ('[operator \'-\']', 'Usage: a - b'),
  '__mul__': ('[operator \'*\']', 'Usage: a * b'),
  '__div__': ('[operator \'/\']', 'Usage: a / b'),
  '__mod__': ('[operator \'%\']', 'Usage: a % b'),
  '__divmod__': ('[operator \'divmod\']', 'Usage: divmod(a, b)'),
  '__floordiv__': ('[operator \'//\']', 'Usage: a // b'),
  '__truediv__': ('[operator \'/\']', 'Usage: a / b'),
  '__and__': ('[operator \'&\']', 'Usage: a & b'),
  '__or__': ('[operator \'|\']', 'Usage: a | b'),
  '__xor__': ('[operator \'^\']', 'Usage: a ^ b'),
  '__lshift__': ('[operator \'<<\']', 'Usage: a << b'),
  '__rshift__': ('[operator \'>>\']', 'Usage: a >> b'),

  '__radd__': ('[operator \'+\']', 'Usage: a + b'),
  '__rsub__': ('[operator \'-\']', 'Usage: a - b'),
  '__rmul__': ('[operator \'*\']', 'Usage: a * b'),
  '__rdiv__': ('[operator \'/\']', 'Usage: a / b'),
  '__rmod__': ('[operator \'%\']', 'Usage: a % b'),
  '__rdivmod__': ('[operator \'divmod\']', 'Usage: divmod(a, b)'),
  '__rfloordiv__': ('[operator \'//\']', 'Usage: a // b'),
  '__rtruediv__': ('[operator \'/\']', 'Usage: a / b'),
  '__rand__': ('[operator \'&\']', 'Usage: a & b'),
  '__ror__': ('[operator \'|\']', 'Usage: a | b'),
  '__rxor__': ('[operator \'^\']', 'Usage: a ^ b'),
  '__rlshift__': ('[operator \'<<\']', 'Usage: a << b'),
  '__rrshift__': ('[operator \'>>\']', 'Usage: a >> b'),

  '__iadd__': ('[operator \'+=\']', 'Usage: a += b'),
  '__isub__': ('[operator \'-=\']', 'Usage: a -= b'),
  '__imul__': ('[operator \'*=\']', 'Usage: a *= b'),
  '__idiv__': ('[operator \'/=\']', 'Usage: a /= b'),
  '__imod__': ('[operator \'%=\']', 'Usage: a %= b'),
  '__ifloordiv__': ('[operator \'//=\']', 'Usage: a //= b'),
  '__itruediv__': ('[operator \'/=\']', 'Usage: a /= b'),
  '__iand__': ('[operator \'&=\']', 'Usage: a &= b'),
  '__ior__': ('[operator \'|=\']', 'Usage: a |= b'),
  '__ixor__': ('[operator \'^=\']', 'Usage: a ^= b'),
  '__ilshift__': ('[operator \'<<=\']', 'Usage: a <<= b'),
  '__irshift__': ('[operator \'>>=\']', 'Usage: a >>= b'),

  '__pow__': ('[operator \'**\']', 'Usage: a ** 2'),
  '__rpow__': ('[operator \'**\']', 'Usage: a ** 2'),
  '__ipow__': ('[operator \'**=\']', 'Usage: a **= 2'),

  '__len__': ('[operator \'len\']', 'Usage: len(a)'),
  '__concat__': ('[operator \'+\' (list)]', 'Usage: a + b'),
  '__repeat__': ('[operator \'*\' (list)]', 'Usage: a * b'),
  '__getitem__': ('[operator \'getitem\']', 'Usage: a[i]'),
  '__setitem__': ('[operator \'setitem\']', 'Usage: a[i] = b'),
  '__delitem__': ('[operator \'delitem\']', 'Usage: del a[i]'),
  '__getslice__': ('[operator \'getslice\']', 'Usage: a[i:j]'),
  '__setslice__': ('[operator \'setslice\']', 'Usage: a[i:j] = b'),
  '__delslice__': ('[operator \'delslice\']', 'Usage: del a[i:j]'),
  '__contains__': ('[operator \'contains\']', 'Usage: a in b'),

  '__repr__': ('[operator \'repr\']', 'Usage: repr(a)'),
  '__cmp__': ('[operator \'cmp\']', 'Usage: cmp(a, b)'),
  '__getattr__': ('[operator \'getattr\']', 'Usage: a.b'),
  '__setattr__': ('[operator \'setattr\']', 'Usage: a.b = c'),
  '__delattr__': ('[operator \'delattr\']', 'Usage: del a.b'),
  '__del__': ('[operator \'del\']', 'Usage: del a'),
  '__str__': ('[operator \'str\']', 'Usage: str(a)'),
  '__hash__': ('[operator \'hash\']', 'Usage: hash(a)'),
  '__le__': ('[operator \'<=\']', 'Usage: a <= b'),
  '__lt__': ('[operator \'<\']', 'Usage: a < b'),
  '__eq__': ('[operator \'==\']', 'Usage: a == b, a is b'),
  '__ne__': ('[operator \'!=\']', 'Usage: a != b, a <> b, a is not b'),
  '__gt__': ('[operator \'>\']', 'Usage: a > b'),
  '__ge__': ('[operator \'>=\']', 'Usage: a >= b'),
  '__coerce__': ('[operator \'coerce\']', 'Usage: coerce(a, b)'),
  '__nonzero__': ('[operator \'nonzero\']', 'Usage: None, used by core for things such as the not operator'),
  '__iter__': ('[operator \'iter\']', 'Usage: iter(a)'),
  '__call__': ('[operator \'call\']', 'Usage: func([arguments])'),
  '__print__': ('[operator \'print\']', 'Usage: print a, print(a)'),

  '__doc__': ('[member \'__doc__\']', 'Documentation for this class'),
  '__name__': ('[member \'__name__\']', 'The name of this class'),
  '__module__': ('[member \'__module__\']', 'The module that this class belongs to'),
  '__bases__': ('[member \'__bases__\']', 'The classes that this class inherits'),
  '__base__': ('[member \'__base__\']', 'The main super class of this class'),
  '__dict__': ('[member \'__dict__\']', 'The dictionary of attributes and methods for this class'),
  '__class__': ('[member \'__class__\']', 'A reference to this class\' type'),
 
  '__weakref__': ('[member \'__weakref__\']', 'No Documentation'),
  '__slots__': ('[member \'__slots__\']', 'If declared, reserves space for the variables it specifies'),
}


def write_main_item(f, name, doc, items=None, bases=None):
    lines = [
    '<div class="main_head">%s' % name,
    '  <div class="main_desc">%s</div>' % doc,
    ]

    if items and len(items) > 0:
        lines.append('  <ul class="main_list">')
        for x in items:
            lines.append('    <li><a href="#%s">%s</a></li>' % (x[1], x[0]))
        lines.append('  </ul>')

    if bases and len(bases) > 0:
        lines.append('  <div class="inherits">Inherits: ')
        for x in bases:
            lines.append('    <a href="%s.html">%s</a> ' % (x, x))
        lines.append('  </div>')

    lines.append('</div><br />')
    f.writelines(lines)

def write_sub_item(f, name, doc, anchor):
    f.writelines(
    ['<a name="%s" />' % anchor,
     '<div class="sub_head">%s' % name,
     '    <div class="sub_desc">%s</div>' % doc,
     '</div><br />',
    ])

def write_header(f):
    f.write( file('./support/main1.layout', 'r').read() )

def copy_files(directory):
    file(directory + '/waxapi.css', 'w').write( file('./support/waxapi.css', 'r').read() )
    file(directory + '/header.gif', 'wb').write( file('./support/header.gif', 'rb').read() )
    
def write_footer(f):
    f.write( file('./support/main2.layout', 'r').read() )

def write_module(module, directory, accepted):
    # make sure that directory exists
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            pass
            
    print 'Exporting to HTML...'
    
    temp = [(k, v) for k, v in module.__dict__.items() if type(v) in accepted]
    temp.sort()

    for k, v in temp:
        hierarchial_write(v, directory)
    write_hierarchial_index(temp, directory)
    write_alphabetical_index(temp, directory)
    copy_files(directory)
    
    print 'Finished exporting!'


#
# For the alphabetical index
#
def write_alphabetical_index(items, directory):
    f = file(directory + '/index_a.html', 'w')

    write_header(f)
    alpha_dict = {}
    for x in ascii_lowercase:
        alpha_dict[x] = False
        
    for k, v in items:
        alpha_dict[ k[0].lower() ] = True
        
    alpha_list = alpha_dict.keys()
    alpha_list.sort()

    f.write('<div style="text-align: center;">')
    for k in alpha_list:
        if alpha_dict[k]:
            f.write('<a href="#%s">%s</a> ' % (k, k))
        else:
            f.write(k + ' ')
    f.write('</div><hr /><br />')

    lastletter = ''
    for k, v in items:
        if k[0].lower() != lastletter:
            lastletter = k[0].lower()
            f.write('<a name="%s" />' % lastletter)
        f.write('<a href="%s.%s.html">%s</a><br />' % (v.__module__, k, k))
    
    write_footer(f)

#
# For the hierarchial index
#
def write_hierarchial_index(items, directory):
    f = file(directory + '/index_h.html', 'w')

    write_header(f)
    f.write('<ul>')
    for k, v in items:
        klass = v
        if isinstance(klass, InstanceType):
            klass = klass.__class__
        hindex_recursive(f, klass)
    f.write('</ul>')
    write_footer(f)
    
def hindex_recursive(f, obj):
    
    f.write('<li><a href="%s.%s.html">%s</a></li>' % (obj.__module__, obj.__name__, obj.__name__))
    for cls in obj.__bases__:
        klass = cls
        if isinstance(klass, InstanceType):
            klass = klass.__class__
        f.write('<ul>')
        if klass is not object:
            hindex_recursive(f, klass)
        f.write('</ul>')
            
#
# Helper function for BuildClassHierarchyDict
#
def hierarchial_write(obj, directory):   
    if isinstance(obj, InstanceType):
        obj = obj.__class__

    bases = []
    name = str(obj.__name__)
    doc = str(obj.__doc__)
    sep = ', '

    for cls in obj.__bases__:
        if cls is not object:
            hierarchial_write(cls, directory)
            bases.append('%s.%s' % (cls.__module__, cls.__name__))
            
    f = file( '%s/%s.%s.html' % (directory, obj.__module__, name), 'w' )
    items = [ (x, x) for x in obj.__dict__ if x[0] != '_' ] + \
            [ (name_mapping[x][0], x) for x in obj.__dict__ if x.startswith('__') and \
                                                               x in name_mapping ]
    items.sort()

    write_header(f)
    write_main_item(f, '%s.%s' % (obj.__module__, name), doc, items, bases)
    for x in items:
        if x[1] in name_mapping:
            write_sub_item(f, x[0], name_mapping[ x[1] ][1], x[1])
        else:
            item = getattr(obj, x[1])
            if type(item) is MethodType:
                name = x[0] + '(' + sep.join(item.func_code.co_varnames) + ')'
                write_sub_item(f, name, item.__doc__, x[1])
            else:
                write_sub_item(f, x[0], item.__doc__, x[1])
    write_footer(f)

