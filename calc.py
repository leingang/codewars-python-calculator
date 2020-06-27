#!/usr/bin/env python

import logging
import re

from utils import config_logger, add_logger
logger = logging.getLogger(__name__)
config_logger(logger)

class Token(object):
    """A token"""
    name = None
    value = None

    def __init__(self,name,value):

        self.name = name
        self.value = value

    def __str__(self):
        return "{cls}({name},{value})".format(cls=self.__class__.__name__,
                                            name= self.name,
                                            value=repr(self.value))
                                        

class TokenizerException(Exception): pass


class Lexer(object):
    """A lexical analyzer"""
    
    lexemes = None

    def __init__(self,specs):
        """Constructor

        *specs* is a list of tuples `(name,re)`
        """
        self.lexemes = specs

    def tokenize(self,text):
        """Tokenize *text*.  Yields a sequence of :class:`Token`s."""
        token_re = "|".join('(?P<%s>%s)' % pair for pair in self.lexemes)
        # See https://stackoverflow.com/a/2359619/297797
        # and https://docs.python.org/3.2/library/re.html#writing-a-tokenizer
        regex = re.compile(token_re)
        pos = 0
        while True:
            m = regex.match(text, pos)
            if not m: break
            pos = m.end()
            tokname = m.lastgroup
            tokvalue = m.group(tokname)
            yield Token(tokname, tokvalue)
        if pos != len(text):
            raise TokenizerException('tokenizer stopped at pos %r of %r' % (
                pos, len(text)))        


# Parsing
# =======

# The abstract syntax tree
# ------------------------

class AbstractSyntaxTree(object): 
    """Base type of an AST node"""
    
    def __str__(self):
        """String representation (mainly for introspection)"""
        return self.__class__.__name__


class Number(AbstractSyntaxTree):
    """AST node for a number."""

    def __init__(self,token):
        self.token = token
        self.value = int(token.value)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__,self.value)


class BinOp(AbstractSyntaxTree):
    """AST node for a binary operator"""

    def __init__(self,left,op,right):
        self.left = left
        self.token = self.op = op
        self.right = right
    
    def __str__(self):
        return "{cls}({name},left={left},right={right})"\
            .format(cls=self.__class__.__name__,
                name=self.op.name,
                left=self.left,
                right=self.right)


class UnaryOp(AbstractSyntaxTree):
    """AST node for a unary operator"""

    def __init__(self,op,expr):
        self.token = self.op = op
        self.expr = expr

    def __str__(self):
        return "{cls}({name},expr={expr})"\
            .format(cls=self.__class__.__name__,
                name=self.op.name,
                expr=self.expr)



