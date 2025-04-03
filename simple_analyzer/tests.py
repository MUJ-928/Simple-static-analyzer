import unittest
import ast
from analyzer import StaticAnalyzer, VariableAnalyzer, ImportAnalyzer


# 测试主分析器接口
class TestStaticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = StaticAnalyzer()

    def test_syntax_error(self):
        code = "x = "
        result = self.analyzer.analyze(code)
        self.assertTrue(len(result["syntax_errors"]) > 0)
        self.assertEqual(result["syntax_errors"][0]["message"][:11], "invalid syntax")

    def test_unused_variable(self):
        code = """x = 10\ny = 20\nprint(x)"""
        result = self.analyzer.analyze(code)
        self.assertEqual(len(result["unused_vars"]), 1)
        self.assertEqual(result["unused_vars"][0]["name"], "y")

    def test_unused_import(self):
        code = """import os\nimport sys\nprint(sys.path)"""
        result = self.analyzer.analyze(code)
        self.assertEqual(len(result["unused_imports"]), 1)
        self.assertEqual(result["unused_imports"][0]["name"], "os")

    def test_star_import(self):
        code = """from math import *\nprint(pi)"""
        result = self.analyzer.analyze(code)
        self.assertEqual(len(result["star_imports"]), 1)
        self.assertEqual(result["star_imports"][0]["module"], "math")

    def test_nested_scopes(self):
        code = """def outer():\n    x = 10\n    def inner():\n        y = 20\n    return x"""
        result = self.analyzer.analyze(code)
        self.assertEqual(len(result["unused_vars"]), 1)
        self.assertEqual(result["unused_vars"][0]["name"], "y")

    def test_attribute_access(self):
        code = """import os.path\nprint(os.path.join)"""
        result = self.analyzer.analyze(code)
        self.assertEqual(len(result["unused_imports"]), 0)


# 测试变量分析模块
class TestVariableAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = VariableAnalyzer()

    def test_variable_tracking(self):
        code = "x = 10\ny = x + 5"
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        unused = self.analyzer.get_unused_vars()
        self.assertEqual(len(unused), 0)

    def test_function_scope(self):
        code = """def test():\n    x = 10\n    return x\ny = 20"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        unused = self.analyzer.get_unused_vars()
        self.assertEqual(len(unused), 1)
        self.assertEqual(unused["y"], 4)


# 测试导入分析模块
class TestImportAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ImportAnalyzer()

    def test_import_usage(self):
        code = """import os\nprint(os.name)"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        unused = self.analyzer.get_unused_imports()
        self.assertEqual(len(unused), 0)

    def test_from_import(self):
        code = """from sys import path, version\nprint(path)"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        unused = self.analyzer.get_unused_imports()
        self.assertEqual(len(unused), 1)
        self.assertEqual(next(iter(unused))[0], "sys.version")

    def test_nested_imports(self):
        code = """import os.path\nfrom os.path import join\nprint(join('/a', 'b'))"""
        tree = ast.parse(code)
        self.analyzer.visit(tree)
        unused = self.analyzer.get_unused_imports()
        self.assertEqual(len(unused), 1)
        self.assertEqual(next(iter(unused))[0], "os.path")


# 测试完整集成场景
class TestIntegration(unittest.TestCase):
    def test_full_analysis(self):
        code = """
import os
import sys
from math import *

x = 10
y = 20
print(x)

def test():
    z = 30
    return z
"""
        analyzer = StaticAnalyzer()
        result = analyzer.analyze(code)

        self.assertEqual(len(result["unused_vars"]), 1)
        self.assertEqual(result["unused_vars"][0]["name"], "y")

        self.assertEqual(len(result["unused_imports"]), 2)
        import_names = {imp["name"] for imp in result["unused_imports"]}
        self.assertTrue("os" in import_names)
        self.assertTrue("sys" in import_names)

        self.assertEqual(len(result["star_imports"]), 1)
        self.assertEqual(result["star_imports"][0]["module"], "math")


if __name__ == "__main__":
    unittest.main()