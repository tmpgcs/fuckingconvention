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
  'Long'    : 'l',
  'uShort'  : 's',
  'unsigned int'  : 'ui',
}

class Defect(object):
  def __init__(self, msg, location):
    super(Defect, self).__init__()
    self.msg = msg
    self.location = location

Defects = []

def check_variable_naming(node):
  if node.location.file != None and node.location.file.name != file_name:
    return

  if node.kind == cindex.CursorKind.VAR_DECL:
    DEBUG('--var: %s %s' % (node.spelling, node.type.spelling))
    # check single character variable
    if len(node.spelling) == 1:
      Defects.append(Defect(
        '%s: should not use single character variable' % (node.spelling),
        node.location
      ))

    # check underscore
    if '_' in node.spelling:
      d = Defect('%s: variable name should not contain underscore' % node.spelling, node.location)
      Defects.append(d)

    # check type prefix
    if node.type.spelling in TYPE_PREFIX_MAP:
      prefix = TYPE_PREFIX_MAP[node.type.spelling]
      if node.spelling.startswith(prefix) == False:
        Defects.append(Defect(
          '%s: variable of type %s should begin with %s' % (node.spelling, node.type.spelling, prefix),
          node.location
        ))
      elif len(node.spelling) > len(prefix):
        if node.spelling[len(prefix)].islower():
          Defects.append(Defect(
            '%s: first character following type prefix %s should be capitalized' % (node.spelling, prefix),
            node.location
          ))
    else:
      WARN('%s: unknown prefix for type %s' % (node.spelling, node.type.spelling))

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