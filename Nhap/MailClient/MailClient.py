import socket
# Mã hóa và giải mã dữ liệu nhị phân theo định dạng base64
import base64
# Cung cấp tương tác với hệ diều hành (Dùng trong thao tác tệp tin)
import os
# Cung cấp phương thức thao tác file json
import json
# Thư viện Regular Expressions (biểu thức chính quy)
# Ví dụ: tìm, so, xử lý chuỗi,...
import re
# import email
# Lấy tên cơ bản của một tệp từ đường dẫn
from os.path import basename
# Một lớp để tạo các tin nhắn MIME phần đa, có thể bao gồm cả văn bản thuần và các đính kèm
from email.mime.multipart import MIMEMultipart
# Một lớp để tạo các tin nhắn MIME văn bản
from email.mime.text import MIMEText
# Một lớp cơ sở cho tất cả các lớp con cụ thể của MIME
from email.mime.base import MIMEBase
# Chứa các hàm để mã hóa và giải mã nội dung MIME của các loại khác nhau
from email import encoders
# Nhận biết ngôn ngữ
# import langid
# Lấy dữ liệu ngày giờ và múi giờ
import datetime
import uuid
import threading
import time

FORMAT = 'utf-8'
exit_flag = False

# HÀM MAIN
def main(user_info, server_info): 
# Bắt đầu giao diện người dùng
    email_address = extract_EmailAddress(user_info["Username"])
    
    while True:
        print("Menu:")
        print("1. Send mail")
        print("2. View a list of received emails")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
    # GỬI MAIL
        if choice == '1':
            menu_send_mail(user_info, server_info)

    # XEM MAIL
        elif choice == '2':
            watch_mail(email_address)      

    # THOÁT
        elif choice == '3':
            global exit_flag
            exit_flag = True
            print("Exiting program...")
            break

    # NHẬP SAI
        else:
            print("Invalid choice! Please try again!")
            print('------------------------------------------------------------------')
            continue
            

# CÁC HÀM ĐĂNG NHẬP
def login():
    # Khởi tạo và nhập thông tin người dùng
    username = "Kelvin" #input("Enter username: ")
    email_address = "ahihi.gioi@gmail.com" #input("Enter email address: ")
    user_info = {'Username': username + " <" + email_address + ">",
                 'Password': input("Enter password: "),
                 'MailServer': '127.0.0.1',
                 'SMTP': 2225,
                 'POP3': 3335,
                 'AutoLoad': 10
                 }
      
# Kiểm tra tài khoảng người dùng
    check_account(user_info)
    return user_info
    
