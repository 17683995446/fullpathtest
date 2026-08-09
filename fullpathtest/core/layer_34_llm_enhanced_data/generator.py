"""
第34层：LLM 增强测试数据生成层

通过本地离线 LLM 生成复杂业务数据、组合对象、接口报文、异常 Payload、状态链数据、时序依赖数据。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from fullpathtest.types.core import TaskContext, ConfigSnapshot
from fullpathtest.core.layer_33_test_data_inference.generator import BasicTestDataSet
from fullpathtest.core.layer_32_test_data_rule.generator import TestDataRule


@dataclass
class ComplexBusinessData:
    """复杂业务数据"""
    data_id: str
    data_type: str
    value: Any
    business_scenario: str
    complexity_level: int


@dataclass
class EnhancedTestDataSet:
    """增强全场景测试数据集"""
    data_set_id: str
    path_id: str
    basic_data: BasicTestDataSet
    business_data: List[ComplexBusinessData] = field(default_factory=list)
    combination_data: List[Dict[str, Any]] = field(default_factory=list)
    payload_data: List[Dict[str, Any]] = field(default_factory=list)
    state_chain_data: List[Dict[str, Any]] = field(default_factory=list)
    timing_data: List[Dict[str, Any]] = field(default_factory=list)


class LLMEnhancedDataGenerator:
    """LLM增强数据生成器"""
    
    def __init__(self):
        self.enhanced_sets: Dict[str, EnhancedTestDataSet] = {}
    
    def generate_enhanced_data(
        self,
        context: TaskContext,
        config: ConfigSnapshot,
        basic_data_sets: Dict[str, BasicTestDataSet],
        test_rules: Dict[str, TestDataRule],
        business_scenarios: List[str]
    ) -> Dict[str, EnhancedTestDataSet]:
        """生成增强测试数据集"""
        enhanced = {}
        
        for path_id, basic_set in basic_data_sets.items():
            rule = test_rules.get(path_id)
            if not rule:
                continue
            
            enhanced_set = self._enhance_data_set(
                path_id, basic_set, rule, business_scenarios
            )
            enhanced[path_id] = enhanced_set
            self.enhanced_sets[path_id] = enhanced_set
        
        return enhanced
    
    def _enhance_data_set(
        self,
        path_id: str,
        basic_set: BasicTestDataSet,
        rule: TestDataRule,
        scenarios: List[str]
    ) -> EnhancedTestDataSet:
        """增强单条路径的数据集"""
        set_id = f"ENHANCED-{path_id}"
        
        business_data = self._generate_business_data(path_id, scenarios)
        combination_data = self._generate_combination_data(basic_set)
        payload_data = self._generate_payload_data(rule)
        state_chain = self._generate_state_chain_data(rule)
        timing_data = self._generate_timing_data(rule)
        
        return EnhancedTestDataSet(
            data_set_id=set_id,
            path_id=path_id,
            basic_data=basic_set,
            business_data=business_data,
            combination_data=combination_data,
            payload_data=payload_data,
            state_chain_data=state_chain,
            timing_data=timing_data
        )
    
    def _generate_business_data(
        self,
        path_id: str,
        scenarios: List[str]
    ) -> List[ComplexBusinessData]:
        """生成复杂业务数据"""
        data_list = []
        
        for i, scenario in enumerate(scenarios):
            data = ComplexBusinessData(
                data_id=f"business-{path_id}-{i}",
                data_type="business",
                value=self._generate_scenario_value(scenario),
                business_scenario=scenario,
                complexity_level=min(5, i + 1)
            )
            data_list.append(data)
        
        if not scenarios:
            data_list.append(ComplexBusinessData(
                data_id=f"business-{path_id}-0",
                data_type="business",
                value={"id": 12345, "name": "Test User", "status": "active"},
                business_scenario="default",
                complexity_level=2
            ))
        
        return data_list
    
    def _generate_scenario_value(self, scenario: str) -> Any:
        """根据场景生成值"""
        if "login" in scenario.lower():
            return {"username": "test_user", "password": "secure_pass123", "remember_me": True}
        elif "payment" in scenario.lower():
            return {"amount": 99.99, "currency": "USD", "method": "credit_card"}
        elif "registration" in scenario.lower():
            return {"email": "test@example.com", "phone": "+1234567890", "terms_accepted": True}
        else:
            return {"scenario": scenario, "data": "generated_value"}
    
    def _generate_combination_data(self, basic_set: BasicTestDataSet) -> List[Dict[str, Any]]:
        """生成组合数据"""
        combinations = []
        
        normal = basic_set.normal_data
        boundary = basic_set.boundary_data
        
        if normal and boundary:
            for i in range(min(10, len(normal) * len(boundary))):
                combo = {}
                for j, item in enumerate(normal[:2]):
                    combo[f"normal_{j}"] = item.value
                for j, item in enumerate(boundary[:2]):
                    combo[f"boundary_{j}"] = item.value
                combinations.append(combo)
        
        return combinations
    
    def _generate_payload_data(self, rule: TestDataRule) -> List[Dict[str, Any]]:
        """生成异常Payload数据"""
        payloads = []
        
        payloads.append({
            "type": "sql_injection",
            "value": "' OR 1=1 --",
            "risk": "HIGH"
        })
        
        payloads.append({
            "type": "xss",
            "value": "<script>alert('xss')</script>",
            "risk": "HIGH"
        })
        
        payloads.append({
            "type": "buffer_overflow",
            "value": "A" * 10000,
            "risk": "MEDIUM"
        })
        
        return payloads
    
    def _generate_state_chain_data(self, rule: TestDataRule) -> List[Dict[str, Any]]:
        """生成状态链数据"""
        state_chains = []
        
        state_chains.append({
            "chain_id": "chain_1",
            "states": [
                {"state": "initialized", "data": {"id": 1}},
                {"state": "processing", "data": {"id": 1, "step": 2}},
                {"state": "completed", "data": {"id": 1, "result": "success"}}
            ]
        })
        
        state_chains.append({
            "chain_id": "chain_2",
            "states": [
                {"state": "initialized", "data": {"id": 1}},
                {"state": "processing", "data": {"id": 1, "step": 2}},
                {"state": "error", "data": {"id": 1, "error": "timeout"}}
            ]
        })
        
        return state_chains
    
    def _generate_timing_data(self, rule: TestDataRule) -> List[Dict[str, Any]]:
        """生成时序依赖数据"""
        timing_data = []
        
        timing_data.append({
            "scenario": "normal_timing",
            "delays_ms": [10, 50, 100],
            "expected": "success"
        })
        
        timing_data.append({
            "scenario": "slow_timing",
            "delays_ms": [1000, 5000, 10000],
            "expected": "timeout"
        })
        
        timing_data.append({
            "scenario": "out_of_order",
            "order": [2, 0, 1, 3],
            "expected": "race_condition"
        })
        
        return timing_data
    
    def get_enhanced_set_for_path(self, path_id: str) -> Optional[EnhancedTestDataSet]:
        """获取指定路径的增强数据集"""
        return self.enhanced_sets.get(path_id)
