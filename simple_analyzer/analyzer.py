import ast
from typing import Dict, List, Union


__version__ = "0.1.0"


# 主控模块 : 作为静态分析器的入口类，负责协调变量分析、导入分析，并生成综合报告
class StaticAnalyzer:
    # 未使用变量、未使用导入、语法错误、星号导入
    def __init__(self):
        self.report = {
            "unused_vars": [],
            "unused_imports": [],
            "syntax_errors": [],
            "star_imports": []
        }

    def analyze(self, code: str) -> Dict[str, List[Dict[str, Union[str, int]]]]:
        try:
            tree = ast.parse(code) # 解析代码为 AST
        except SyntaxError as e:
            self._handle_syntax_error(e)
            return self.report

        self._analyze_variables(tree)
        self._analyze_imports(tree)
        return self.report

    # 处理语法错误，记录错误行号和消息
    def _handle_syntax_error(self, error):
        self.report["syntax_errors"].append({
            "line": error.lineno if hasattr(error, 'lineno') else 0,
            "message": str(error)
        })

    # 调用变量分析器并生成未使用变量报告
    def _analyze_variables(self, tree):
        analyzer = VariableAnalyzer()
        analyzer.visit(tree)
        self.report["unused_vars"] = [
            {"name": var, "line": line}
            for var, line in analyzer.get_unused_vars().items()
        ]

    # 调用导入分析器并生成未使用导入报告
    def _analyze_imports(self, tree):
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        self.report["unused_imports"] = [
            {"name": imp[0], "line": imp[1]}
            for imp in analyzer.get_unused_imports()
        ]
        if analyzer.star_imports:
            self.report["star_imports"] = [
                {"module": mod, "line": 0}
                for mod in analyzer.star_imports
            ]


# 变量分析模块 : 通过遍历 AST 检测代码中定义了但未使用的变量
class VariableAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.used_vars = set()
        self.scopes = [{}]

    # 进入函数时创建新作用域
    def visit_FunctionDef(self, node):
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    # 进入类时创建新作用域
    def visit_ClassDef(self, node):
        self._enter_scope()
        self.generic_visit(node)
        self._exit_scope()

    # 记录赋值语句中的变量及其定义行号, 存储到当前作用域
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.scopes[-1][target.id] = node.lineno
        self.generic_visit(node)

    # 记录被读取的变量（ast.Load 上下文）
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)

    # 比较所有作用域中定义但未使用的变量，返回 {变量名: 行号} 字典
    def get_unused_vars(self):
        return {
            var: lineno
            for scope in self.scopes
            for var, lineno in scope.items()
            if var not in self.used_vars
        }

    # 通过栈结构管理作用域层级
    def _enter_scope(self):
        self.scopes.append({})

    # 通过栈结构管理作用域层级
    def _exit_scope(self):
        self.scopes.pop()


# 导入分析模块 : 检测代码中导入但未使用的模块或符号
class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()
        self.used_names = set()
        self.star_imports = set()

    # 记录普通导入（如 import os）及其行号
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add((alias.name, node.lineno))
        self.generic_visit(node)

    # 处理 from ... import 语句
    # 记录具体导入项（如 from sys import path → 记录 sys.path）
    # 检测星号导入（import *）并标记模块名
    def visit_ImportFrom(self, node):
        module = getattr(node, 'module', '') or ""
        if any(alias.name == '*' for alias in node.names):
            self.star_imports.add(module)

        for alias in node.names:
            if alias.name != '*':
                full_name = f"{module}.{alias.name}" if module else alias.name
                self.imports.add((full_name, node.lineno))
        self.generic_visit(node)

    # 记录直接使用的标识符（如 print(os) 中的 os）
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)

    # 递归解析属性访问链（如 os.path.join → 标记 os 被使用）
    def visit_Attribute(self, node):
        while isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                self.used_names.add(node.value.id)
            node = node.value
        self.generic_visit(node)

    # 返回未使用的导入项集合，格式为 {(导入名, 行号)}
    def get_unused_imports(self) -> set[tuple[str, int]]:
        return {
            (name, lineno)
            for (name, lineno) in self.imports
            if name not in self.used_names
        }


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: analyzer <filename.py>")
        return

    with open(sys.argv[1]) as f:
        code = f.read()

    analyzer = StaticAnalyzer()
    result = analyzer.analyze(code)
    print(result)


if __name__ == "__main__":
    main()
"""
典型输出结构
{
    "unused_vars": [{"name": "x", "line": 5}],
    "unused_imports": [{"name": "os", "line": 3}],
    "syntax_errors": [{"line": 10, "message": "invalid syntax"}],
    "star_imports": [{"module": "numpy", "line": 0}]
}
"""