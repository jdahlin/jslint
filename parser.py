import commands
import sys

import cjson

PN_NULLARY = 0                     # 0 kids, only pn_atom/pn_dval/etc.
PN_UNARY = 1                       # one kid, plus a couple of scalars
PN_BINARY = 2                      # two kids, plus a couple of scalars
PN_TERNARY = 3                     # three kids
PN_FUNC = 4                        # function definition node
PN_LIST = 5                        # generic singly linked list
PN_NAME = 6                        # name use or definition node
PN_NAMESET = 7                     # JSAtomList + JSParseNode ptr

TOK_ERROR = -1                     # well-known as the only code < EOF
TOK_EOF = 0                        # end of file
TOK_EOL = 1                        # end of line
TOK_SEMI = 2                       # semicolon
TOK_COMMA = 3                      # comma operator
TOK_ASSIGN = 4                     # assignment ops (= += -= etc.)
TOK_HOOK = 5; TOK_COLON = 6        # conditional (?:)
TOK_OR = 7                         # logical or (||)
TOK_AND = 8                        # logical and (&&)
TOK_BITOR = 9                      # bitwise-or (|)
TOK_BITXOR = 10                    # bitwise-xor (^)
TOK_BITAND = 11                    # bitwise-and (&)
TOK_EQOP = 12                      # equality ops (== !=)
TOK_RELOP = 13                     # relational ops (< <= > >=)
TOK_SHOP = 14                      # shift ops (<< >> >>>)
TOK_PLUS = 15                      # plus
TOK_MINUS = 16                     # minus
TOK_STAR = 17; TOK_DIVOP = 18      # multiply/divide ops (* / %)
TOK_UNARYOP = 19                   # unary prefix operator
TOK_INC = 20; TOK_DEC = 21         # increment/decrement (++ --)
TOK_DOT = 22                       # member operator (.)
TOK_LB = 23; TOK_RB = 24           # left and right brackets
TOK_LC = 25; TOK_RC = 26           # left and right curlies (braces)
TOK_LP = 27; TOK_RP = 28           # left and right parentheses
TOK_NAME = 29                      # identifier
TOK_NUMBER = 30                    # numeric constant
TOK_STRING = 31                    # string constant
TOK_REGEXP = 32                    # RegExp constant
TOK_PRIMARY = 33                   # true false null this super
TOK_FUNCTION = 34                  # function keyword
TOK_IF = 35                        # if keyword
TOK_ELSE = 36                      # else keyword
TOK_SWITCH = 37                    # switch keyword
TOK_CASE = 38                      # case keyword
TOK_DEFAULT = 39                   # default keyword
TOK_WHILE = 40                     # while keyword
TOK_DO = 41                        # do keyword
TOK_FOR = 42                       # for keyword
TOK_BREAK = 43                     # break keyword
TOK_CONTINUE = 44                  # continue keyword
TOK_IN = 45                        # in keyword
TOK_VAR = 46                       # var keyword
TOK_WITH = 47                      # with keyword
TOK_RETURN = 48                    # return keyword
TOK_NEW = 49                       # new keyword
TOK_DELETE = 50                    # delete keyword
TOK_DEFSHARP = 51                  # #n= for object/array initializers
TOK_USESHARP = 52                  # #n# for object/array initializers
TOK_TRY = 53                       # try keyword
TOK_CATCH = 54                     # catch keyword
TOK_FINALLY = 55                   # finally keyword
TOK_THROW = 56                     # throw keyword
TOK_INSTANCEOF = 57                # instanceof keyword
TOK_DEBUGGER = 58                  # debugger keyword
TOK_XMLSTAGO = 59                  # XML start tag open (<)
TOK_XMLETAGO = 60                  # XML end tag open (</)
TOK_XMLPTAGC = 61                  # XML point tag close (/>)
TOK_XMLTAGC = 62                   # XML start or end tag close (>)
TOK_XMLNAME = 63                   # XML start-tag non-final fragment
TOK_XMLATTR = 64                   # XML quoted attribute value
TOK_XMLSPACE = 65                  # XML whitespace
TOK_XMLTEXT = 66                   # XML text
TOK_XMLCOMMENT = 67                # XML comment
TOK_XMLCDATA = 68                  # XML CDATA section
TOK_XMLPI = 69                     # XML processing instruction
TOK_AT = 70                        # XML attribute op (@)
TOK_DBLCOLON = 71                  # namespace qualified name op (::)
TOK_ANYNAME = 72                   # XML AnyName singleton (*)
TOK_DBLDOT = 73                    # XML descendant op (..)
TOK_FILTER = 74                    # XML filtering predicate op (.())
TOK_XMLELEM = 75                   # XML element node type (noTOKen)
TOK_XMLLIST = 76                   # XML list node type (noTOKen)
TOK_YIELD = 77                     # yield from generator function
TOK_ARRAYCOMP = 78                 # array comprehension initialiser
TOK_ARRAYPUSH = 79                 # array push within comprehension
TOK_LEXICALSCOPE = 80              # block scope AST node label
TOK_LET = 81                       # let keyword
TOK_SEQ = 82                       # synthetic sequence of statements
TOK_FORHEAD = 83                   # head of for(;;)-style loop
TOK_ARGSBODY = 84                  # formal args in list + body at end
TOK_UPVARS = 85                    # lexical dependencies as JSAtomList
                                   #      of definitions paired with a parse
                                   #      tree full of uses of those names
