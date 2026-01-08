
import os
import json
import time
import re
import random
from collections import defaultdict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
KEYWORD_TO_DELETE = 'forum'
# --- File names for state management ---
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
ALL_IDS_FILE = 'gmail_all_ids.json'
PROGRESS_FILE = 'gmail_progress.json'
TO_ARCHIVE_FILE = 'gmail_to_archive.json'
TO_DELETE_FILE = 'gmail_to_delete.json'
# --- Batching Configuration ---
CLASSIFY_CHUNK_SIZE = 5000  # Process up to 5000 emails in one run of the script.

def authenticate():
    """Handles user authentication and returns a valid credential object."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("正在刷新授权...")
            creds.refresh(Request())
        else:
            print("需要您进行授权...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

# Removed execute_batch_with_retry as it's not used in sequential processing

def phase_one_fetch_ids(service):
    """
    Fetches all message IDs from the INBOX and saves them to a file.
    Skips if the file already exists.
    """
    if os.path.exists(ALL_IDS_FILE):
        print(f"'{ALL_IDS_FILE}' 文件已存在，跳过邮件ID获取阶段。")
        with open(ALL_IDS_FILE, 'r') as f:
            return json.load(f)

    print("阶段1: 正在获取整个收件箱的邮件ID（这可能需要一些时间）...")
    all_messages = []
    page_token = None
    while True:
        try:
            results = service.users().messages().list(
                userId='me', labelIds=['INBOX'], maxResults=500, pageToken=page_token
            ).execute()
            
            messages_page = results.get('messages', [])
            if messages_page:
                all_messages.extend(messages_page)
                print(f"已获取 {len(all_messages)} 封邮件ID...")

            page_token = results.get('nextPageToken')
            if not page_token:
                break
            time.sleep(0.1) # Be gentle with the list API
        except HttpError as e:
            print(f"获取邮件列表时出错: {e}。等待10秒后重试...")
            time.sleep(10)

    with open(ALL_IDS_FILE, 'w') as f:
        json.dump(all_messages, f)
    
    print(f"所有邮件ID已保存至 '{ALL_IDS_FILE}'。")
    return all_messages

def phase_two_classify_messages(service, all_message_ids):
    """
    Classifies messages sequentially and saves progress.
    Returns True if classification is complete, False otherwise.
    """
    print("\n阶段2: 分析和分类邮件...")
    
    start_index = 0
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
            start_index = progress.get('next_index', 0)

    ids_to_archive = []
    if os.path.exists(TO_ARCHIVE_FILE):
        with open(TO_ARCHIVE_FILE, 'r') as f:
            ids_to_archive = json.load(f)
            
    ids_to_delete = []
    if os.path.exists(TO_DELETE_FILE):
        with open(TO_DELETE_FILE, 'r') as f:
            ids_to_delete = json.load(f)

    total_messages = len(all_message_ids)
    if start_index >= total_messages:
        print("所有邮件都已分类完毕！")
        return True

    print(f"从第 {start_index + 1} 封邮件开始处理（共 {total_messages} 封）。")
    
    current_chunk_end_index = min(start_index + CLASSIFY_CHUNK_SIZE, total_messages)
    
    for i in range(start_index, current_chunk_end_index):
        message_obj = all_message_ids[i]
        msg_id = message_obj['id']
        
        if (i - start_index) % 100 == 0: # Print progress every 100 emails
             print(f"  正在分析第 {i + 1} / {total_messages} 封邮件...")

        try:
            # DIRECT SEQUENTIAL API CALL
            response = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['subject']).execute() 
            
            headers = response.get('payload', {}).get('headers', [])
            subject = ''
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = header['value']
                    break
            
            if re.search(KEYWORD_TO_DELETE, subject, re.IGNORECASE):
                ids_to_delete.append(msg_id)
            else:
                ids_to_archive.append(msg_id)

            time.sleep(0.1) # Small delay to be respectful to the API

        except HttpError as e:
            print(f"处理邮件 {msg_id} 时出错: {e}。")
            if e.resp.status in [429, 500, 502, 503, 504]:
                print("检测到频率限制或服务器错误，暂停30秒后重试当前邮件...")
                time.sleep(30)
                # Decrement i so this email is retried on the next loop iteration
                i -= 1 
                continue 
            else:
                print("发生无法重试的错误，跳过此邮件。")
                continue # Skip this email if it's not a retryable error
        except Exception as e:
            print(f"处理邮件 {msg_id} 时发生意外错误: {e}。跳过此邮件。")
            continue


    # De-duplicate lists (in case of retries or previous runs)
    ids_to_archive = list(set(ids_to_archive))
    ids_to_delete = list(set(ids_to_delete))

    with open(TO_ARCHIVE_FILE, 'w') as f:
        json.dump(ids_to_archive, f)
    with open(TO_DELETE_FILE, 'w') as f:
        json.dump(ids_to_delete, f)

    # Save the new progress
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({'next_index': current_chunk_end_index}, f)
        
    print(f"\n本轮分析完成。进度: {current_chunk_end_index}/{total_messages}。")
    
    if current_chunk_end_index >= total_messages:
        print("所有邮件都已分类完毕！")
        return True
    else:
        print("请再次运行脚本以处理下一批邮件。")
        return False

def phase_three_execute_actions(service):
    """
    Reads the classified ID files and executes the final actions after confirmation.
    """
    print("\n阶段3: 执行操作...")

    with open(TO_ARCHIVE_FILE, 'r') as f:
        ids_to_archive = json.load(f)
    with open(TO_DELETE_FILE, 'r') as f:
        ids_to_delete = json.load(f)

    print("\n--- 最终确认 ---")
    print(f"将删除 {len(ids_to_delete)} 封邮件 (主题包含 '{KEYWORD_TO_DELETE}')")
    print(f"将归档 {len(ids_to_archive)} 封邮件")
    print("--------------------")

    if not ids_to_delete and not ids_to_archive:
        print("没有需要处理的邮件。" )
        for f in [ALL_IDS_FILE, PROGRESS_FILE, TO_ARCHIVE_FILE, TO_DELETE_FILE]:
            if os.path.exists(f): os.remove(f)
        return

    try:
        confirm = input("**警告：此操作无法撤销！**\n请输入 'yes' 以继续执行: ").strip().lower()
    except EOFError:
        print("在非交互模式下无法获取确认。操作已取消。")
        confirm = 'no'

    if confirm == 'yes':
        action_batch_size = 1000 # Gmail API batchDelete and batchModify have a limit of 1000 IDs. 
        
        # Perform deletion in chunks
        if ids_to_delete:
            print(f"正在分批删除 {len(ids_to_delete)} 封邮件...")
            for k in range(0, len(ids_to_delete), action_batch_size):
                id_chunk = ids_to_delete[k:k + action_batch_size]
                # No batching for individual actions, just direct call and retry
                # This part already uses batch.execute() in the original script and it has its own retry logic.
                # It's not a single GET request but a batchModify/batchDelete which are designed for bulk ops.
                try:
                    service.users().messages().batchDelete(userId='me', body={'ids': id_chunk}).execute()
                    print(f"  已删除 {min(k + action_batch_size, len(ids_to_delete))} / {len(ids_to_delete)}")
                    time.sleep(1)
                except HttpError as e:
                    print(f"删除批次时出错: {e}. 跳过此批次。")


            print("删除完成。" )

        # Perform archiving in chunks
        if ids_to_archive:
            print(f"正在分批归档 {len(ids_to_archive)} 封邮件...")
            for k in range(0, len(ids_to_archive), action_batch_size):
                id_chunk = ids_to_archive[k:k + action_batch_size]
                try:
                    service.users().messages().batchModify(userId='me', body={'ids': id_chunk, 'removeLabelIds': ['INBOX']}).execute()
                    print(f"  已归档 {min(k + action_batch_size, len(ids_to_archive))} / {len(ids_to_archive)}")
                    time.sleep(1)
                except HttpError as e:
                    print(f"归档批次时出错: {e}. 跳过此批次。")
            print("归档完成。" )
        
        print("\n所有操作已完成！正在清理临时文件...")
        for f in [ALL_IDS_FILE, PROGRESS_FILE, TO_ARCHIVE_FILE, TO_DELETE_FILE]:
            if os.path.exists(f): os.remove(f)
        print("清理完毕。" )
    else:
        print("操作已取消。" )

def main():
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        all_message_ids = phase_one_fetch_ids(service)
        
        is_classification_complete = phase_two_classify_messages(service, all_message_ids)

        if is_classification_complete:
            phase_three_execute_actions(service)

    except Exception as error:
        print(f'发生严重错误: {error}')

if __name__ == '__main__':
    main()