def check_account(user_info):
    try:
        with open('account.json', 'r') as f:
            data = json.load(f)
            # Vòng lặp để duyệt qua từng tài khoản trong file json
            for account in data['account']:
                # Check xem tài khoản đã tồn tại hay chưa
                if check_again(account, user_info) == True:
                    return
            # Nếu chưa thì tạo tài khoản mới 
            create_account(user_info)
            return
    # Nếu file json chưa tồn tại thì tạo file json và tạo tài khoản mới
    except FileNotFoundError:
        data = {'account': []}
        data['account'].append(user_info)
        with open('account.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Account created successfully!")
        print('------------------------------------------------------------------')
        
def check_again(account, user_info):
    try:
        # Tách gmail từ account
        match = re.search(r'<([^>]+)>', account['Username'])
        gmail_inServer = match.group(1)
        
        # Tách gmail từ username
        match = re.search(r'<([^>]+)>', user_info['Username'])
        gmail_ofUser = match.group(1)

        # Nếu người dùng nhập đúng gmail thì kiểm tra username
        if gmail_inServer == gmail_ofUser:
            # Nếu username đúng thì kiểm tra password
            if account['Username'] == user_info['Username']:
                while True:
                    # Nếu password đúng thì thông báo đăng nhập thành công
                    if account['Password'] == user_info['Password']:
                        print("Login successfully!")
                        print('------------------------------------------------------------------')
                        return True
                    # Nếu password sai thì yêu cầu nhập lại password
                    else:
                        print("Wrong password!", end=' - ')
                        user_info['Password'] = input("Enter password again (Enter 0 to EXIT): ")
                        if user_info['Password'] == '0':
                            return True
            else:
                print("Wrong username!", end=' - ')
                user_info['Username'] = input("Just enter username again (Enter 0 to EXIT): ")
                if user_info['Username'] == '0':
                    return True
                user_info['Username'] += ' <{}>'.format(gmail_ofUser)
                if check_again(account, user_info):
                    return True
    except AttributeError:
        return False

def create_account(user_info):
    with open('account.json', 'r') as f:
        data = json.load(f)
        data['account'].append(user_info)
    with open('account.json', "w") as json_file:
        json.dump(data, json_file, indent=2)
    print("Account created successfully!")
    print('------------------------------------------------------------------')
    
def folder_isExist(username):
    # Lấy đường dẫn hiện tại của chương trình
    program_address = os.getcwd()
    # Lấy danh sách các tệp và thư mục trong đường dẫn hiện tại
    list_file_folder = os.listdir(program_address)

    # Tạo thư mục cho người dùng nếu chưa có
    if username not in list_file_folder:
        os.makedirs(username) # Tạo thư mục
        
    data_raw = {username: [
                    {"STT": 0,
                    "msg": "Example",
                    "Status": "Unread",
                    "Capacity": 0,
                    "From": "",
                    "Subject": "",
                    "Date": "",
                    "To": [],
                    "CC": [],
                    "Body": "",
                    "has_attachment": False,
                    "Num_File": 0
                    }
                ]
            }
    # Tạo file uidl.json cho chương trình nếu chưa có
    if "uidl.json" not in list_file_folder:
        with open('uidl.json', 'w') as f:
            json.dump(data_raw, f, indent=2)
    else:
        with open('uidl.json', 'r') as f:
            data = json.load(f)
        if username not in data:
            data.update(data_raw)
            with open('uidl.json', 'w') as f:
                json.dump(data, f, indent=2)
                
    # Tạo file filter.json cho chương trình nếu chưa có
    if "filter.json" not in list_file_folder:
        with open('filter.json', 'w') as f:
            filter_content = {
            "filters": [
                {
                    "keywords": ["Tuan01@testing.com", "Truong02@testing.com"],
                    "folder": "Project"
                },
                {
                    "keywords": ["virus", "hack", "crack"],
                    "folder": "Spam"
                },
                {
                    "keywords": ["report", "meeting"],
                    "folder": "Work"
                },
                {
                    "keywords": ["urgent", "ASAP"],
                    "folder": "Important"
                }
            ]
            }
            json.dump(filter_content, f, indent=2)

    os.chdir(username) # Di chuyển đến thư mục username
    # Lấy danh sách các tệp và thư mục trong đường dẫn hiện tại
    list_file_folder = os.listdir(os.getcwd())

    # Tạo các thư mục con cho người dùng nếu chưa có
    folders = ["Project", "Attachments", "Important", "Work", "Spam", "Inbox"]
    for folder in folders:
        if folder not in list_file_folder:
            os.makedirs(folder)  # Tạo thư mục
    
    # Di chuyển đến thư mục chương trình        
    os.chdir(program_address) 
    
def get_server_info(user_info):
    server_info = {'MailServer': '',
                   'SMTP': int,
                   'POP3': int,
                   'AutoLoad': int
                   }
    with open('account.json', 'r') as f:
        data = json.load(f)
        for account in data["account"]:
            if (account["Username"] == user_info["Username"]):
                server_info["MailServer"] = account["MailServer"]
                server_info["SMTP"] = account["SMTP"]
                server_info["POP3"] = account["POP3"]
                server_info["AutoLoad"] = account["AutoLoad"]
                return server_info


# CÁC HÀM GỬI MAIL
def menu_send_mail(user_info, server_info):
    print("This is information for composing an email (press Enter to PASS)...")
    # Kiểu gửi TO và CC
    to = input('TO: ')
    cc = input('CC: ')
    bcc = input('BCC: ')
    # Nội dung mail
    subject = input("Subject: ")
    content = input("Content: ")
    attached_files = []  # Danh sách các tệp đính kèm
    # Phần nhập attach file
    choice_attach = input("Do you want to send attachment files? (1. Yes, 2. No): ")
    if choice_attach == '1':
        MAX_SIZE = 3 * 1024 * 1024
        remain_size = MAX_SIZE
        num = int(input("Number of files: "))

        for i in range(num):
            while True:
                path = input(f"Enter path for file {i + 1}: ")
                try:
                    file_size = os.path.getsize(path)
                    with open(path, 'rb') as file:
                        pass

                    if file_size > remain_size:
                        print(f"Attached file exceeds remaining maximum size. "
                              f"Current size: {file_size} bytes, Remaining maximum allowed size: {remain_size} bytes")
                        print("Please try again.")
                    else:
                        attached_files.append(path)  # Thêm đường dẫn tệp vào danh sách đính kèm
                        remain_size -= file_size
                        break

                except FileNotFoundError:
                    print(f"File not found: {path}. Please enter a valid file path.")
                except IOError as e:
                    print(f"Error opening file {path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

    # Gọi hàm send_mail với danh sách tệp đính kèm
    send_mail(user_info, server_info, to, subject, content, cc, bcc, attached_files)
    print("SEND SUCCESSFULLY!")
    print('------------------------------------------------------------------')

def send_mail(user_info, server_info, to, subject, content, cc=None, bcc=None, attachments=None):
    # Dùng khối try để gửi mail
    try:
        # Mở kết nối socket
        smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        smtp_socket.connect((server_info["MailServer"], int(server_info["SMTP"])))
        # Nhận thông tin lời chào từ server
        welcome_message = smtp_socket.recv(1024).decode()

        try:
            if attachments:
                msg = MIMEMultipart()
            else:
                msg = MIMEText(content + '\r\n', 'plain')
                msg.replace_header('Content-Type', 'text/plain; charset=UTF-8; format=flowed')
                # Xóa dòng MIME-Version
                del msg['MIME-Version']

            # Gửi lệnh EHLO để bắt đầu
            global FORMAT
            message = 'EHLO [{}] \r\n'.format(str(user_info['MailServer'])).encode(FORMAT)
            smtp_socket.send(message)
            # Tách email từ username
            match = re.search(r'<([^>]+)>', user_info['Username'])
            email = match.group(1)
            # Gửi lệnh MAIL FROM
            mail_from = 'MAIL FROM:<{}> \r\n'.format(email).encode(FORMAT)
            smtp_socket.send(mail_from)

            to_addresses = []
            # Gửi lệnh RCPT TO cho người nhận TO
            if to.strip():
                to_addresses = to.split(',')  # Lấy mail đã được format lại
                for address in to_addresses:
                    # Gửi các mail đã được format lại (Xóa bỏ khoảng trắng, newline, carriage return)
                    smtp_socket.send(f'RCPT TO:<{address.strip()}> \r\n'.encode(FORMAT))

            cc_addresses = []
            # Gửi lệnh RCPT TO cho người nhận CC
            if cc.strip():  # Kiểm tra xem có mail gửi dạng cc không
                cc_addresses = cc.split(',')  # Lấy mail đã được format lại
                for address in cc_addresses:
                    smtp_socket.send(f'RCPT TO:<{address.strip()}> \r\n'.encode(FORMAT))

            bcc_addresses = []
            # Gửi lệnh RCPT TO cho người nhận BCC
            if bcc.strip():  # Kiểm tra xem có mail gửi dạng bcc không
                bcc_addresses = bcc.split(',')  # Lấy mail đã được format lại
                for address in bcc_addresses:
                    smtp_socket.send(f'RCPT TO:<{address.strip()}> \r\n'.encode(FORMAT))

            # Lệnh DATA
            smtp_socket.sendall(b'DATA\r\n')
            unique_id = str(uuid.uuid4())
            msg['Message-ID'] = f"<{unique_id}@gmail.com>"
            now = datetime.datetime.now(datetime.timezone.utc).astimezone()
            # Định dạng lại ngày tháng
            # %a: viết tắt tên ngày trong tuần
            # %d: ngày trong tháng dưới dạng 01,02,...
            # %b: tên tháng viết tắt
            # %Y: tên năm viết đầy đủ
            # %H: giờ viết dưới dạng 01,02,...
            # %M: phút viết dưới dạng 01,02,...
            # %S: giây viết dưới dạng 01,02,...
            # %z  Mốc giờ dưới dạng +HHMM hoặc -HHMM
            formatted_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")
            # Assign to the 'Date' field in your message
            msg['Date'] = formatted_date
            ##### language, confidence = langid.classify(content)
            ##### msg['Content-Language'] = language
            if bcc.strip() and not to.strip() and not cc.strip():
                msg['To'] = 'undisclosed-recipients: ;'
            else:
                if to.strip():
                    msg['To'] = ", ".join(to_addresses)
                if cc.strip():
                    msg['Cc'] = ",".join(cc_addresses)

            msg['From'] = user_info["Username"]
            msg['Subject'] = subject
            if attachments:
                # text/plain: Chỉ định nội dung văn bản của email không chứa định dạng đặc biệt
                body = MIMEText(content + '\r\n', 'plain')
                body.replace_header('Content-Type', 'text/plain; charset=UTF-8; format=flowed')
                # Xóa dòng MIME-Version
                del body['MIME-Version']
                msg.attach(body)
            # Thêm file đính kèm
            if attachments:
                for path in attachments:
                    send_file(path, msg)

            # Xử lý khoảng trắng trước dấu chấm
            smtp_socket.sendall(f'{msg.as_string()}\r\n.\r\n'.replace('\r\n\r\n.\r\n', '\r\n.\r\n').encode(FORMAT))
            response = smtp_socket.recv(1024)
            if not response.startswith(b'250'):
                return

        except Exception as e:
            # Handle exceptions appropriately
            print(f"An error occurred: {e}")
        finally:
            smtp_socket.send(b'QUIT\r\n')
                
    # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
    # Thông tin lỗi sẽ lưu vào biến e
    except Exception as e:
        smtp_socket.close()  # Đóng kết nối socket để tránh rò rỉ kết nối
        print(f"Error: {e}")  # Xuất thông tin lỗi lên màn hình
        print("Disconnected from SERVER!")
        return

def send_file(path, msg):
    file_name = basename(path)
    # Mở chế độ đọc nhị phân 'rb'
    with open(path, 'rb') as attachment_file:
        last_four_char = file_name[-4:].lower()
        # Khởi tạo Content-Type mặc định
        maintype = 'application'
        subtype = 'octet-stream'
        if last_four_char == '.txt':
            maintype = 'text'
            subtype = 'plain'
        elif last_four_char == '.pdf':
            maintype = 'application'
            subtype = 'pdf'
        elif last_four_char == '.jpg' or last_four_char == 'jpeg':
            maintype = 'image'
            subtype = 'jpeg'
        elif last_four_char == '.png':
            maintype = 'image'
            subtype = 'png'
        elif last_four_char == '.zip':
            maintype = 'application'
            subtype = 'zip'
        elif last_four_char == '.doc':
            maintype = 'application'
            subtype = 'msword'
        elif last_four_char == 'docx':
            maintype = 'application'
            subtype = 'vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif last_four_char == '.xls':
            maintype = 'application'
            subtype = 'vnd.ms-excel'
        elif last_four_char == 'xlsx':
            maintype = 'application'
            subtype = 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif last_four_char == '.ppt':
            maintype = 'application'
            subtype = 'vnd.ms-powerpoint'
        elif last_four_char == 'pptx':
            maintype = 'application'
            subtype = 'vnd.openxmlformats-officedocument.presentationml.presentation'
        elif last_four_char == "json":
            maintype = 'application'
            subtype = 'json'

        attachment_package = MIMEBase(maintype, subtype, name=f'{file_name}')
        # Đặt dữ liệu tệp tin đã được mã hóa vào đối tượng MIMEBase
        attachment_package.set_payload(attachment_file.read())
        attachment_package.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
        encoders.encode_base64(attachment_package)

        # Xóa dòng MIME-Version (được thêm tự động)
        del attachment_package['MIME-Version']

        msg.attach(attachment_package)
        
    
# CÁC HÀM NHẬN MAIL
def receive_mail(user_info, server_info):
    global FORMAT
    try:
        # Mở kết nối socket
        pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pop3_socket.connect((server_info["MailServer"], server_info["POP3"]))
        # Nhận thông tin lời chào từ server
        welcome_message = pop3_socket.recv(1024).decode()
        
        # SEND CAPA
        pop3_socket.send(b'CAPA\r\n')
        pop3_socket.recv(1024).decode()

        # Tách email từ username
        match = re.search(r'<([^>]+)>', user_info['Username'])
        email_address = match.group(1)
        # SEND USER
        pop3_socket.send(f'USER {email_address}\r\n'.encode())
        pop3_socket.recv(1024).decode()

        # SEND PASS
        pop3_socket.send(f'PASS {user_info["Password"]}\r\n'.encode())
        pop3_socket.recv(1024).decode()
    
        # SEND STAT
        pop3_socket.send(b'STAT\r\n')
        ## TRẢ VỀ: +OK x y (x là số mail, y là tổng kích thước theo byte)
        response = pop3_socket.recv(1024).decode(FORMAT)
    
        num_mail = response[4] # Lấy x trong +OK x y
    
        # SEND LIST
        pop3_socket.send(b'LIST\r\n')
        ## TRẢ VỀ: 
        # +OK
        # Thứ tự mail _ size mail
        # .
        response = pop3_socket.recv(2048).decode(FORMAT)
    
        # Lấy dung lượng các mail
        capacity = get_mail_capacity(response)

        # SEND UIDL
        pop3_socket.send(b'UIDL\r\n')
        ## TRẢ VỀ: 
        # +OK
        # Thứ tự mail _ <mã độc nhất>.msg
        # .
        response = pop3_socket.recv(2048).decode(FORMAT)
    
        # Tải mail về máy
        download_mail(pop3_socket, response, email_address, capacity)

    except Exception as e:
        # Kiểm tra xem pop3_socket có tồn tại không
        if pop3_socket:
            try:
                # Đóng kết nối socket nếu chưa được đóng
                pop3_socket.send(b'QUIT\r\n')
                pop3_socket.close()
            except Exception as close_error:
                    # Xử lý lỗi khi đóng kết nối socket
                print(f"Error closing socket: {close_error}")

        print(f"Error: {e}")
        print("Disconnected from SERVER!")
        
def get_mail_capacity(response):
    # Lấy các dòng phản hồi LIST từ server
    list_lines = response.split('\r\n')
    capacity = {}
    
    # Đọc các dòng LIST trừ dòng đầu (+OK) và dòng cuối (.)
    for i, list_line in enumerate(list_lines[1:-2], start=0):
        capacity[i] = int(list_line[2:])
    
    return capacity    
    
def download_mail(pop3_socket, response, email_address, capacity):            
    # Lấy các dòng phản hồi UIDL từ server
    uidl_lines = response.split('\r\n')
    
    # Đọc các dòng UIDL trừ dòng đầu (+OK) và dòng cuối (.)
    for i, uidl_line in enumerate(uidl_lines[1:-2], start=0):
        with open('uidl.json', 'r') as f:
            data = json.load(f)
            
            check = False
            # Chạy vòng lặp kiểm tra xem mail đã được tải về chưa
            for email_info in data[str(email_address)]:
                if str(email_info["msg"]) == str(uidl_line[2:]):
                    check = True
                    break
                
            # Nếu mail chưa được tải về thì tải về
            if check == False:
                pop3_socket.send('RETR {}\r\n'.format(uidl_line[0]).encode())  
                response = pop3_socket.recv(capacity[i]).decode()
                retr_lines = response.split('\r\n')
                # raw_email_data = '\n'.join(retr_lines[1:-2])
                # raw_email_data = email.message_from_string(raw_email_data, uidl_line, capacity)
                email_info = parse_email(retr_lines[1:-2], uidl_line, capacity[i])
                save_mail_filtered(email_address, email_info, retr_lines[1:-2])
                with open('uidl.json', 'r') as f:
                    data = json.load(f)
                    data[str(email_address)].append(email_info)
                with open('uidl.json', 'w') as f:
                    json.dump(data, f, indent=2)

def parse_email(retr_lines, uidl_line, capacity):
    email_info = {
        "STT": int(uidl_line[0]),
        "msg": str(uidl_line[2:]),
        "Status": "Unread",
        "Capacity": capacity,
        "From": "",
        "Subject": "",
        "Date": "",
        "To": [],
        "CC": [],
        "Body": "",
        "has_attachment": False,
        "Num_File": 0
    }
    
    # Lấy các dữ liệu cơ bản
    for retr_line in retr_lines:
        if retr_line.startswith("From"):
            email_info["From"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("Subject"):
            email_info["Subject"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("Date"):
            email_info["Date"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("To"):
            tos = retr_line.split(":")[1].strip()
            for to in tos.split(','):
                email_info["To"].append(to.strip())
        elif retr_line.startswith("Cc"):
            ccs = retr_line.split(":")[1].strip()
            for cc in ccs.split(','):
                email_info["CC"].append(cc.strip())
   
    count_emptyLine = 0
    count_file = 0
    #boundary = ""
    
    if "multipart" in retr_lines[0]:
        for retr_line in retr_lines:
            # Kiểm tra mail có file đính kèm hay không
            if retr_line.startswith("Content-Disposition"):
                disposition = retr_line.split(":")[1].strip()
                if "attachment" in disposition:
                    count_file += 1
                    email_info["has_attachment"] = True
                
            # Kiểm tra mail có nội dung hay không
            elif retr_line == '':
                count_emptyLine += 1
            if count_emptyLine == 2 and retr_line != '':
                email_info["Body"] += (retr_line + '\n')  
        
        email_info["Num_File"] = count_file
        return email_info

    else:
        for retr_line in retr_lines:
            if retr_line == '':
                count_emptyLine += 1
            if count_emptyLine == 1 and retr_line != '':
                email_info["Body"] += retr_line
        return email_info       
        
        # elif count_emptyLine == 4 and retr_line != '':
        #     email_info["Attachments"] += retr_line                
    
def save_mail_filtered(username, email_info, raw_email_data):
    # Lấy đường dẫn của chương trình
    program_address = os.getcwd()
    # Lọc folder tương ứng với mail
    folder = folder_sort(email_info)
    # Cấu hình lại file
    msg = '\n'.join(raw_email_data)

    # Folder chương trình/Folder người dùng/Folder lọc/File mail
    file_path = os.path.join(program_address, str(username), folder, email_info['msg'])
    with open(file_path, 'w') as f:
        f.write(msg)
            
def folder_sort(email_data):
    # Filters lưu trữ nội dung của file filter.json
    with open('filter.json', 'r') as f:
        filters = json.load(f)

    # Sau đó xét lần lượt các item trong data
    for filter_item in filters["filters"]:
        # Xét từng keyword trong item
        for keyword in filter_item["keywords"]:
            # nếu có keyword đó ở trong nội dung của email thì sẽ return lại tên folder tương ứng
            # có thể làm nhiều if để so sánh các cái trường với nhau
            if keyword in str(email_data):
                return filter_item["folder"]
    return "Inbox"


# CÁC HÀM XEM MAIL
def watch_mail_raw():#pop3_socket, response):
    while True:
        print('------------------------------------------------------------------')
        print("This is folder list in your mailbox: ")
        print("1. Inbox")
        print("2. Project")
        print("3. Important")
        print("4. Work")
        print("5. Spam")
        print("Press Enter to EXIT.")
        choice = input("Enter your choice: ")
        if choice == '':
            return
        elif choice == '1':
            ### BỔ SUNG HÀM CHECK XEM CÓ MAIL KHÔNG, NẾU KHÔNG THÌ THÔNG BÁO KHÔNG CÓ MAIL

            print('------------------------------------------------------------------')
            print("This is mail list in your Inbox folder: ")
            ### Hàm này sẽ in ra danh sách mail trong Inbox folder

            print("Enter to exit, enter 0 to back.")
            while True:
                print('------------------------------------------------------------------')
                mail_choice = input("Enter number of mail you want to watch: ")
                if mail_choice == '':
                    return
                elif mail_choice == '0':
                    break
                else:
                    print('------------------------------------------------------------------')
                    print("This is mail content: ")
                    ### Hàm này sẽ in ra nội dung mail

                    ### Hàm này sẽ cho biết mail này có file không

                    ## Nếu có file thì hỏi có muốn lưu file không
                    save_choice = input("This mail has attached file, Do you want to save this mail? (1. Yes, 2. No): ")
                    # Nếu có file và muốn lưu
                    if save_choice == '1':
                        path_attached_file = input("Enter the path you want to save: ")
                        ### Hàm này sẽ lưu file vào thư mục tương ứng

                        print("Mail saved!")
                    # Nếu có file nhưng không muốn lưu
                    else:
                        continue
        
        elif choice == '2':
            ### BỔ SUNG HÀM CHECK XEM CÓ MAIL KHÔNG, NẾU KHÔNG THÌ THÔNG BÁO KHÔNG CÓ MAIL

            print('------------------------------------------------------------------')
            print("This is mail list in your Project folder: ")
            ### Hàm này sẽ in ra danh sách mail trong Project folder

            print("Enter to exit, enter 0 to back.")
            while True:
                print('------------------------------------------------------------------')
                mail_choice = input("Enter number of mail you want to watch: ")
                if mail_choice == '':
                    return
                elif mail_choice == '0':
                    break
                else:
                    print('------------------------------------------------------------------')
                    print("This is mail content: ")
                    ### Hàm này sẽ in ra nội dung mail

                    ### Hàm này sẽ cho biết mail này có file không

                    ## Nếu có file thì hỏi có muốn lưu file không
                    save_choice = input("This mail has attached file, Do you want to save this mail? (1. Yes, 2. No): ")
                    # Nếu có file và muốn lưu
                    if save_choice == '1':
                        path_attached_file = input("Enter the path you want to save: ")
                        ### Hàm này sẽ lưu file vào thư mục tương ứng

                        print("Mail saved!")
                    # Nếu có file nhưng không muốn lưu
                    else:
                        continue
                    
        elif choice == '3':
            ### BỔ SUNG HÀM CHECK XEM CÓ MAIL KHÔNG, NẾU KHÔNG THÌ THÔNG BÁO KHÔNG CÓ MAIL

            print('------------------------------------------------------------------')
            print("This is mail list in your Important folder: ")
            ### Hàm này sẽ in ra danh sách mail trong Important folder

            print("Enter to exit, enter 0 to back.")
            while True:
                print('------------------------------------------------------------------')
                mail_choice = input("Enter number of mail you want to watch: ")
                if mail_choice == '':
                    return
                elif mail_choice == '0':
                    break
                else:
                    print('------------------------------------------------------------------')
                    print("This is mail content: ")
                    ### Hàm này sẽ in ra nội dung mail

                    ### Hàm này sẽ cho biết mail này có file không

                    ## Nếu có file thì hỏi có muốn lưu file không
                    save_choice = input("This mail has attached file, Do you want to save this mail? (1. Yes, 2. No): ")
                    # Nếu có file và muốn lưu
                    if save_choice == '1':
                        path_attached_file = input("Enter the path you want to save: ")
                        ### Hàm này sẽ lưu file vào thư mục tương ứng

                        print("Mail saved!")
                    # Nếu có file nhưng không muốn lưu
                    else:
                        continue
                    
        elif choice == '4':
            ### BỔ SUNG HÀM CHECK XEM CÓ MAIL KHÔNG, NẾU KHÔNG THÌ THÔNG BÁO KHÔNG CÓ MAIL

            print('------------------------------------------------------------------')
            print("This is mail list in your Work folder: ")
            ### Hàm này sẽ in ra danh sách mail trong Work folder

            print("Enter to exit, enter 0 to back.")
            while True:
                print('------------------------------------------------------------------')
                mail_choice = input("Enter number of mail you want to watch: ")
                if mail_choice == '':
                    return
                elif mail_choice == '0':
                    break
                else:
                    print('------------------------------------------------------------------')
                    print("This is mail content: ")
                    ### Hàm này sẽ in ra nội dung mail

                    ### Hàm này sẽ cho biết mail này có file không

                    ## Nếu có file thì hỏi có muốn lưu file không
                    save_choice = input("This mail has attached file, Do you want to save this mail? (1. Yes, 2. No): ")
                    # Nếu có file và muốn lưu
                    if save_choice == '1':
                        path_attached_file = input("Enter the path you want to save: ")
                        ### Hàm này sẽ lưu file vào thư mục tương ứng

                        print("Mail saved!")
                    # Nếu có file nhưng không muốn lưu
                    else:
                        continue
                    
        elif choice == '5':
            ### BỔ SUNG HÀM CHECK XEM CÓ MAIL KHÔNG, NẾU KHÔNG THÌ THÔNG BÁO KHÔNG CÓ MAIL

            print('------------------------------------------------------------------')
            print("This is mail list in your Spam folder: ")
            ### Hàm này sẽ in ra danh sách mail trong Spam folder

            print("Enter to exit, enter 0 to back.")
            while True:
                print('------------------------------------------------------------------')
                mail_choice = input("Enter number of mail you want to watch: ")
                if mail_choice == '':
                    return
                elif mail_choice == '0':
                    break
                else:
                    print('------------------------------------------------------------------')
                    print("This is mail content: ")
                    ### Hàm này sẽ in ra nội dung mail

                    ### Hàm này sẽ cho biết mail này có file không

                    ## Nếu có file thì hỏi có muốn lưu file không
                    save_choice = input("This mail has attached file, Do you want to save this mail? (1. Yes, 2. No): ")
                    # Nếu có file và muốn lưu
                    if save_choice == '1':
                        path_attached_file = input("Enter the path you want to save: ")
                        ### Hàm này sẽ lưu file vào thư mục tương ứng

                        print("Mail saved!")
                    # Nếu có file nhưng không muốn lưu
                    else:
                        continue
                 
        else:
            print('------------------------------------------------------------------')
            print("Invalid choice! Please try again!")
            continue

def watch_mail(email_address):#pop3_socket, response):
    # Lấy đường dẫn chương trình
    program_address = os.getcwd()
    user_path = os.path.join(program_address, email_address)
    
    while True:
        # List ra các folder phân loại mail
        print('------------------------------------------------------------------')
        print("This is folder list in your mailbox: ")
        folders = ["Inbox", "Spam", "Project", "Important", "Work"]
        for i, folder in enumerate(folders, start=1):
            print(f"{i}. {folder}")
        # Chọn xem folder nào   
        folder_choice = input("Enter folder number to view emails (or press Enter to EXIT): ")

        # EXIT
        if folder_choice == '':
            return    
        # List ra các email trong folder đó
        elif folder_choice.isdigit() and 1 <= int(folder_choice) <= len(folders):
            # Lấy tên folder được chọn
            selected_folder = folders[int(folder_choice) - 1]
            # Lấy đường dẫn folder được chọn
            folder_path = os.path.join(user_path, selected_folder)
            while True:
                # Lấy các email trong folder được chọn
                selected_emails = os.listdir(folder_path)

                # List ra các email trong folder được chọn
                print('------------------------------------------------------------------')
                print(f"This is mail list in your {selected_folder} folder: ")
                
                if selected_emails is None:
                    print("---No mail in this folder---")
                    break
                else:
                    # List từng email
                    for i, email in enumerate(selected_emails, start=1):
                        email_data = getEmail_Data(email, email_address)
                        email_from = email_data["From"]
                        email_subject = email_data["Subject"]
                        email_status = email_data["Status"]
                        if email_status == "Unread":
                            print(f"{i}. ({email_status}) <{email_from}>, <{email_subject}>")
                        else:
                            print(f"{i}. <{email_from}>, <{email_subject}>")
            
                    print('------------------------------------------------------------------')
                    print("Enter 0 to back or press Enter to EXIT.")
                    email_choice = input("Enter email number to view details: ")

                    # EXIT
                    if email_choice == '':
                        return
                    # BACK
                    elif email_choice == '0':
                        break
                    elif email_choice.isdigit() and 1 <= int(email_choice):
                        msg = selected_emails[int(email_choice)-1]
                        file_path = os.path.join(folder_path, msg)
                        
                        #Lấy Body và attachment (nếu có) của mail
                        data  = getEmailBody_Attachments(file_path) #email_datas["has_attachment"][int(input) - 1])

                        with open('uidl.json', 'r') as f:
                            data2 = json.load(f)
                        for email_data in data2[email_address]:
                            if msg == email_data["msg"]:
                                print("From:", email_data["From"])
                                print("To: ", email_data["To"])
                                print("CC: ", email_data["CC"])
                                print("Subject:", email_data["Subject"])
                                print("\n", data["Body"])
                        # if email_datas["has_attachment"] == True:
                        #     att_choice = input("There an attachment, do you want to download?")
                        # Cập nhật lại status của mail trong file uidl.json
                                changeMailStatus(email_address, email_data["msg"])
                    else:
                        print('------------------------------------------------------------------')
                        print("Invalid choice! Please try again!")
                        continue
        else:
            print('------------------------------------------------------------------')
            print("Invalid choice! Please try again!")
            continue

def getEmail_Data(msgfileName, email_address):
    program_path = os.getcwd()

    with open ("uidl.json", 'r') as f:
        data = json.load(f)
    email_datas = data[email_address]

    for email_data in email_datas:
        if (str(msgfileName) == email_data["msg"]):
            return email_data               
      
def changeMailStatus(email_address, msg):
    with open ('uidl.json', 'r') as file:
        data = json.load(file)

    for info in data[email_address]:
        if info["msg"] ==  msg:
            info["Status"] = ''
            break
    
    with open('uidl.json', 'w') as file2:
        json.dump(data, file2, indent=2)
 
def getEmailBody_Attachments(file_path):
    data = {
        "Body": '',
        "Attachments": []
    }

    with open(file_path, 'r', encoding='latin1') as file:
        file_content = file.read()
        
        # Đếm dòng trống để xác định phần body và attachments
        count_emptyLine = 0
        for line in file_content.split('\n'):
            if line == '':
                count_emptyLine += 1
            if count_emptyLine == 2 and line != '':
                data["Body"] += line
    return data

def printEmail(email):
    pass
  
### ------------------------------------------------------x---    
def load_filters():
    program_address = os.getcwd()
    filter_file_path = os.path.join(program_address, 'Filter.json')

    # Kiểm tra xem tệp Filter.json có tồn tại không
    if not os.path.exists(filter_file_path):
        print("Filter.json not found. Please create the file.")
        return {}

    with open(filter_file_path, 'r') as file:
        data = json.load(file)
    return data

def save_email(folder, email, username):
    program_address = os.getcwd()

    file_name = f"(chưa đọc) {email['from_']} {email['subject']}.txt"
    file_path = os.path.join(folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"From: {email['from_']}\n")
        file.write(f"To: {email['to']}\n")
        file.write(f"Subject: {email['subject']}\n")
        file.write(f"Body:\n{email['body']}\n")
### ------------------------------------------------------x---
 

# HÀM AUTO LOAD MAIL SAU THỜI GIAN NHẤT ĐINH CHO TRƯỚC
def auto_load_mail(user_info, server_info):
    global exit_flag
    while not exit_flag:
        receive_mail(user_info, server_info)
        time.sleep(server_info["AutoLoad"])

def extract_EmailAddress(username):
    # Kiểm tra và tạo thư mục cho người dùng
    # r là tiền tố để xử lý ký tự đặc biệt mà không xóa chúng
    # r'<([^>]+)>' có nghĩa là đọc chuỗi trong dấu < và >
    match = re.search(r'<([^>]+)>', username)
    # Số 1 có nghĩa là nó trả về chuỗi khớp đầu tiên
    # Nếu thay bằng 0 thì nó sẽ trả về toàn bộ chuỗi
    # Nếu để trống thì nó sẽ tự thay 0 nếu không tìm thấy và 1 nếu tìm thấy
    email_address = match.group(1)
    
    return email_address
    

if __name__ == "__main__":
    user_info = login()
    if user_info["Username"] != "0" and user_info["Password"] != "0":
        email_address = extract_EmailAddress(user_info["Username"])
        folder_isExist(email_address)
        server_info = get_server_info(user_info)
        # receive_mail(user_info, server_info)
        main_thread = threading.Thread(target=main,args=(user_info, server_info))
        auto_thread = threading.Thread(target=auto_load_mail,args=(user_info, server_info))
        main_thread.start()
        auto_thread.start()
        main_thread.join()
    else:
        print("Login failed!")
        
    
# def parse_email(data, spliter):
#       lines = data.split(spliter)
#       boundary = ""
#       message_id = ""
#       date = ""
#       tos = []
#       ccs = []
#       _from = ""
#       subject = ""
#       attachment_arr = []
#       content = ""
#       start_idx_attach = -1

#       for i in range(0, len(lines)):
#       # Lấy boundary
#         if (lines[i].find("Content-Type: multipart/mixed") != -1):
#           boundary = lines[0][lines[0].find('"') + 1:len(lines[0]) - 1]
          
#       # Lấy thông tin
#         elif lines[i].startswith("Message-ID"): message_id = lines[i].split(": ", 1)[1]
#         elif lines[i].startswith("Date"): date = lines[i].split(": ", 1)[1]
#         # Lấy nhiều to
#         elif lines[i].startswith("To"): 
#           to = lines[i].split(": ", 1)[1]
#           tos = to.split(',')
#         # Lấy nhiều cc
#         elif lines[i].startswith("Cc"): 
#           cc = lines[i].split(": ", 1)[1]
#           ccs = cc.split(',')
#         elif lines[i].startswith("From"): _from = lines[i].split(": ", 1)[1]
#         # ??? Lấy subject
#         elif lines[i].startswith("Subject"): 
#           subject = (lines[i].split(": ", 1)[1]).strip()
#           subject = base64.b64decode(subject).decode("utf8")
        
#         # ??? Lấy content
#         if subject != '' and lines[i] == '':
#           start_idx_attach = i
#           break
      
      
#       if (boundary == ""):
#         for i in range(start_idx_attach, len(lines)):
#           content = content + lines[i] + '\n'
#         content = content[1:content.rfind('.') - 2]
#         content = base64.b64decode(content).decode("utf8")
#         return {"ID": message_id, "Date": date, "To": tos, "Cc": ccs, "From": _from, "Subject": subject, "Content": content}

#       else:
#         for j in range(start_idx_attach, len(lines), 1):
#           if lines[j].startswith("Content-Transfer-Encoding: 7bit"):
#             for k in range(j + 2, len(lines)):
#               if boundary in lines[k]:
#                 break
#               content = content + lines[k]
#               content = base64.b64decode(content).decode("utf8")
#           elif lines[j].startswith("Content-Disposition: attachment"):
#             attachment_data = ""
#             file_name = ""
#             if (lines[j].find("filename") != -1):
#               file_name = lines[j][lines[j].find('"') + 1:len(lines[j]) - 1]
#             else:
#               file_name = lines[j + 1][lines[j + 1].find('"') + 1:len(lines[j + 1])- 1]
#             file_name = base64.b64decode(file_name).decode("utf8")
#             for k in range(j + 2, len(lines)):
#               if boundary in lines[k]:
#                 break
#               attachment_data = attachment_data + lines[k]
#             attachment_data.strip()
#             attachment = {"name": file_name, "data": attachment_data}
#             attachment_arr.append(attachment)
#         return {"ID": message_id, "Date": date, "To": tos, "Cc": ccs, "From": _from, "Subject": subject, "Content": content, "Attachment": attachment_arr}
