import os.path
import re
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# --- Configuration ---
# The keyword for deletion (case-insensitive)
KEYWORD_TO_DELETE = 'forum'
# ---------------------


def main():
    """
    Connects to the Gmail API, fetches ALL emails from the inbox using pagination,
    classifies them for deletion (by keyword) and archiving, and executes
    the actions after a final user confirmation.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)

        # 1. Fetch ALL messages from the INBOX using pagination
        print("正在获取整个收件箱的邮件（这可能需要一些时间）...")
        all_messages = []
        page_token = None
        while True:
            results = service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                maxResults=500,  # Fetch in pages of 500
                pageToken=page_token
            ).execute()
            
            messages_page = results.get('messages', [])
            if messages_page:
                all_messages.extend(messages_page)
                print(f"已获取 {len(all_messages)} 封邮件...")

            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        if not all_messages:
            print("收件箱中没有找到邮件。\n")
            return
        
        print(f"\n共找到 {len(all_messages)} 封邮件。现在开始分析...")

        # 2. Analyze messages in batches
        ids_to_archive = []
        ids_to_delete = []
        
        callback_data = {'delete': ids_to_delete, 'archive': ids_to_archive}

        def classification_callback(request_id, response, exception):
            if exception is None:
                msg_id = request_id.split('-')[1]
                headers = response.get('payload', {}).get('headers', [])
                subject = ''
                for header in headers:
                    if header['name'].lower() == 'subject':
                        subject = header['value']
                        break
                
                if re.search(KEYWORD_TO_DELETE, subject, re.IGNORECASE):
                    callback_data['delete'].append(msg_id)
                else:
                    callback_data['archive'].append(msg_id)

        batch_size = 100
        for i in range(0, len(all_messages), batch_size):
            batch = service.new_batch_http_request()
            chunk = all_messages[i:i + batch_size]
            print(f"正在处理第 {i+1} 至 {i+len(chunk)} 封邮件...")

            for j, message in enumerate(chunk):
                req_id = f"msg-{message['id']}-{i}-{j}"
                batch.add(service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['subject']), callback=classification_callback, request_id=req_id)
            
            batch.execute()

        # 3. Final confirmation and execution
        print("\n--- 分析完成 ---")
        print(f"找到 {len(ids_to_delete)} 封要删除的邮件 (主题包含 '{KEYWORD_TO_DELETE}')")
        print(f"找到 {len(ids_to_archive)} 封要归档的邮件")
        print("--------------------")

        if not ids_to_delete and not ids_to_archive:
            print("没有需要处理的邮件。\n")
            return

        print("\n**警告：删除操作无法撤销！**")
        confirm = input("请输入 'yes' 以继续执行删除和归档操作: ").strip().lower()

        if confirm == 'yes':
            # Gmail API batchDelete and batchModify have a limit of 1000 IDs per request.
            
            # Perform deletion in chunks of 1000
            if ids_to_delete:
                print(f"正在删除 {len(ids_to_delete)} 封邮件...")
                for k in range(0, len(ids_to_delete), 1000):
                    id_chunk = ids_to_delete[k:k + 1000]
                    service.users().messages().batchDelete(
                        userId='me',
                        body={'ids': id_chunk}
                    ).execute()
                print("删除完成。\n")

            # Perform archiving in chunks of 1000
            if ids_to_archive:
                print(f"正在归档 {len(ids_to_archive)} 封邮件...")
                for k in range(0, len(ids_to_archive), 1000):
                    id_chunk = ids_to_archive[k:k + 1000]
                    service.users().messages().batchModify(
                        userId='me',
                        body={'ids': id_chunk, 'removeLabelIds': ['INBOX']}
                    ).execute()
                print("归档完成。\n")
            
            print("\n所有操作已完成！")
        else:
            print("操作已取消。\n")

    except HttpError as error:
        print(f'发生错误: {error}')
    except FileNotFoundError:
        print("错误: 'credentials.json' 文件未找到。\n")


if __name__ == '__main__':
    main()