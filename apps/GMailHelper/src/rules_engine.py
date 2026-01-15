"""
规则引擎模块

负责解析规则配置、匹配邮件、执行白名单检查
"""

import re
import yaml
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class MatchCondition:
    """匹配条件"""
    sender_domains: List[str]
    subject_keywords: List[str]
    body_keywords: List[str]


@dataclass
class Action:
    """处理动作"""
    type: str  # add_label, archive, mark_read, delete
    value: Optional[str] = None  # 对于add_label，这是标签名称


@dataclass
class Rule:
    """处理规则"""
    name: str
    priority: int
    enabled: bool
    matchers: MatchCondition
    actions: List[Action]
    apply_to_unmatched: bool = False


class RulesEngine:
    """规则引擎"""

    def __init__(self, config_path: str):
        """
        初始化规则引擎

        Args:
            config_path: 规则配置文件路径
        """
        self.config = self._load_config(config_path)
        self.rules = self._parse_rules(self.config)
        self.whitelist = self._parse_whitelist(self.config)

    def _load_config(self, config_path: str) -> Dict:
        """加载YAML配置文件"""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _parse_whitelist(self, config: Dict) -> Dict:
        """解析白名单配置"""
        return config.get("whitelist", {})

    def _parse_rules(self, config: Dict) -> List[Rule]:
        """解析规则配置"""
        rules = []

        rule_configs = config.get("rules", [])

        for rule_config in rule_configs:
            if not rule_config.get("enabled", True):
                continue

            matchers = rule_config.get("matchers", {})
            actions = rule_config.get("actions", [])

            rule = Rule(
                name=rule_config["name"],
                priority=rule_config.get("priority", 50),
                enabled=rule_config.get("enabled", True),
                matchers=MatchCondition(
                    sender_domains=matchers.get("sender_domains", []),
                    subject_keywords=matchers.get("subject_keywords", []),
                    body_keywords=matchers.get("body_keywords", [])
                ),
                actions=[
                    Action(
                        type=action.get("type"),
                        value=action.get("value")
                    ) for action in actions
                ],
                apply_to_unmatched=rule_config.get("apply_to_unmatched", False)
            )

            rules.append(rule)

        # 按优先级排序（数字越小优先级越高）
        return sorted(rules, key=lambda r: r.priority)

    def is_whitelisted(self, email: Dict) -> bool:
        """
        检查邮件是否在白名单中

        Args:
            email: 邮件对象

        Returns:
            是否在白名单
        """
        # 提取发件人
        sender = email.get("from", "")
        subject = email.get("subject", "")
        labels = [label.get("name", "") for label in email.get("labelIds", [])]

        # 检查发件人白名单
        whitelist_senders = self.whitelist.get("senders", [])
        for pattern in whitelist_senders:
            if self._match_sender(sender, pattern):
                return True

        # 检查主题白名单
        whitelist_subjects = self.whitelist.get("subjects", [])
        for keyword in whitelist_subjects:
            if keyword.lower() in subject.lower():
                return True

        # 检查标签白名单
        whitelist_labels = self.whitelist.get("labels", [])
        for label in labels:
            if label in whitelist_labels:
                return True

        return False

    def _match_sender(self, sender: str, pattern: str) -> bool:
        """
        匹配发件人

        支持通配符：
        - "*.com" 匹配任何.com域名
        - "noreply@*" 匹配任何noreply@开头的邮箱

        Args:
            sender: 发件人邮箱
            pattern: 匹配模式

        Returns:
            是否匹配
        """
        # 提取邮箱地址（可能包含名称，如 "John Doe <john@example.com>"）
        email_match = re.search(r'<(.+?)>|([^\s<>]+@[^\s<>]+)', sender)
        if not email_match:
            return False

        sender_email = email_match.group(1) or email_match.group(2)

        # 转换通配符为正则表达式
        # * -> .*
        # . -> \.
        pattern_regex = pattern.replace(".", r"\.").replace("*", ".*")
        pattern_regex = f"^{pattern_regex}$"

        return bool(re.match(pattern_regex, sender_email, re.IGNORECASE))

    def match_rule(self, email: Dict) -> Optional[Rule]:
        """
        匹配邮件到规则

        Args:
            email: 邮件对象

        Returns:
            匹配的规则，如果没有匹配则返回None
        """
        sender = email.get("from", "")
        subject = email.get("subject", "")
        snippet = email.get("snippet", "")  # 邮件摘要

        for rule in self.rules:
            # 跳过"仅对未匹配邮件"的规则（这些规则在最后处理）
            if rule.apply_to_unmatched:
                continue

            # 检查发件人域名
            if rule.matchers.sender_domains:
                matched_sender = False
                for domain in rule.matchers.sender_domains:
                    if self._match_sender(sender, f"*@{domain}"):
                        matched_sender = True
                        break

                if not matched_sender:
                    continue  # 发件人不匹配，尝试下一个规则

            # 检查主题关键词
            if rule.matchers.subject_keywords:
                matched_subject = False
                for keyword in rule.matchers.subject_keywords:
                    if keyword.lower() in subject.lower():
                        matched_subject = True
                        break

                if not matched_subject:
                    # 如果配置了主题关键词但不匹配，继续尝试下一个规则
                    if rule.matchers.sender_domains:
                        # 如果发件人已匹配，但主题不匹配，不算完全匹配
                        pass
                    else:
                        continue

            # 检查正文关键词（可选）
            if rule.matchers.body_keywords:
                matched_body = False
                for keyword in rule.matchers.body_keywords:
                    if keyword.lower() in snippet.lower():
                        matched_body = True
                        break

                if not matched_body:
                    continue

            # 所有条件都匹配，返回该规则
            return rule

        return None

    def get_ai_fallback_rule(self) -> Optional[Rule]:
        """
        获取AI分类兜底规则

        Returns:
            AI分类规则，如果未启用则返回None
        """
        for rule in self.rules:
            if rule.apply_to_unmatched:
                return rule

        return None

    def get_config(self) -> Dict:
        """
        获取原始配置

        Returns:
            完整配置字典
        """
        return self.config
