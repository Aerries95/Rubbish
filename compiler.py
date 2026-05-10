import re
import random as _py_random

# ==========================================
# 1. 词法分析器 (Lexer)
# ==========================================
class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

def lex(code):
    rules = [
        ('COMMENT', r'//.*'),             # 注释 //
        ('STRING', r'"[^"]*"'),           # 字符串 (支持长文本)
        ('FLOAT_LIT', r'\d+\.\d+'),       # 浮点数
        ('INT_LIT', r'\d+'),              # 整数
        ('DEF', r'\bdef\b'),              # def 关键字
        ('PRINT', r'\bprint\b'),          # print 关键字
        ('INPUT', r'\binput\b'),          # input 关键字
        ('FOR', r'\bfor\b'),              # for 关键字
        ('WHILE', r'\bwhile\b'),          # while 关键字
        ('IF', r'\bif\b'),                # if 关键字
        ('ELIF', r'\belif\b'),            # elif 关键字
        ('ELSE', r'\belse\b'),            # else 关键字
        ('RETURN', r'\breturn\b'),        # return 关键字
        ('BREAK', r'\bbreak\b'),          # break 关键字
        ('CONTINUE', r'\bcontinue\b'),    # continue 关键字
        ('TYPE', r'\b(int|str|bool|float)\b'), # 类型
        ('ID', r'[a-zA-Z_]\w*'),          # 标识符
        ('DOT', r'\.'),                   # 访问符 .
        ('EQEQ', r'=='),                  # 等于
        ('LESS', r'<'),                   # 小于
        ('GREATER', r'>'),                # 大于
        ('PLUS', r'\+'),                  # 加号
        ('MINUS', r'-'),                  # 减号
        ('EQ', r'='),                     # 赋值
        ('COMMA', r','),                  # 逗号
        ('LBRACKET', r'\['),             # [
        ('RBRACKET', r'\]'),             # ]
        ('LPAREN', r'\('),                # (
        ('RPAREN', r'\)'),                # )
        ('LBRACE', r'\{'),                # {
        ('RBRACE', r'\}'),                # }
        ('NEWLINE', r'\n'),               # 换行
        ('SKIP', r'[ \t\r]+'),            # 空格和制表符
    ]

    tokens = []
    line_num = 1
    
    # 词法扫描
    while code:
        match = None
        for name, pattern in rules:
            regex = re.compile(pattern)
            match = regex.match(code)
            if match:
                val = match.group(0)
                if name != 'SKIP' and name != 'COMMENT':
                    tokens.append(Token(name, val, line_num))
                if name == 'NEWLINE':
                    line_num += 1
                code = code[len(val):]
                break
        if not match:
            raise SyntaxError(f"词法错误: 无法解析的字符 '{code[0]}' 在第 {line_num} 行")
    
    # 过滤多余的换行符
    filtered = []
    for t in tokens:
        if t.type == 'NEWLINE':
            if len(filtered) > 0 and filtered[-1].type != 'NEWLINE':
                filtered.append(t)
        else:
            filtered.append(t)
    return filtered

# ==========================================
# 2. 抽象语法树 (AST)
# ==========================================
class ASTNode:
    def __init__(self, lineno=None):
        self.lineno = lineno

class Program(ASTNode):
    def __init__(self, functions, lineno=None):
        super().__init__(lineno)
        self.functions = functions

class FunctionDecl(ASTNode):
    def __init__(self, name, body, return_type=None, params=None, lineno=None):
        super().__init__(lineno)
        self.name = name
        self.body = body
        self.return_type = return_type
        self.params = params or []

class VarDecl(ASTNode):
    def __init__(self, var_type, name, value, lineno=None):
        super().__init__(lineno)
        self.var_type = var_type
        self.name = name
        self.value = value # 可以是一个表达式或常量

class PrintCall(ASTNode):
    def __init__(self, arg, lineno=None):
        super().__init__(lineno)
        self.arg = arg

class StringLiteral(ASTNode):
    def __init__(self, value, lineno=None):
        super().__init__(lineno)
        self.value = value

