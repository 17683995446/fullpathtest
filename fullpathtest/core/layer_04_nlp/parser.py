"""
第4层：自然语言命令解析层

将用户输入的自然语言测试指令，结构化解析为系统可执行的任务目标。
"""

from typing import Dict, Any, List, Optional
from fullpathtest.types.core import TaskContext, TaskInstruction, CoverageRules
import re


class NLPCommandParser:
    """NLP命令解析器"""
    
    INTENT_PATTERNS = {
        'full_coverage': [
            r'全面测试|完整测试|full.*coverage',
            r'所有.*测试|全部覆盖',
            r'完整覆盖'
        ],
        'critical_path': [
            r'关键路径|critical.*path',
            r'核心功能|主要流程',
            r'重要.*测试'
        ],
        'regression': [
            r'回归测试|regression',
            r'冒烟测试|smoke',
            r'快速测试'
        ],
        'security': [
            r'安全测试|security',
            r'漏洞扫描|vulnerability',
            r'渗透测试'
        ],
        'performance': [
            r'性能测试|performance',
            r'压力测试|stress',
            r'负载测试'
        ],
        'mutation': [
            r'变异测试|mutation',
            r'混沌测试|chaos'
        ]
    }
    
    def __init__(self):
        self.intent_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """编译正则表达式模式"""
        compiled = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            compiled[intent] = [re.compile(p, re.IGNORECASE) for p in patterns]
        return compiled
    
    def parse(self, context: TaskContext) -> TaskInstruction:
        """解析自然语言命令"""
        user_command = context.request.metadata.get('user_command', '')
        
        intent = self._identify_intent(user_command)
        target_modules = self._extract_targets(user_command)
        coverage_req = self._extract_coverage_requirements(user_command, context.request.coverage_rules)
        priority_areas = self._extract_priority_areas(user_command)
        constraints = self._extract_constraints(user_command)
        scenarios = self._identify_scenarios(user_command)
        
        return TaskInstruction(
            task_id=context.task_id,
            intent=intent,
            target_modules=target_modules,
            coverage_requirements=coverage_req,
            priority_areas=priority_areas,
            constraints=constraints,
            business_scenarios=scenarios
        )
    
    def _identify_intent(self, command: str) -> str:
        """识别用户意图"""
        scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern.search(command):
                    score += 1
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return 'general_test'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _extract_targets(self, command: str) -> List[str]:
        """提取目标模块"""
        targets = []
        
        module_patterns = [
            r'模块[:：]\s*([^\s,，]+)',
            r'测试[:：]\s*([^\s,，]+)',
            r'文件[:：]\s*([^\s,，]+)',
            r'类[:：]\s*([^\s,，]+)'
        ]
        
        for pattern in module_patterns:
            matches = re.findall(pattern, command)
            targets.extend(matches)
        
        return list(set(targets))
    
    def _extract_coverage_requirements(
        self, 
        command: str, 
        default_rules: CoverageRules
    ) -> CoverageRules:
        """提取覆盖要求"""
        rules = CoverageRules(
            statement='statement' in command.lower() or '语句' in command,
            branch='branch' in command.lower() or '分支' in command,
            condition='condition' in command.lower() or '条件' in command,
            path='path' in command.lower() or '路径' in command,
            call_chain='call' in command.lower(),
            e2e_flow='e2e' in command.lower() or '端到端' in command
        )
        
        if '100%' in command or '完全' in command:
            rules.statement = True
            rules.branch = True
            rules.condition = True
            rules.path = True
        
        return rules
    
    def _extract_priority_areas(self, command: str) -> List[str]:
        """提取优先级区域"""
        areas = []
        
        priority_keywords = {
            '高优先级': ['核心', '关键', '主要', '登录', '支付', '安全'],
            '中优先级': ['查询', '列表', '配置'],
            '低优先级': ['日志', '统计', '导出']
        }
        
        for priority, keywords in priority_keywords.items():
            for keyword in keywords:
                if keyword in command:
                    areas.append(keyword)
        
        return list(set(areas))
    
    def _extract_constraints(self, command: str) -> Dict[str, Any]:
        """提取约束条件"""
        constraints = {}
        
        timeout_match = re.search(r'超时[:：]\s*(\d+)', command)
        if timeout_match:
            constraints['timeout'] = int(timeout_match.group(1))
        
        max_paths_match = re.search(r'最大路径[:：]\s*(\d+)', command)
        if max_paths_match:
            constraints['max_paths'] = int(max_paths_match.group(1))
        
        parallel_match = re.search(r'并行[:：]\s*(\d+)', command)
        if parallel_match:
            constraints['parallel_degree'] = int(parallel_match.group(1))
        
        return constraints
    
    def _identify_scenarios(self, command: str) -> List[str]:
        """识别业务场景"""
        scenarios = []
        
        scenario_keywords = {
            '正常流程': ['正常', 'happy.*path', '成功'],
            '异常流程': ['异常', 'error', '失败', '边界'],
            '并发场景': ['并发', 'concurrent', 'race'],
            '安全场景': ['安全', '注入', 'xss'],
            '性能场景': ['性能', '压力', '慢']
        }
        
        for scenario, keywords in scenario_keywords.items():
            for keyword in keywords:
                if re.search(keyword, command, re.IGNORECASE):
                    scenarios.append(scenario)
                    break
        
        return scenarios