TOK_RESERVED = 86                  # reserved keywords
TOK_LIMIT = 87                     # domain size


NODE_NAMES = {
    TOK_SEMI: 'SEMI', # 2

    TOK_ASSIGN: 'ASSIGN', # 4
    TOK_HOOK: 'HOOK', # 5
    TOK_COLON: 'COLON', # 6
    TOK_OR: 'OR', # 7
    TOK_AND: 'AND', # 8
    TOK_BITOR: 'BITOR', # 9
    TOK_BITXOR: 'BITXOR', # 9
    TOK_BITAND: 'BITAND', # 11
    TOK_EQOP: 'EQOP', # 12
    TOK_RELOP: 'RELOP', # 13

    TOK_PLUS: 'PLUS', # 15
    TOK_MINUS: 'MINUS', # 16
    TOK_STAR: 'STAR', # 17
    TOK_DIVOP: 'DIVOP', # 18
    TOK_UNARYOP: 'UNARYOP', # 19
    TOK_INC: 'INC', # 20
    TOK_DEC: 'DEC', # 21
    TOK_DOT: 'DOT', # 22
    TOK_LB: 'LB', # 23
    TOK_RB: 'RB', # 24
    TOK_LC: 'LC', # 25
    TOK_RC: 'RC', # 26
    TOK_LP: 'LP', # 27
    TOK_RP: 'RP', # 28
    TOK_NAME: 'NAME', # 29
    TOK_NUMBER: 'NUMBER', # 30
    TOK_STRING: 'STRING', # 31

    TOK_PRIMARY: 'PRIMARY', # 33
    TOK_FUNCTION: 'FUNCTION', # 34
    TOK_IF: 'IF', # 35

    TOK_FOR: 'FOR', # 42
    TOK_BREAK: 'BREAK', # 43

    TOK_IN: 'IN', # 45
    TOK_VAR: 'VAR', # 46

    TOK_RETURN: 'RETURN', # 48
    TOK_NEW: 'NEW', # 49
    TOK_DELETE: 'DELETE', # 50

    TOK_THROW: 'THROW', # 56

    TOK_LEXICALSCOPE: 'LEXICALSCOPE', # 80
    TOK_LET: 'LET', # 81
    TOK_FORHEAD: 'FORHEAD', # 83
    TOK_ARGSBODY: 'ARGSBODY', # 84
    TOK_UPVARS: 'UPVARS', # 85
}


class Node(object):
    def __init__(self, json):
        self.json = json

    def __repr__(self):
        return '<%s>' % (NODE_NAMES.get(self.json['type'], 'unknown').lower(),)


class Error(object):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return '%s: %s' % (self.__class__.desc, self.msg)


class Undefined(Error):
    desc = 'Undefined variable'


class Scope(object):
    def __init__(self):
        self.vars = []


class GlobalScope(object):
    def __init__(self):
        self.vars = ['Date', 'Error', 'eval', 'Math']

        self.vars += ['imports', 'log', 'logError']


class Prototype(object):
    def __init__(self, name):
        self.name = name
        self.vars = []