class Identifier(ASTNode):
    def __init__(self, name, lineno=None):
        super().__init__(lineno)
        self.name = name

class ArrayAccess(ASTNode):
    def __init__(self, name, indices, lineno=None):
        super().__init__(lineno)
        self.name = name
        self.indices = indices

class Call(ASTNode):
    def __init__(self, name, args, lineno=None):
        super().__init__(lineno)
        self.name = name
        self.args = args

class MemberCall(ASTNode):
    def __init__(self, target, name, args, lineno=None):
        super().__init__(lineno)
        self.target = target
        self.name = name
        self.args = args

class IntegerLiteral(ASTNode):
    def __init__(self, value, lineno=None):
        super().__init__(lineno)
        self.value = value

class FloatLiteral(ASTNode):
    def __init__(self, value, lineno=None):
        super().__init__(lineno)
        self.value = value

class ForLoop(ASTNode):
    def __init__(self, loop_count_expr, var_name, body, lineno=None):
        super().__init__(lineno)
        self.loop_count_expr = loop_count_expr
        self.var_name = var_name
        self.body = body

class WhileLoop(ASTNode):
    def __init__(self, condition, body, lineno=None):
        super().__init__(lineno)
        self.condition = condition
        self.body = body

class IfStmt(ASTNode):
    def __init__(self, condition, true_body, elif_branches, false_body, lineno=None):
        super().__init__(lineno)
        self.condition = condition
        self.true_body = true_body
        self.elif_branches = elif_branches # list of (condition, body) tuples
        self.false_body = false_body # list of ASTNode or None

class BinaryOp(ASTNode):
    def __init__(self, left, op, right, lineno=None):
        super().__init__(lineno)
        self.left = left
        self.op = op
        self.right = right

class Assignment(ASTNode):
    def __init__(self, name, expr, lineno=None):
        super().__init__(lineno)
        self.name = name
        self.expr = expr

class ArrayAssignment(ASTNode):
    def __init__(self, name, indices, expr, lineno=None):
        super().__init__(lineno)
        self.name = name
        self.indices = indices
        self.expr = expr

class Return(ASTNode):
    def __init__(self, expr, lineno=None):
        super().__init__(lineno)
        self.expr = expr

class ExprStmt(ASTNode):
    def __init__(self, expr, lineno=None):
        super().__init__(lineno)
        self.expr = expr

class BreakStmt(ASTNode): pass
class ContinueStmt(ASTNode): pass

