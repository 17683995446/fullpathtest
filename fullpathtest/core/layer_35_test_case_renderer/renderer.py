"""
第35层：用例模板渲染层

根据目标语言、测试框架、路径信息、测试数据，渲染生成可直接编译/运行的标准化测试用例代码。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from fullpathtest.types.core import TaskContext, ConfigSnapshot, Path, LanguageType
from fullpathtest.core.layer_34_llm_enhanced_data.generator import EnhancedTestDataSet


@dataclass
class TestCaseCode:
    """可执行单测用例代码"""
    code_id: str
    path_id: str
    language: LanguageType
    framework: str
    code_content: str
    file_name: str
    is_async: bool = False


class TestCaseRenderer:
    """用例模板渲染器"""
    
    FRAMEWORKS = {
        'python': ['pytest', 'unittest'],
        'java': ['junit5', 'testng'],
        'javascript': ['jest', 'mocha'],
        'typescript': ['jest', 'vitest'],
        'golang': ['testing'],
        'rust': ['built-in']
    }
    
    def __init__(self):
        self.generated_cases: Dict[str, TestCaseCode] = {}
    
    def render_test_cases(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        enhanced_data_sets: Dict[str, EnhancedTestDataSet],
        paths: List[Path],
        language: LanguageType
    ) -> Dict[str, TestCaseCode]:
        """渲染测试用例代码"""
        cases = {}
        
        for path in paths:
            enhanced_data = enhanced_data_sets.get(path.path_id)
            if not enhanced_data:
                continue
            
            framework = self._select_framework(language)
            code = self._render_case(path, enhanced_data, language, framework)
            
            cases[path.path_id] = code
            self.generated_cases[path.path_id] = code
        
        return cases
    
    def _select_framework(self, language: LanguageType) -> str:
        """选择测试框架"""
        lang_name = language.name.lower()
        frameworks = self.FRAMEWORKS.get(lang_name, ['default'])
        return frameworks[0]
    
    def _render_case(
        self,
        path: Path,
        enhanced_data: EnhancedTestDataSet,
        language: LanguageType,
        framework: str
    ) -> TestCaseCode:
        """渲染单条用例"""
        lang_name = language.name.lower()
        
        if lang_name == 'python':
            code = self._render_pytest_case(path, enhanced_data)
            file_name = f"test_{path.path_id.lower()}.py"
        elif lang_name == 'java':
            code = self._render_junit_case(path, enhanced_data)
            file_name = f"{path.path_id.capitalize()}Test.java"
        elif lang_name in ['javascript', 'typescript']:
            code = self._render_jest_case(path, enhanced_data, lang_name)
            extension = 'ts' if lang_name == 'typescript' else 'js'
            file_name = f"{path.path_id.lower()}.test.{extension}"
        else:
            code = self._render_generic_case(path, enhanced_data)
            file_name = f"test_{path.path_id.lower()}.txt"
        
        return TestCaseCode(
            code_id=f"CODE-{path.path_id}",
            path_id=path.path_id,
            language=language,
            framework=framework,
            code_content=code,
            file_name=file_name
        )
    
    def _render_pytest_case(self, path: Path, data: EnhancedTestDataSet) -> str:
        """渲染pytest用例"""
        lines = []
        
        lines.append(f"import pytest")
        lines.append("")
        lines.append(f"class Test{path.path_id.replace('-', '_')}:")
        lines.append("")
        
        test_data = data.basic_data.normal_data
        for i, item in enumerate(test_data):
            lines.append(f"    def test_case_{i}(self):")
            lines.append(f"        \"\"\"测试用例: {item.data_id}\"\"\"")
            lines.append("        # 准备")
            lines.append(f"        input_data = {repr(item.value)}")
            lines.append("")
            lines.append("        # 执行")
            lines.append("        result = None  # TODO: 调用被测试函数")
            lines.append("")
            lines.append("        # 断言")
            lines.append("        assert result is not None")
            lines.append("")
        
        lines.append("")
        lines.append("@pytest.mark.parametrize(\"test_input\", [")
        for item in data.basic_data.boundary_data:
            lines.append(f"    {repr(item.value)},  # {item.data_id}")
        lines.append("])")
        lines.append("def test_boundary_cases(test_input):")
        lines.append("    \"\"\"测试边界值用例\"\"\"")
        lines.append("    pass  # TODO: 实现测试")
        lines.append("")
        
        return "\n".join(lines)
    
    def _render_junit_case(self, path: Path, data: EnhancedTestDataSet) -> str:
        """渲染JUnit用例"""
        lines = []
        
        class_name = f"{path.path_id.replace('-', '')}Test"
        
        lines.append("import org.junit.jupiter.api.*;")
        lines.append("import static org.junit.jupiter.api.Assertions.*;")
        lines.append("")
        lines.append(f"class {class_name} {{")
        lines.append("")
        
        for i, item in enumerate(data.basic_data.normal_data):
            lines.append(f"    @Test")
            lines.append(f"    void testCase{i}() {{")
            lines.append(f"        // 准备")
            lines.append(f"        var input = {self._format_java_value(item.value)};")
            lines.append("")
            lines.append("        // 执行")
            lines.append("        // var result = testSubject.method(input);")
            lines.append("")
            lines.append("        // 断言")
            lines.append("        // assertNotNull(result);")
            lines.append("    }")
            lines.append("")
        
        lines.append("}")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_java_value(self, value: Any) -> str:
        """格式化Java值"""
        if value is None:
            return "null"
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)
    
    def _render_jest_case(self, path: Path, data: EnhancedTestDataSet, lang: str) -> str:
        """渲染Jest用例"""
        lines = []
        
        describe_name = path.path_id.replace('-', ' ')
        
        lines.append(f"describe('{describe_name}', () => {{")
        lines.append("")
        
        for i, item in enumerate(data.basic_data.normal_data):
            lines.append(f"  it('test case {i}', () => {{")
            lines.append(f"    // 准备")
            lines.append(f"    const input = {JSON.stringify(item.value, indent=2)};")
            lines.append("")
            lines.append("    // 执行")
            lines.append("    // const result = testSubject(input);")
            lines.append("")
            lines.append("    // 断言")
            lines.append("    // expect(result).toBeDefined();")
            lines.append("  });")
            lines.append("")
        
        lines.append("});")
        lines.append("")
        
        return "\n".join(lines)
    
    def _render_generic_case(self, path: Path, data: EnhancedTestDataSet) -> str:
        """渲染通用用例"""
        lines = []
        
        lines.append(f"# Test Case: {path.path_id}")
        lines.append("=" * 60)
        lines.append("")
        
        for i, item in enumerate(data.basic_data.normal_data):
            lines.append(f"## Test {i}")
            lines.append(f"Data: {item.value}")
            lines.append("Expected: ...")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_case_for_path(self, path_id: str) -> Optional[TestCaseCode]:
        """获取指定路径的测试用例代码"""
        return self.generated_cases.get(path_id)