class Checker(object):
    def __init__(self, filename):
        self._filename = filename
        self._globalScope = GlobalScope()
        self._scopes = [self._globalScope]
        self._prototypes = []
        self._currentPrototype = None

    def _error(self, error, node):
        print '%s:%d:%d: %s' % (self._filename, node['lineno'], node['index'], error)

    def _addPrototype(self, proto):
        self._currentPrototype = proto
        self._prototypes.append(proto)

    def feed(self, node):
        self.parse(node)

    def parse(self, node):
        name = NODE_NAMES.get(node['type'])
        if name is None:
            raise ValueError("%d node is missing in NODE_NAMES" % (
                node['type'],))

        method = getattr(self, name, None)
        if method is not None:
            #print 'call', name
            method(node)
        else:
            self.parseChildren(node)

    def parseChildren(self, node):
        arity = node['arity']
        if arity == PN_LIST:
            for child in node['list']:
                self.parse(child)
        elif arity == PN_NAME:
            if 'expr' in node:
                self.parse(node['expr'])
        elif arity == PN_NAMESET:
            self.parse(node['tree'])
        elif arity == PN_UNARY:
            if 'kid' in node:
                self.parse(node['kid'])
        elif arity == PN_BINARY:
            self.parse(node['left'])
            self.parse(node['right'])
        elif arity == PN_TERNARY:
            self.parse(node['kid1'])
            self.parse(node['kid2'])
            if 'kid3' in node:
                self.parse(node['kid3'])
        elif arity == PN_FUNC:
            self.parse(node['body'])

    LC = RC = LP = RP = LB = RB = SEMI = PLUS = MINUS = STAR = STRING = NUMBER = \
    RETURN = UPVARS = HOOK = RELOP = FOR = FORHEAD = INC = DEC = IF = \
    EQOP = BITAND = COLON = ASSIGN = DOT = PRIMARY = NEW = IN = \
    OR = AND = UNARYOP = DIVOP = LEXICALSCOPE = BITOR = BITXOR = BREAK = parseChildren

    def VAR(self, node):
        # FIXME, let or var
        scope = self._scopes[-1]
        for item in node['list']:
            scope.vars.append(item['atom'])
        self.parseChildren(node)
    LET = VAR

    def NAME(self, node):
        varName = node['atom']
        for scope in reversed(self._scopes):
            if varName in scope.vars:
                break
        else:
            self._error(Undefined(varName), node)
            return
        self.parseChildren(node)

    def FUNCTION(self, node):
        self._scopes[-1].vars.append(node['name'])
        self._scopes.append(Scope())
        self.parseChildren(node)

    def ARGSBODY(self, node):
        scope = self._scopes[-1]
        for item in node['list']:
            if 'atom' in item:
                scope.vars.append(item['atom'])
        self.parseChildren(node)

    def DELETE(self, node):
        scope = self._scopes[-1]
        kid = node['kid']
        if kid['type'] == TOK_NAME:
            scope.vars.remove(kid['atom'])

    def ASSIGN(self, node):
        right = node['right']
        left = node['left']
        if right['type'] == TOK_RC:
            if left.get('atom') == 'prototype':
                self.parse(left)
                self.parsePrototype(right['list'])
                return
        elif left['type'] == TOK_DOT:
            if left['expr']['type'] == TOK_PRIMARY:
                proto = self._currentPrototype
                if proto is not None:
                    proto.vars.append(left['atom'])
        self.parseChildren(node)

    def DOT(self, node):
        nameList = []
        n = node
        while 'expr' in n:
            if 'atom' in n:
                nameList.insert(0, n['atom'])
            n = n['expr']

        if node['atom'] == 'prototype':
            self.protoName = nameList[0]
        self.parseChildren(node)
        if 'expr' in node and node['expr']['type'] == TOK_PRIMARY:
            self.parseThisAccess(node)

    def parsePrototype(self, nodes):
        proto = Prototype(self.protoName)
        self._addPrototype(proto)

        for node in nodes:
            if node['type'] != TOK_COLON:
                self.parse(node)
                continue
            left = node['left']
            right = node['right']
            proto.vars.append(left['atom'])
            self.parse(right)

    def parseThisAccess(self, node):
        name = node['atom']
        proto = self._currentPrototype
        if proto is None:
            return
        if not name in proto.vars:
            self._error(Undefined('this.%s in prototype %s' % (name, proto.name)), node)


def main(argv):
    filename = argv[1]
    data = commands.getoutput("./parser %s" % (filename, ));
    try:
        json = cjson.decode(data)
    except cjson.DecodeError, e:
        try:
            offset = int(str(e).split()[-1])
        except ValueError:
            raise e
        print 'Parse Error:', data[offset-100:offset+100]
        return
    c = Checker(filename)
    #import pprint
    #pprint.pprint(json)
    c.feed(json)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