# The parser object
# -----------------
class Parser(object):
    """Processor of a calculator token list to an abstract syntax tree"""

    lexer = None
    current_token = None
    tokens = None

    def __init__(self):
        self.lexer = Lexer([
            ('INTEGER',   r'[0-9]+'),
            ('PLUS',      r'\+'),
            ('MINUS',     r'-'),
            ('WHITESPACE',r'\s+'),
            ('LPAREN',    r'\('),
            ('RPAREN',    r'\)'),
            ('MUL',       r'\*'),
            ('DIV',       r'/')
        ])

    def parse(self,text):
        self.tokens = self.lexer.tokenize(text)
        self.current_token = next(self.tokens)
        return self.parse_expr()

    @add_logger
    def eat(self,token_type):
        """Eat a :class:`Token` of type *token_type*.

        Raise an error if the current token is not of type *token_type*.
        """
        if self.current_token.name == token_type:
            logger.debug("eating {}".format(token_type))
            try:
                self.current_token = next(self.tokens)
            except StopIteration:
                self.current_token = Token('EOF',None)
            logger.debug("self.current_token: {}".format(self.current_token))
        else:
            raise SyntaxError("Expected token of type '{}' but found '{}'"\
                                .format(token_type,self.current_token.name))

    def eat_whitespace(self):
        """Eat whitespace."""
        while (self.current_token.name == 'WHITESPACE'):
            self.eat('WHITESPACE')

    @add_logger
    def parse_expr(self):
        """Parse an expression.

        Rules:

            expr: term WHITESPACE* (addop term)*
            addop: (PLUS|MINUS) WHITESPACE*
            term: factor WHITESPACE* (multop factor)*
            multop: (MUL|DIV) WHITESPACE*
            factor: MINUS factor | INTEGER | LPAREN WHITESPACE* expr WHITESPACE* RPAREN WHITESPACE*

        Returns: :class:`AbstractSyntaxTree`
        """
        logger.debug("begin")
        node = self.parse_term()
        self.eat_whitespace()
        while (self.match_addop()):
            node = self.parse_binop(left=node,right_callback=self.parse_term)
        logger.debug("node: {}".format(node))
        return node

    @add_logger
    def parse_term(self):
        """Parse a term."""
        logger.debug("begin")
        node = self.parse_factor()
        self.eat_whitespace()
        while self.match_multop():
            node = self.parse_binop(left=node,right_callback=self.parse_factor)
        return node

    @add_logger
    def match_addop(self):
        """Check if the token matches an addop"""
        logger.debug("result: {}".format(self.current_token.name in ('PLUS','MINUS')))
        return self.current_token.name in ('PLUS','MINUS')

    @add_logger
    def parse_binop(self,left=None,right_callback=None):
        """Parse a binary operator."""
        logger.debug("begin")
        op = self.current_token
        self.eat(self.current_token.name)
        self.eat_whitespace()
        if right_callback is None:
            right_callback = lambda : None
        node = BinOp(op=op,left=left,right=right_callback())
        logger.debug("node: {}".format(node))
        return node

    @add_logger
    def match_multop(self):
        """Check if the token matches a multop"""
        logger.debug("result: {}".format(self.current_token.name in ('MUL','DIV')))
        return self.current_token.name in ('MUL','DIV')

    @add_logger
    def parse_factor(self):
        """Parse a factor.
        
        Rule:

            factor: MINUS factor | INTEGER | LPAREN WHITESPACE* expr WHITESPACE* RPAREN WHITESPACE*
        
        """
        logger.debug("begin")
        token = self.current_token
        if token.name == 'INTEGER':
            self.eat('INTEGER') # advances self.current_token but we saved token
            node = Number(token)
        elif token.name == 'MINUS':
            self.eat('MINUS')
            node = UnaryOp(token,self.parse_factor())
            # Whitespace *cannot* follow a unary - !
        elif token.name == 'LPAREN':
            self.eat('LPAREN')
            self.eat_whitespace()
            node = self.parse_expr()
            self.eat_whitespace()
            self.eat('RPAREN')
        else:
            raise SyntaxError("Unrecognized token: {}".format(token))
        self.eat_whitespace()
        logger.debug("node: {}".format(node))
        return node


# Evaluating
# ==========

class NodeVistor(object):
    """Visitor that recurses down a tree."""

    def visit(self,node):
        """Visit *node*.
        
        For each node class *cls* in the tree, looks for a method 
        :code:`visit_*cls*`.  If the method does not exist, calls
        :code:`generic_visit`.
        """
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self,method_name,'generic_visit')
        return visitor(node)

    def generic_visit(node):
        raise NotImplementedError


class Evaluator(NodeVistor):
    """Evaluator of an AST."""

    def __init__(self,parser=None):
        if parser is None:
            self.parser = Parser()
    
    def visit_BinOp(self,node):
        operators = {
            'PLUS' : lambda x,y: x+y,
            'MINUS' : lambda x,y: x-y,
            'MUL' : lambda x,y: x*y,
            'DIV' : lambda x,y: x/y
        }
        f = operators[node.op.name]
        return f(self.visit(node.left),self.visit(node.right))

    def visit_Number(self,node):
        return node.value

    def visit_UnaryOp(self,node):
        return - self.visit(node.expr)

    def evaluate(self,text):
        tree = self.parser.parse(text)
        return self.visit(tree)

    



def calc(text):
    """Calculate the expression in *text*"""
    evaluator = Evaluator()
    return evaluator.evaluate(text)


if __name__ == '__main__':
    import codewars_test as Test

    logger.setLevel(logging.DEBUG)
    logging.getLogger('__main__.Parser').setLevel(logging.WARNING)

    tests = [
        ["1 + 1", 2],
        ["8/16", 0.5],
        ["2 + 3 + 4", 9],
        ["2 * 7 + 3", 17],
        ["3 -(-1)", 4],
        ["2 + -2", 0],
        ["10- 2- -5", 13],
        ["(2 + 7) * 3", 27],
        ["(((10)))", 10],
        ["3 * 5", 15],
        ["-7 * -(6 / 3)", 14]
    ]

    parser = Parser()
    for text, val in tests:
        logger.debug('string: {}'.format(text))
        result = calc(text)
        print(result)
        

    # for test in tests:
    #     Test.assert_equals(calc(test[0]), test[1])