# ==========================================
# 3. 语法分析器 (Parser) 简单手写递归下降
# ==========================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type):
        curr = self.current()
        if curr and curr.type == expected_type:
            self.pos += 1
            return curr
        raise SyntaxError(f"语法错误: 期待 {expected_type}, 得到 {curr.type if curr else 'EOF'} 在第 {curr.line if curr else '?'} 行")
        
    def match(self, expected_type):
        curr = self.current()
        if curr and curr.type == expected_type:
            self.pos += 1
            return True
        return False

    def skip_newlines(self):
        while self.match('NEWLINE'):
            pass

    def parse(self):
        self.skip_newlines()
        functions = []
        while self.current():
            functions.append(self.parse_function())
            self.skip_newlines()
        return Program(functions)

    def parse_function(self):
        def_tok = self.consume('DEF')
        # optional return type: def int a(){...}
        return_type = None
        if self.current() and self.current().type == 'TYPE':
            return_type = self.consume('TYPE').value
        name_tok = self.consume('ID')
        name = name_tok.value
        self.consume('LPAREN')
        params = []
        if not self.match('RPAREN'):
            # parse first param
            if self.current().type == 'TYPE':
                ptype = self.consume('TYPE').value
                pname = self.consume('ID').value
                params.append((ptype, pname))
            else:
                raise SyntaxError("语法错误: 函数参数需要类型和名称")
            while self.match('COMMA'):
                if self.current().type == 'TYPE':
                    ptype = self.consume('TYPE').value
                    pname = self.consume('ID').value
                    params.append((ptype, pname))
                else:
                    raise SyntaxError("语法错误: 函数参数需要类型和名称")
            # consume closing RPAREN for non-empty param list
            self.consume('RPAREN')
        
        self.consume('LBRACE')
        self.skip_newlines()
        
        body = self.parse_block()
        return FunctionDecl(name, body, return_type, params, lineno=def_tok.line)

    def parse_block(self):
        body = []
        while True:
            if self.current() is None:
                raise SyntaxError("语法错误: 遇到文件结尾，缺少 '}'")
            if self.match('RBRACE'):
                break
            if self.current().type == 'TYPE':
                body.append(self.parse_var_decl())
            elif self.current().type == 'PRINT':
                body.append(self.parse_print())
            elif self.current().type == 'FOR':
                body.append(self.parse_for())
            elif self.current().type == 'WHILE':
                body.append(self.parse_while())
            elif self.current().type == 'IF':
                body.append(self.parse_if())
            elif self.current().type == 'BREAK':
                self.consume('BREAK')
                body.append(BreakStmt())
            elif self.current().type == 'CONTINUE':
                self.consume('CONTINUE')
                body.append(ContinueStmt())
            elif self.current().type == 'RETURN':
                body.append(self.parse_return())
            elif self.current().type == 'ID':
                # Distinguish between function call / member expression / assignment
                next_tok = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
                if next_tok and next_tok.type in ('LPAREN', 'DOT'):
                    expr = self.parse_expr()
                    body.append(ExprStmt(expr, lineno=getattr(expr, 'lineno', None)))
                else:
                    body.append(self.parse_assignment())
            else:
                raise SyntaxError(f"未知的语句: {self.current()}")
            
            # 允许语句结尾有换行符
            if self.current() and self.current().type == 'NEWLINE':
                self.consume('NEWLINE')
            while self.current() and self.current().type == 'COMMA':
                self.consume('COMMA')
            self.skip_newlines()

        return body

    def parse_return(self):
        ret_tok = self.consume('RETURN')
        # accept return(expr) or return expr
        if self.current() and self.current().type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expr()
            self.consume('RPAREN')
        else:
            expr = self.parse_expr()
        return Return(expr, lineno=ret_tok.line)

    def parse_expr(self):
        # 简单解析表达式 (比如: 10, a, a < 10)
        left = self.parse_single_expr()
        curr = self.current()
        if curr and curr.type in ('LESS', 'GREATER', 'EQEQ', 'PLUS', 'MINUS'):
            op_tok = self.consume(curr.type)
            op = op_tok.value
            right = self.parse_single_expr()
            return BinaryOp(left, op, right, lineno=op_tok.line)
        return left
        
    def parse_single_expr(self):
        curr = self.current()
        if curr.type == 'ID':
            # function call in expression? e.g., len(a)
            next_tok = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
            if next_tok and next_tok.type == 'LPAREN':
                return self.parse_call()
            node = self.parse_target()
            # support member access/chaining like a.max or a.max()
            while self.current() and self.current().type == 'DOT':
                self.consume('DOT')
                member_tok = self.consume('ID')
                member_name = member_tok.value
                member_line = member_tok.line
                args = []
                if self.current() and self.current().type == 'LPAREN':
                    self.consume('LPAREN')
                    if not self.match('RPAREN'):
                        args.append(self.parse_expr())
                        while self.match('COMMA'):
                            args.append(self.parse_expr())
                        self.consume('RPAREN')
                node = MemberCall(node, member_name, args, lineno=member_line)
            return node
        elif curr.type == 'INPUT':
            input_tok = self.consume('INPUT')
            args = []
            if self.current() and self.current().type == 'LPAREN':
                self.consume('LPAREN')
                if not self.match('RPAREN'):
                    args.append(self.parse_expr())
                    while self.match('COMMA'):
                        args.append(self.parse_expr())
                    self.consume('RPAREN')
            return Call('input', args, lineno=input_tok.line)
        elif curr.type == 'INT_LIT':
            tok = self.consume('INT_LIT')
            return IntegerLiteral(int(tok.value), lineno=tok.line)
        elif curr.type == 'FLOAT_LIT':
            tok = self.consume('FLOAT_LIT')
            return FloatLiteral(float(tok.value), lineno=tok.line)
        elif curr.type == 'STRING':
            tok = self.consume('STRING')
            return StringLiteral(tok.value[1:-1], lineno=tok.line)
        else:
            raise SyntaxError(f"语法错误: 期待表达式，得到 {curr.type}")

    def parse_for(self):
        for_tok = self.consume('FOR')
        self.consume('LPAREN')
        count_expr = self.parse_expr()
        self.consume('COMMA')
        var_tok = self.consume('ID')
        var_name = var_tok.value
        self.consume('RPAREN')
        self.consume('LBRACE')
        self.skip_newlines()
        body = self.parse_block()
        return ForLoop(count_expr, var_name, body, lineno=for_tok.line)

    def parse_call(self):
        name_tok = self.consume('ID')
        name = name_tok.value
        call_line = name_tok.line
        self.consume('LPAREN')
        args = []
        if not self.match('RPAREN'):
            args.append(self.parse_expr())
            while self.match('COMMA'):
                args.append(self.parse_expr())
            self.consume('RPAREN')
        return Call(name, args, lineno=call_line)

    def parse_target(self):
        name_tok = self.consume('ID')
        name = name_tok.value
        indices = []
        while self.match('LBRACKET'):
            index_expr = self.parse_expr()
            self.consume('RBRACKET')
            indices.append(index_expr)
        if indices:
            return ArrayAccess(name, indices, lineno=name_tok.line)
        return Identifier(name, lineno=name_tok.line)

    def parse_assignment(self):
        target = self.parse_target()
        self.consume('EQ')
        expr = self.parse_expr()
        if isinstance(target, ArrayAccess):
            return ArrayAssignment(target.name, target.indices, expr, lineno=target.lineno)
        return Assignment(target.name, expr, lineno=target.lineno)

    def parse_while(self):
        while_tok = self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.parse_expr()
        self.consume('RPAREN')
        self.consume('LBRACE')
        self.skip_newlines()
        body = self.parse_block()
        return WhileLoop(condition, body, lineno=while_tok.line)

    def parse_if(self):
        if_tok = self.consume('IF')
        self.consume('LPAREN')
        condition = self.parse_expr()
        self.consume('RPAREN')
        self.consume('LBRACE')
        self.skip_newlines()
        true_body = self.parse_block()
        
        elif_branches = []
        # 注意：使用用户要求的 elif，且判断带有条件的情况
        while self.match('ELIF'):
            self.consume('LPAREN')
            condition_elif = self.parse_expr()
            self.consume('RPAREN')
            self.consume('LBRACE')
            self.skip_newlines()
            body_elif = self.parse_block()
            elif_branches.append((condition_elif, body_elif))
            self.skip_newlines()
            
        false_body = None
        if self.match('ELSE'):
            self.consume('LBRACE')
            self.skip_newlines()
            false_body = self.parse_block()
            
        return IfStmt(condition, true_body, elif_branches, false_body, lineno=if_tok.line)

    def parse_var_decl(self):
        type_tok = self.consume('TYPE')
        var_type = type_tok.value
        name_tok = self.consume('ID')
        name = name_tok.value
        dimensions = []
        while self.match('LBRACKET'):
            dim_expr = self.parse_expr()
            self.consume('RBRACKET')
            dimensions.append(dim_expr)

        # 支持数组声明后直接带初始化器: int a[3] = {1,2,3}
        if dimensions:
            init = None
            if self.current() and self.current().type == 'EQ':
                self.consume('EQ')
                init = self.parse_initializer()
            return VarDecl(var_type, (name, dimensions), init, lineno=type_tok.line)

        self.consume('EQ')

        curr = self.current()
        if curr.type == 'STRING':
            tok = self.consume('STRING')
            val = StringLiteral(tok.value[1:-1], lineno=tok.line) # 去掉引号
        elif curr.type == 'FLOAT_LIT':
            tok = self.consume('FLOAT_LIT')
            val = FloatLiteral(float(tok.value), lineno=tok.line)
        elif curr.type == 'INT_LIT':
            tok = self.consume('INT_LIT')
            val = IntegerLiteral(int(tok.value), lineno=tok.line)
        else:
            val = self.parse_expr()
            
        return VarDecl(var_type, name, val, lineno=type_tok.line)

    def parse_initializer(self):
        # parse nested initializer lists like {1,2,3} or {{1,2},{3,4}}
        self.consume('LBRACE')
        items = []
        while True:
            if self.current().type == 'LBRACE':
                items.append(self.parse_initializer())
            else:
                items.append(self.parse_expr())
            if self.match('COMMA'):
                continue
            break
        self.consume('RBRACE')
        return items

    def parse_print(self):
        print_tok = self.consume('PRINT')
        self.consume('LPAREN')
        arg = self.parse_expr()
        self.consume('RPAREN')
        return PrintCall(arg, lineno=print_tok.line)


