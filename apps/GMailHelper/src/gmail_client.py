"""
Gmail MCP 客户端封装

通过JSON-RPC over stdio与Gmail MCP服务器通信
"""

import json
import subprocess
from typing import List, Dict, Optional
from pathlib import Path


class GmailMCPClient:
    """Gmail MCP 客户端，封装MCP工具调用"""

    def __init__(self):
        """初始化Gmail MCP客户端"""
        # 检查Gmail MCP认证
        credentials_path = Path.home() / ".gmail-mcp" / "credentials.json"
        if not credentials_path.exists():
            raise RuntimeError(
                "Gmail MCP 未认证。请运行: npx @gongrzhe/server-gmail-autoauth-mcp auth"
            )

    def _call_mcp_tool(self, tool_name: str, **kwargs) -> Dict:
        """
        调用MCP工具（通过JSON-RPC over stdio）

        Args:
            tool_name: MCP工具名称（如 'search_emails'）
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        # 构造JSON-RPC请求
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs
            }
        }

        try:
            # 启动MCP服务器
            process = subprocess.Popen(
                ["npx", "@gongrzhe/server-gmail-autoauth-mcp@1.1.11"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 发送请求
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(input=request_json, timeout=60)

            # 解析响应（MCP返回的是JSON-RPC格式）
            for line in stdout.split('\n'):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            return response["result"]
                        elif "error" in response:
                            error = response["error"]
                            raise RuntimeError(
                                f"MCP工具错误: {error.get('message', error)}"
                            )
                    except json.JSONDecodeError:
                        continue

            # 如果没有找到有效响应
            raise RuntimeError(f"MCP工具未返回有效响应")

        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"MCP工具调用超时: {tool_name}")
        except Exception as e:
            raise RuntimeError(f"MCP工具调用失败: {e}")

    def _parse_email_content(self, content_list: List[Dict]) -> List[Dict]:
        """
        解析MCP工具返回的邮件content

        MCP返回格式：
        {
          "content": [{
            "type": "text",
            "text": "ID: xxx\nSubject: xxx\nFrom: xxx\nDate: xxx\n\nID: ..."
          }]
        }

        Args:
            content_list: MCP返回的content数组

        Returns:
            解析后的邮件列表
        """
        emails = []

        for item in content_list:
            if item.get("type") == "text":
                text = item.get("text", "")

                # 解析文本格式的邮件列表
                # 每封邮件由空行分隔，字段格式为 "Key: Value"
                current_email = {}

                for line in text.split('\n'):
                    line = line.strip()

                    if not line:
                        # 空行表示一封邮件结束
                        if current_email:
                            emails.append(current_email)
                            current_email = {}
                        continue

                    # 解析字段（格式: "Key: Value"）
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        key = key.lower()  # 统一小写

                        if key == 'id':
                            current_email['id'] = value
                        elif key == 'subject':
                            current_email['subject'] = value
                        elif key == 'from':
                            current_email['from'] = value
                        elif key == 'date':
                            current_email['date'] = value
                        elif key == 'snippet':
                            current_email['snippet'] = value

                # 添加最后一封邮件
                if current_email:
                    emails.append(current_email)

        return emails

    def search_emails(
        self,
        query: str,
        max_results: int = 100
    ) -> List[Dict]:
        """
        搜索邮件

        Args:
            query: Gmail搜索查询（如 "is:unread in:inbox"）
            max_results: 最大结果数

        Returns:
            邮件列表，每个元素包含 id, from, subject, snippet等字段
        """
        result = self._call_mcp_tool(
            "search_emails",
            query=query,
            maxResults=max_results
        )

        # MCP工具返回格式: {"content": [{type": "text", "text": "..."}]}
        content = result.get("content", [])

        return self._parse_email_content(content)

    def get_email(self, message_id: str) -> Dict:
        """
        获取邮件详情

        Args:
            message_id: 邮件ID

        Returns:
            邮件详细信息
        """
        result = self._call_mcp_tool("read_email", messageId=message_id)
        content = result.get("content", [])

        emails = self._parse_email_content(content)

        return emails[0] if emails else {}

    def modify_email(
        self,
        message_id: str,
        add_label_ids: Optional[List[str]] = None,
        remove_label_ids: Optional[List[str]] = None
    ):
        """
        修改单封邮件

        Args:
            message_id: 邮件ID
            add_label_ids: 要添加的标签ID列表
            remove_label_ids: 要移除的标签ID列表
        """
        params = {"messageId": message_id}

        if add_label_ids:
            params["addLabelIds"] = add_label_ids

        if remove_label_ids:
            params["removeLabelIds"] = remove_label_ids

        return self._call_mcp_tool("modify_email", **params)

    def batch_modify_emails(
        self,
        message_ids: List[str],
        add_label_ids: Optional[List[str]] = None,
        remove_label_ids: Optional[List[str]] = None
    ):
        """
        批量修改邮件

        Args:
            message_ids: 邮件ID列表
            add_label_ids: 要添加的标签ID列表
            remove_label_ids: 要移除的标签ID列表
        """
        params = {"messageIds": message_ids}

        if add_label_ids:
            params["addLabelIds"] = add_label_ids

        if remove_label_ids:
            params["removeLabelIds"] = remove_label_ids

        return self._call_mcp_tool("batch_modify_emails", **params)

    def delete_email(self, message_id: str):
        """
        删除邮件

        Args:
            message_id: 邮件ID
        """
        return self._call_mcp_tool("delete_email", messageId=message_id)

    def batch_delete_emails(self, message_ids: List[str], batch_size: int = 50):
        """
        批量删除邮件

        Args:
            message_ids: 邮件ID列表
            batch_size: 批次大小
        """
        return self._call_mcp_tool(
            "batch_delete_emails",
            messageIds=message_ids,
            batchSize=batch_size
        )

    def list_labels(self) -> List[Dict]:
        """
        获取所有标签

        Returns:
            标签列表
        """
        result = self._call_mcp_tool("list_email_labels")
        content = result.get("content", [])

        labels = self._parse_email_content(content)

        return labels if isinstance(labels, list) else []

    def create_label(
        self,
        name: str,
        label_list_visibility: str = "labelShow",
        message_list_visibility: str = "show"
    ) -> Dict:
        """
        创建标签

        Args:
            name: 标签名称
            label_list_visibility: 标签列表可见性
            message_list_visibility: 消息列表可见性

        Returns:
            创建的标签信息
        """
        result = self._call_mcp_tool(
            "create_label",
            name=name,
            labelListVisibility=label_list_visibility,
            messageListVisibility=message_list_visibility
        )

        content = result.get("content", [])
        labels = self._parse_email_content(content)

        return labels[0] if labels else {}

    def get_or_create_label(self, name: str) -> str:
        """
        获取或创建标签

        Args:
            name: 标签名称

        Returns:
            标签ID
        """
        # 先查找是否已存在
        labels = self.list_labels()

        for label in labels:
            if label.get("name") == name:
                return label["id"]

        # 不存在则创建
        result = self.create_label(name)
        return result.get("id", "")
