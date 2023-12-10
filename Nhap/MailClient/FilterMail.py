import os
import json

def save_email_filtered(email_address, email_info, raw_email_data):
    # Lấy đường dẫn của chương trình
    program_path = os.getcwd()
    # Lọc folder tương ứng với mail
    folder = folder_sort(email_info)
    # Cấu hình lại file
    msg = '\n'.join(raw_email_data)

    # Folder chương trình/Folder người dùng/Folder lọc/File mail
    email_path = os.path.join(program_path, str(email_address), folder, email_info['UniqueID'])
    with open(email_path, 'w') as f:
        f.write(msg)
            
def folder_sort(email_info):
    # Filters lưu trữ nội dung của file filter.json
    with open('filter.json', 'r') as f:
        filter_items = json.load(f)

    # Sau đó xét lần lượt các item trong data
    for filter_item in filter_items["filters"]:
        # Xét từng keyword trong item
        for keyword in filter_item["keywords"]:
            # Xét từng thông tin trong email
            for info in email_info:
                # Nếu keyword nào trong item trùng với keyword nào trong email thì trả về folder
                if keyword in info:
                    return filter_item["folder"]
    return "Inbox"