# ==========================================
# 4. 解释器 (直接像 Python 一样运行)
# ==========================================
class BreakException(Exception): pass
class ContinueException(Exception): pass
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self, ast_root):
        self.ast_root = ast_root
        self.env = {} # 存储变量的内存环境

    def default_value_for_type(self, var_type):
        if var_type == 'int':
            return 0
        if var_type == 'float':
            return 0.0
        if var_type == 'bool':
            return False
        return ""

    def build_array(self, var_type, dimensions):
        size = dimensions[0]
        if len(dimensions) == 1:
            return [self.default_value_for_type(var_type) for _ in range(size)]
        return [self.build_array(var_type, dimensions[1:]) for _ in range(size)]

    def resolve_indices(self, array_value, indices, create_missing=False):
        current = array_value
        for index_expr in indices[:-1]:
            index = self.eval_expr(index_expr)
            if not isinstance(index, int):
                lineno = getattr(index_expr, 'lineno', None)
                msg = "数组下标必须是整数"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)
            if index < 1 or index > len(current):
                lineno = getattr(index_expr, 'lineno', None)
                msg = "数组下标越界"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)
            current = current[index - 1]
        last_index = self.eval_expr(indices[-1])
        if not isinstance(last_index, int):
            lineno = getattr(indices[-1], 'lineno', None)
            msg = "数组下标必须是整数"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        if last_index < 1 or last_index > len(current):
            lineno = getattr(indices[-1], 'lineno', None)
            msg = "数组下标越界"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        return current, last_index - 1

    def format_value(self, value):
        if isinstance(value, list):
            return "{" + ",".join(self.format_value(item) for item in value) + "}"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def eval_expr(self, expr):
        if isinstance(expr, IntegerLiteral):
            return expr.value
        elif isinstance(expr, FloatLiteral):
            return expr.value
        elif isinstance(expr, StringLiteral):
            return expr.value
        elif isinstance(expr, Identifier):
            if expr.name in self.env:
                return self.env[expr.name]
            lineno = getattr(expr, 'lineno', None)
            msg = f"变量 '{expr.name}' 未定义"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        elif isinstance(expr, ArrayAccess):
            if expr.name not in self.env:
                lineno = getattr(expr, 'lineno', None)
                msg = f"变量 '{expr.name}' 未定义"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)
            current = self.env[expr.name]
            for index_expr in expr.indices:
                index = self.eval_expr(index_expr)
                if not isinstance(index, int):
                    lineno = getattr(index_expr, 'lineno', None)
                    msg = "数组下标必须是整数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                if index < 1 or index > len(current):
                    lineno = getattr(index_expr, 'lineno', None)
                    msg = "数组下标越界"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                current = current[index - 1]
            return current
        elif isinstance(expr, Call):
            # built-in input([prompt]) -> int if numeric else string
            if expr.name == 'input':
                if len(expr.args) > 1:
                    lineno = getattr(expr, 'lineno', None)
                    msg = "input() 最多接受 1 个参数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                prompt = ""
                if len(expr.args) == 1:
                    prompt_val = self.eval_expr(expr.args[0])
                    prompt = str(prompt_val)
                raw = input(prompt)
                # 与当前语言用法对齐：如果像整数就转成 int，否则保留字符串
                if re.fullmatch(r"-?\d+", raw or ""):
                    return int(raw)
                return raw
            # built-in len
            if expr.name == 'len':
                if len(expr.args) != 1:
                    lineno = getattr(expr, 'lineno', None)
                    msg = "len() 需要 1 个参数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                val = self.eval_expr(expr.args[0])
                if not isinstance(val, list):
                    lineno = getattr(expr, 'lineno', None)
                    msg = "len() 参数必须是数组"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                return len(val)
            # built-in random(a,b) -> integer between a and b (inclusive)
            if expr.name == 'random':
                if len(expr.args) != 2:
                    lineno = getattr(expr, 'lineno', None)
                    msg = "random() 需要 2 个参数: random(a,b)"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                a = self.eval_expr(expr.args[0])
                b = self.eval_expr(expr.args[1])
                if not isinstance(a, int) or not isinstance(b, int):
                    lineno = getattr(expr, 'lineno', None)
                    msg = "random() 参数必须是整数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                # Python's randint is inclusive
                return _py_random.randint(a, b)
            # calling user function as expression: evaluate args and call
            for func in self.ast_root.functions:
                if func.name == expr.name:
                    arg_vals = [self.eval_expr(a) for a in expr.args]
                    return self.execute_function(func, arg_vals)
            lineno = getattr(expr, 'lineno', None)
            msg = f"函数 '{expr.name}' 未定义"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        elif isinstance(expr, MemberCall):
            # member functions on arrays, like a.max() or a.max
            target_val = self.eval_expr(expr.target)
            lineno = getattr(expr, 'lineno', None)
            if not isinstance(target_val, list):
                msg = "成员方法只能用于数组"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)

            # flatten nested arrays
            def flatten(lst):
                for item in lst:
                    if isinstance(item, list):
                        yield from flatten(item)
                    else:
                        yield item

            flat = list(flatten(target_val))
            if len(flat) == 0:
                msg = "数组为空，无法计算 max/min"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)

            if expr.name == 'max':
                if len(expr.args) != 0:
                    msg = "max() 不接受参数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                # ensure numeric elements (int/float), but exclude bool
                for v in flat:
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        msg = "max() 仅支持数值数组(int/float)"
                        if lineno:
                            msg += f" 在第 {lineno} 行"
                        raise RuntimeError(msg)
                return max(flat)
            if expr.name == 'min':
                if len(expr.args) != 0:
                    msg = "min() 不接受参数"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                for v in flat:
                    if isinstance(v, bool) or not isinstance(v, (int, float)):
                        msg = "min() 仅支持数值数组(int/float)"
                        if lineno:
                            msg += f" 在第 {lineno} 行"
                        raise RuntimeError(msg)
                return min(flat)
            msg = f"未知的成员方法 '{expr.name}'"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        elif isinstance(expr, BinaryOp):
            left = self.eval_expr(expr.left)
            right = self.eval_expr(expr.right)
            if expr.op == '<': return left < right
            if expr.op == '>': return left > right
            if expr.op == '==': return left == right
            try:
                if expr.op == '+': return left + right
                if expr.op == '-': return left - right
            except TypeError:
                lineno = getattr(expr, 'lineno', None)
                msg = f"类型错误: 无法对操作数执行 '{expr.op}'"
                if lineno:
                    msg += f" 在第 {lineno} 行"
                raise RuntimeError(msg)
            lineno = getattr(expr, 'lineno', None)
            msg = f"未知的操作符 '{expr.op}'"
            if lineno:
                msg += f" 在第 {lineno} 行"
            raise RuntimeError(msg)
        lineno = getattr(expr, 'lineno', None)
        msg = "未知的表达式"
        if lineno:
            msg += f" 在第 {lineno} 行"
        raise RuntimeError(msg)

    def run(self):
        # 寻找 main 函数作为入口
        main_func = None
        for func in self.ast_root.functions:
            if func.name == "main":
                main_func = func
                break
        
        if not main_func:
            raise RuntimeError("运行错误: 找不到入口程序 'main' 函数")
            
        self.execute_block(main_func.body)

    def execute_function(self, func, arg_values=None):
        # create local scope
        saved_env = self.env
        self.env = {}
        # bind parameters
        if arg_values is None:
            arg_values = []
        for i, p in enumerate(getattr(func, 'params', [])):
            ptype, pname = p
            if i < len(arg_values):
                self.env[pname] = arg_values[i]
            else:
                self.env[pname] = self.default_value_for_type(ptype)
        try:
            try:
                self.execute_block(func.body)
            except ReturnException as r:
                return r.value
        finally:
            self.env = saved_env
        return None

    def execute_block(self, body):
        for stmt in body:
            if isinstance(stmt, VarDecl):
                # 数组声明：name 里存 (变量名, 维度表达式列表)
                if isinstance(stmt.name, tuple):
                        name, dimensions = stmt.name
                        dims = [self.eval_expr(dim) for dim in dimensions]
                        arr = self.build_array(stmt.var_type, dims)
                        # apply initializer if present
                        if stmt.value is not None:
                            def fill(arr_ref, init):
                                for i, v in enumerate(init):
                                    if isinstance(v, list):
                                        fill(arr_ref[i], v)
                                    else:
                                        # v is an expression AST node
                                        arr_ref[i] = self.eval_expr(v)
                            fill(arr, stmt.value)
                        self.env[name] = arr
                else:
                    # 将变量存入环境
                    self.env[stmt.name] = self.eval_expr(stmt.value)
            elif isinstance(stmt, Assignment):
                # 更新已存在的变量
                self.env[stmt.name] = self.eval_expr(stmt.expr)
            elif isinstance(stmt, ArrayAssignment):
                if stmt.name not in self.env:
                    lineno = getattr(stmt, 'lineno', None)
                    msg = f"变量 '{stmt.name}' 未定义"
                    if lineno:
                        msg += f" 在第 {lineno} 行"
                    raise RuntimeError(msg)
                target_array = self.env[stmt.name]
                parent, offset = self.resolve_indices(target_array, stmt.indices)
                parent[offset] = self.eval_expr(stmt.expr)
            elif isinstance(stmt, Call):
                # call a user-defined function (no return value expected)
                called = False
                for func in self.ast_root.functions:
                    if func.name == stmt.name:
                        # allow return value but ignore it here
                        try:
                            val = self.execute_function(func)
                        except ReturnException as r:
                            val = r.value
                        called = True
                        break
                if not called:
                    # allow calling built-in like len as statement (no-op)
                    if stmt.name in ('len', 'random'):
                        self.eval_expr(stmt)
                    else:
                        lineno = getattr(stmt, 'lineno', None)
                        msg = f"函数 '{stmt.name}' 未定义"
                        if lineno:
                            msg += f" 在第 {lineno} 行"
                        raise RuntimeError(msg)
            elif isinstance(stmt, MemberCall):
                # evaluate member call when used as statement and ignore result
                try:
                    _ = self.eval_expr(stmt)
                except ReturnException as r:
                    _ = r.value
            elif isinstance(stmt, PrintCall):
                # 支持打印变量或直接打印字符串字面量
                val = self.eval_expr(stmt.arg)
                if isinstance(val, list):
                    print(self.format_value(val))
                else:
                    print(val)
            elif isinstance(stmt, ForLoop):
                count = self.eval_expr(stmt.loop_count_expr)
                for i in range(1, count + 1):
                    self.env[stmt.var_name] = i
                    try:
                        self.execute_block(stmt.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(stmt, WhileLoop):
                while self.eval_expr(stmt.condition):
                    try:
                        self.execute_block(stmt.body)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            elif isinstance(stmt, IfStmt):
                if self.eval_expr(stmt.condition):
                    self.execute_block(stmt.true_body)
                else:
                    matched_elif = False
                    for elif_cond, elif_body in stmt.elif_branches:
                        if self.eval_expr(elif_cond):
                            self.execute_block(elif_body)
                            matched_elif = True
                            break
                    if not matched_elif and stmt.false_body is not None:
                        self.execute_block(stmt.false_body)
            elif isinstance(stmt, BreakStmt):
                raise BreakException()
            elif isinstance(stmt, ContinueStmt):
                raise ContinueException()
            elif isinstance(stmt, Return):
                val = self.eval_expr(stmt.expr)
                raise ReturnException(val)
            elif isinstance(stmt, ExprStmt):
                # expression statement: evaluate for side effects and ignore result
                self.eval_expr(stmt.expr)

# ==========================================
# 5. LLVM IR 生成 (纯文本生成)
# ==========================================
def generate_llvm_ir(ast_root):
    # 这里我们直接用纯写文本的方式生成合法的 LLVM IR 代码
    # 这样完全不需要安装 llvmlite 模块，也能生成真正的底层代码！
    
    global_strings = []
    functions_ir = []
    str_counter = 0
    ptr_counter = 1

    for func_node in ast_root.functions:
        func_ir = f"define i32 @{func_node.name}() {{\nentry:\n"
        variables = {} # 记录变量名对应的全局字符串名称和长度
        
        for stmt in func_node.body:
            if isinstance(stmt, VarDecl):
                if isinstance(stmt.name, tuple):
                    # 数组目前只在解释器层运行，这里先跳过，避免旧 IR 生成器崩溃
                    continue
                str_val = stmt.value.value
                # 计算 UTF-8 编码的长度 + 1 (用于 \00 结尾)
                str_len = len(str_val.encode('utf-8')) + 1
                str_name = f"@.str.{str_counter}"
                str_counter += 1
                
                # 添加全局字符串常量定义
                global_strings.append(f"{str_name} = private unnamed_addr constant [{str_len} x i8] c\"{str_val}\\00\"")
                variables[stmt.name] = (str_name, str_len)
                
            elif isinstance(stmt, PrintCall):
                if isinstance(stmt.arg, Identifier):
                    str_name, str_len = variables[stmt.arg.name]
                elif isinstance(stmt.arg, StringLiteral):
                    # 如果是直接打印字符串字面量，临时生成一个全局字符常量
                    str_val = stmt.arg.value
                    str_len = len(str_val.encode('utf-8')) + 1
                    str_name = f"@.str.{str_counter}"
                    str_counter += 1
                    global_strings.append(f"{str_name} = private unnamed_addr constant [{str_len} x i8] c\"{str_val}\\00\"")
                else:
                    continue
                    
                # 使用 LLVM 的 getelementptr 指令获取字符串的首地址指针
                func_ir += f"  %ptr_{ptr_counter} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {str_name}, i64 0, i64 0\n"
                # 调用 printf
                func_ir += f"  call i32 (i8*, ...) @printf(i8* %ptr_{ptr_counter})\n"
                ptr_counter += 1
                
        func_ir += "  ret i32 0\n}"
        functions_ir.append(func_ir)

    # 组装完整的 LLVM IR 文件
    ir_code = ""
    # 1. 系统函数声明
    ir_code += "declare i32 @printf(i8*, ...)\n\n"
    # 2. 全局常量声明
    for gs in global_strings:
        ir_code += gs + "\n"
    ir_code += "\n"
    # 3. 函数体
    ir_code += "\n\n".join(functions_ir)
    
    print(ir_code)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python compiler.py <源代码文件>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        tokens = lex(source_code)
        parser = Parser(tokens)
        ast = parser.parse()

        # 解释器直接执行并在前台只输出代码结果
        interpreter = Interpreter(ast)
        interpreter.run()
    except SyntaxError as e:
        # 只显示语法错误信息（不显示 Python traceback）
        print("语法错误：", e)
        sys.exit(1)
    except RuntimeError as e:
        # 运行时错误，例如越界、未定义变量、类型错误等
        print("运行错误：", e)
        sys.exit(1)
    except Exception as e:
        # 未预期的内部错误，给出简短信息并退出（不泄露完整 traceback）
        print("内部错误：", str(e))
        sys.exit(1)
    
    # 偷偷在后台生成底层 LLVM IR (保存为 output.ll)
    # import sys
    # original_stdout = sys.stdout
    # with open("output.ll", "w", encoding="utf-8") as f:
    #     sys.stdout = f
    #     generate_llvm_ir(ast)
    # sys.stdout = original_stdout
