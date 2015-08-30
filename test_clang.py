#!/usr/bin/python

import sys
import os
from clang import *

file_name = 'test.c'
type_name = 'uLong'

if len(sys.argv) > 1:
  file_name = sys.argv[1]
if len(sys.argv) > 2:
  type_name = sys.argv[2]

file_name = os.path.abspath(file_name)

def DEBUG(msg):
  print '[DEBUG] ' + msg
def WARN(msg):
  print '\033[34m' + '[WARN] ' + msg + '\033[0m'
def ERROR(msg):
  print '\033[91m' + '[ERROR] ' + msg + '\033[0m'

TYPE_PREFIX_MAP = {
  'uLong'   : 'ul',
  'uInt'    : 'ui',
  'uShort'  : 'us',
  'uChar'   : 'uc',
  'unsigned int'    : 'ui',
  'unsigned char'   : 'uc',
  'unsigned short'  : 'us',
  'unsigned long'   : 'ul',
  'int'     : 'i',
  'char'    : 'c',
  'short'   : 's',
  'long'    : 'l',
  'Int'     : 'i',
  'Char'    : 'c',
  'Short'   : 's',
  'Long'    : 'l',
}

class Defect(object):
  def __init__(self, location, msg = ''):
    super(Defect, self).__init__()
    self.msg = msg
    self.location = location

Defects = []

def check_variable_type_prefix(node, *prefixes):
  for prefix in prefixes:
    if node.spelling.startswith(prefix) == True:
      return prefix

  d = Defect(node.location)
  d.msg = '%s: variable of type %s should begin with %s' % (node.spelling, node.type.spelling, ' or '.join(prefixes))
  Defects.append(d)
  return None

def check_variable_naming(node):
  if node.location.file != None and node.location.file.name != file_name:
    return

  if node.kind == cindex.CursorKind.VAR_DECL:
    DEBUG('--var: %s %s' % (node.spelling, node.type.spelling))
    # check single character variable
    if len(node.spelling) == 1:
      Defects.append(Defect(
        node.location,
        '%s: should not use single character variable' % (node.spelling)
      ))

    # check underscore
    if '_' in node.spelling:
      d = Defect(node.location, '%s: variable name should not contain underscore' % node.spelling)
      Defects.append(d)

    # check type prefix
    prefix = None
    type_name = node.type.spelling
    try:
      if node.type.kind == cindex.TypeKind.CONSTANTARRAY:
        type_name = node.type.element_type.spelling
        prefix = check_variable_type_prefix(node, 'p', TYPE_PREFIX_MAP[type_name])
      elif node.type.kind == cindex.TypeKind.POINTER:
        type_name = node.type.get_pointee().spelling
        prefix = check_variable_type_prefix(node, 'p', TYPE_PREFIX_MAP[type_name])
      else:
        prefix = check_variable_type_prefix(node, TYPE_PREFIX_MAP[type_name])
    except KeyError:
      WARN('%s: unknown prefix for type %s %s' % (node.spelling, type_name, node.type.kind))
      if node.type.kind == cindex.TypeKind.TYPEDEF:
        # print node.underlying_typedef_type.kind
        print node.type.get_declaration().underlying_typedef_type.kind
        print node.type.get_declaration().type.kind
        print node.type.get_declaration().kind
        print node.get_definition().kind
        print node.type.get_declaration().underlying_typedef_type.get_declaration().location
        print node.type.get_declaration().underlying_typedef_type.get_declaration().kind
        print node.type.is_pod()
    
    if prefix != None:
      if len(node.spelling) > len(prefix):
        if node.spelling[len(prefix)].islower():
          Defects.append(Defect(
            node.location,
            '%s: first character following type prefix %s should be capitalized' % (node.spelling, prefix)
          ))

  for c in node.get_children():
    check_variable_naming(c)

def find_typerefs(node, typename):
  if node.location.file != None and node.location.file.name != file_name:
    return

  print node.kind

  if node.kind == cindex.CursorKind.VAR_DECL:
    print '--var: %s %s' % (node.spelling, node.type.spelling)

  if node.kind.is_reference():
    print '-- %s [line=%s]' % (node.referenced.spelling, node.location)
    if node.referenced.spelling == typename:
      print 'Found %s [line=%s, col=%s]' % (typename, node.location.line, node.location.column)
  
  # Recurse for children of this node
  for c in node.get_children():
    find_typerefs(c, typename)

cindex.Config.set_library_path('/usr/lib/llvm-3.4/lib/')

# index = cindex.Index.create()
index = cindex.Index(cindex.conf.lib.clang_createIndex(False, True))
tu = index.parse(file_name)
DEBUG('Translation unit:' + tu.spelling)
# find_typerefs(tu.cursor, type_name)
check_variable_naming(tu.cursor)

print '#### CHECK RESULT ####'
for d in Defects:
  ERROR('%s:%s:%s: %s' % (d.location.file.name, d.location.line, d.location.column, d.msg))