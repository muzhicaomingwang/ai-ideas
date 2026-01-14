#!/usr/bin/env python3
"""
Gmail批量清理脚本
功能：批量标记未读邮件为已读并归档
支持：进度保存、断点续传、实时进度显示
使用：原生HTTP请求，无需额外依赖
"""

import os
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# 配置
CREDENTIALS_PATH = os.path.expanduser('~/.gmail-mcp/credentials.json')
PROGRESS_FILE = os.path.expanduser('~/.gmail-cleanup-progress.json')
BATCH_SIZE = 100  # 每批处理100封邮件
GMAIL_API_BASE = 'https://gmail.googleapis.com/gmail/v1/users/me'


class TokenManager:
    """Token管理器，支持自动刷新"""

    def __init__(self):
        self.creds_data = None
        self.access_token = None
        self.load_credentials()

    def load_credentials(self):
        """从凭据文件加载"""
        if not os.path.exists(CREDENTIALS_PATH):
            print(f"❌ 凭据文件不存在: {CREDENTIALS_PATH}")
            return False

        try:
            with open(CREDENTIALS_PATH, 'r') as f:
                self.creds_data = json.load(f)

            self.access_token = self.creds_data.get('access_token')
            return True
        except Exception as e:
            print(f"❌ 加载凭据失败: {e}")
            return False

    def refresh_token(self):
        """刷新access token"""
        if not self.creds_data or 'refresh_token' not in self.creds_data:
            print("❌ 没有refresh_token，无法刷新")
            return False

        print("🔄 Access token已过期，正在刷新...")

        try:
            # 从gcp-oauth.keys.json获取client配置
            oauth_keys_path = os.path.expanduser('~/.gmail-mcp/gcp-oauth.keys.json')
            with open(oauth_keys_path, 'r') as f:
                oauth_keys = json.load(f)

            if 'installed' in oauth_keys:
                client_data = oauth_keys['installed']
            elif 'web' in oauth_keys:
                client_data = oauth_keys['web']
            else:
                print("❌ OAuth配置格式不正确")
                return False

            # 刷新token的请求
            data = urllib.parse.urlencode({
                'client_id': client_data['client_id'],
                'client_secret': client_data['client_secret'],
                'refresh_token': self.creds_data['refresh_token'],
                'grant_type': 'refresh_token'
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://oauth2.googleapis.com/token',
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                new_tokens = json.loads(response.read().decode('utf-8'))

            # 更新access_token
            self.access_token = new_tokens['access_token']
            self.creds_data['access_token'] = new_tokens['access_token']

            if 'expires_in' in new_tokens:
                self.creds_data['expiry_date'] = int(time.time() * 1000) + new_tokens['expires_in'] * 1000

            # 保存更新后的凭据
            with open(CREDENTIALS_PATH, 'w') as f:
                json.dump(self.creds_data, f, indent=2)

            print("✅ Token刷新成功")
            return True

        except Exception as e:
            print(f"❌ Token刷新失败: {e}")
            return False

    def get_token(self):
        """获取有效的access token"""
        return self.access_token


def gmail_api_request(endpoint, access_token, method='GET', data=None):
    """发送Gmail API请求"""
    url = f"{GMAIL_API_BASE}/{endpoint}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    req_data = json.dumps(data).encode('utf-8') if data else None
    request = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"❌ API请求失败 ({e.code}): {error_body}")
        raise
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        raise


def load_progress():
    """加载进度文件"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        'total': 0,
        'processed': 0,
        'processed_ids': [],
        'start_time': datetime.now().isoformat(),
        'last_updated': None
    }


def save_progress(progress):
    """保存进度"""
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def get_unread_emails(token_manager, max_results=None):
    """获取所有未读邮件ID"""
    print("📧 正在获取未读邮件列表...")

    all_message_ids = []
    page_token = None
    retry_count = 0

    try:
        while True:
            endpoint = f"messages?q=is:unread+in:inbox&maxResults=500"
            if page_token:
                endpoint += f"&pageToken={page_token}"

            try:
                results = gmail_api_request(endpoint, token_manager.get_token())
                retry_count = 0  # 成功后重置重试计数

            except urllib.error.HTTPError as e:
                if e.code == 401 and retry_count == 0:
                    # Token过期，刷新后重试
                    if token_manager.refresh_token():
                        retry_count += 1
                        continue
                raise

            messages = results.get('messages', [])
            all_message_ids.extend([msg['id'] for msg in messages])

            print(f"   已获取 {len(all_message_ids)} 封邮件ID...", end='\r')

            page_token = results.get('nextPageToken')
            if not page_token or (max_results and len(all_message_ids) >= max_results):
                break

        print(f"\n✅ 共找到 {len(all_message_ids)} 封未读邮件")
        return all_message_ids

    except Exception as error:
        print(f"❌ 获取邮件列表失败: {error}")
        return []


def batch_mark_read_and_archive(token_manager, message_ids, progress):
    """批量标记已读并归档"""
    total = len(message_ids)
    processed = progress['processed']
    processed_ids = set(progress['processed_ids'])

    # 过滤掉已处理的邮件
    remaining_ids = [mid for mid in message_ids if mid not in processed_ids]

    if not remaining_ids:
        print("✅ 所有邮件已处理完成！")
        return

    print(f"\n开始批量处理 {len(remaining_ids)} 封邮件...")
    print(f"进度恢复: 已处理 {processed}/{total} 封")

    start_time = time.time()

    for i in range(0, len(remaining_ids), BATCH_SIZE):
        batch = remaining_ids[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        retry_count = 0
        while retry_count < 2:
            try:
                # 批量修改：标记为已读 + 归档（移除INBOX标签）
                gmail_api_request(
                    'messages/batchModify',
                    token_manager.get_token(),
                    method='POST',
                    data={
                        'ids': batch,
                        'removeLabelIds': ['INBOX', 'UNREAD']
                    }
                )
                break  # 成功则跳出重试循环

            except urllib.error.HTTPError as e:
                if e.code == 401 and retry_count == 0:
                    # Token过期，刷新后重试
                    if token_manager.refresh_token():
                        retry_count += 1
                        continue
                raise

        # 更新进度
        processed += len(batch)
        processed_ids.update(batch)
        progress['processed'] = processed
        progress['processed_ids'] = list(processed_ids)
        progress['total'] = total
        save_progress(progress)

        # 计算进度
        percentage = (processed / total) * 100
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        eta = (total - processed) / rate if rate > 0 else 0

        print(f"[进度: {percentage:.1f}%] 已处理 {processed}/{total} 封 | "
              f"批次 {batch_num} | 速度: {rate:.1f}封/秒 | "
              f"预计剩余: {eta/60:.1f}分钟")

        # 避免API限速
        time.sleep(0.5)

    total_time = time.time() - start_time
    print(f"\n🎉 批量处理完成！")
    print(f"   总计: {processed} 封邮件")
    print(f"   耗时: {total_time/60:.1f} 分钟")
    print(f"   平均速度: {processed/total_time:.1f} 封/秒")


def verify_inbox_empty(token_manager):
    """验证收件箱是否已清空"""
    print("\n🔍 验证收件箱状态...")

    retry_count = 0
    while retry_count < 2:
        try:
            results = gmail_api_request(
                'messages?q=is:unread+in:inbox&maxResults=1',
                token_manager.get_token()
            )

            remaining = results.get('resultSizeEstimate', 0)

            if remaining == 0:
                print("✅ 收件箱已清空！")
            else:
                print(f"⚠️  收件箱还剩 {remaining} 封未读邮件")

            return remaining == 0

        except urllib.error.HTTPError as e:
            if e.code == 401 and retry_count == 0:
                if token_manager.refresh_token():
                    retry_count += 1
                    continue
            print(f"❌ 验证失败: {e}")
            return False
        except Exception as error:
            print(f"❌ 验证失败: {error}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("Gmail 批量清理工具 v2.0 (支持Token自动刷新)")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 初始化Token管理器
    token_manager = TokenManager()
    if not token_manager.get_token():
        print("❌ Token加载失败")
        return

    print("✅ Token 加载成功")

    # 加载进度
    progress = load_progress()

    # 获取未读邮件列表
    message_ids = get_unread_emails(token_manager)

    if not message_ids:
        print("✅ 收件箱已经是空的！")
        return

    print(f"\n📊 统计信息:")
    print(f"   总邮件数: {len(message_ids)}")
    print(f"   已处理: {progress['processed']}")
    print(f"   待处理: {len(message_ids) - progress['processed']}")

    # 确认操作
    print(f"\n⚠️  即将批量处理 {len(message_ids)} 封邮件：")
    print("   - 标记为已读")
    print("   - 归档（移出收件箱）")
    print("\n开始执行...（3秒后自动开始）")
    time.sleep(3)

    # 批量处理
    batch_mark_read_and_archive(token_manager, message_ids, progress)

    # 验证结果
    verify_inbox_empty(token_manager)

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  用户中断，进度已保存")
        print(f"恢复方法: 重新运行此脚本即可从断点继续")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("进度已保存，可稍后重试")
