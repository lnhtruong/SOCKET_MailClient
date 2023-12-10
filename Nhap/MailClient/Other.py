# Thư viện Regular Expressions (biểu thức chính quy)
# Ví dụ: tìm, so, xử lý chuỗi,...
import re
# Thư viện OS (hệ điều hành)
# Ví dụ: tạo, xóa, di chuyển, đổi tên, đọc, ghi file,...
import os
# Thư viện JSON (đọc, ghi file JSON)
import json

def extract_email_address(user_name):
    # Kiểm tra và tạo thư mục cho người dùng
    # r là tiền tố để xử lý ký tự đặc biệt mà không xóa chúng
    # r'<([^>]+)>' có nghĩa là đọc chuỗi trong dấu < và >
    match = re.search(r'<([^>]+)>', user_name)
    
    ### Giải thích match.group(1)
    # Số 1 có nghĩa là nó trả về chuỗi khớp đầu tiên
    # Nếu thay bằng 0 thì nó sẽ trả về toàn bộ chuỗi
    # Nếu để trống thì nó sẽ tự thay 0 nếu không tìm thấy và 1 nếu tìm thấy
    
    if match:
        return match.group(1)
    else:
        return None
    
def folder_isExist(user_name):
    # Lấy đường dẫn hiện tại của chương trình
    program_path = os.getcwd()
    # Lấy danh sách các tệp và thư mục trong đường dẫn hiện tại
    file_folders = os.listdir(program_path)

    # Tạo thư mục cho người dùng nếu chưa có
    if user_name not in file_folders:
        os.makedirs(user_name) # Tạo thư mục
        
    raw_data = {user_name: [
                    {"STT": 0,
                    "UniqueID": "Example",
                    "Status": "Unread",
                    "Size": 0,
                    "From": "",
                    "Subject": "",
                    "Date": "",
                    "To": [],
                    "CC": [],
                    "Body": "",
                    "has_attachment": False,
                    "Num_Attached": 0
                    }
                ]
            }
    
    # Tạo file uidl.json cho chương trình nếu chưa có
    if "uidl.json" not in file_folders:
        with open('uidl.json', 'w') as f:
            json.dump(raw_data, f, indent=2)
    else:
        with open('uidl.json', 'r') as f:
            data = json.load(f)
        if user_name not in data:
            data.update(raw_data)
            with open('uidl.json', 'w') as f:
                json.dump(data, f, indent=2)
                
    # Tạo file filter.json cho chương trình nếu chưa có
    if "filter.json" not in file_folders:
        with open('filter.json', 'w') as f:
            filter_content = {
            "filters": [
                {
                    "keywords": ["virus", "hack", "crack"],
                    "folder": "Spam"
                },
                {
                    "keywords": ["urgent", "ASAP"],
                    "folder": "Important"
                },
                {
                    "keywords": ["Tuan01@testing.com", "Truong02@testing.com"],
                    "folder": "Project"
                },
                {
                    "keywords": ["report", "meeting"],
                    "folder": "Work"
                }
            ]
            }
            json.dump(filter_content, f, indent=2)

    os.chdir(user_name) # Di chuyển đến thư mục của người dùng
    # Lấy danh sách các tệp và thư mục trong thư mục của người dùng
    file_folders = os.listdir(os.getcwd())

    # Tạo các thư mục con cho người dùng nếu chưa có
    folders = ["Project", "Attachments", "Important", "Work", "Spam", "Inbox"]
    for folder in folders:
        if folder not in file_folders:
            os.makedirs(folder)  # Tạo thư mục
    
    # Quay lại thư mục chương trình      
    os.chdir(program_path) 
    
def get_server_info(user_info):
    server_info = {'MailServer': '',
                   'SMTP': int,
                   'POP3': int,
                   'AutoLoad': int
                   }
    with open('account.json', 'r') as f:
        data = json.load(f)
        for account_inJson in data["account"]:
            if (account_inJson["Username"] == user_info["Username"]):
                server_info["MailServer"] = account_inJson["MailServer"]
                server_info["SMTP"] = account_inJson["SMTP"]
                server_info["POP3"] = account_inJson["POP3"]
                server_info["AutoLoad"] = account_inJson["AutoLoad"]
                return server_info
    
def get_email_info(msg_name, email_address):
    with open ("uidl.json", 'r') as f:
        data = json.load(f)
    email_infos = data[email_address]

    for email_info in email_infos:
        if (str(msg_name) == email_info["UniqueID"]):
            return email_info
