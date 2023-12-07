import socket
# Mã hóa và giải mã dữ liệu nhị phân theo định dạng base64
# import base64
# Cung cấp tương tác với hệ diều hành (Dùng trong thao tác tệp tin)
import os
# Cung cấp phương thức thao tác file json
import json
# Thư viện Regular Expressions (biểu thức chính quy)
# Ví dụ: tìm, so, xử lý chuỗi,...
import re
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
FORMAT = 'utf-8'

filter_content = []


# HÀM MAIN
def main():
# Khởi tạo và nhập thông tin người dùng
    username = input("Enter username: ")
    email_address = input("Enter email address: ")
    user_info = {'Username': username + " <" + email_address + ">",
                 'Password': input("Enter password: "),
                 'MailServer': '127.0.0.1',
                 'SMTP': 2225,
                 'POP3': 3335,
                 'Auto': 10
                 }

# Kiểm tra tài khoảng người dùng
    check_account(user_info)
    if user_info['Password'] == '0':
        return

    HOST = user_info['MailServer']
    PORT_SMTP = user_info['SMTP']
    PORT_POP3 = user_info['POP3']

    # Kiểm tra và tạo thư mục cho người dùng
    # r là tiền tố để xử lý ký tự đặc biệt mà không xóa chúng
    # r'<([^>]+)>' có nghĩa là đọc chuỗi trong dấu < và >
    match = re.search(r'<([^>]+)>', user_info['Username'])
    # Số 1 có nghĩa là nó trả về chuỗi khớp đầu tiên
    # Nếu thay bằng 0 thì nó sẽ trả về toàn bộ chuỗi
    # Nếu để trống thì nó sẽ tự thay 0 nếu không tìm thấy và 1 nếu tìm thấy
    email_address = match.group(1)
    folder_isExist(email_address)

# Bắt đầu giao diện người dùng
    while True:
        print("Menu:")
        print("1. Send mail")
        print("2. View a list of received emails")
        print("3. Exit")
        choice = input("Enter your choice: ")

    # GỬI MAIL
        if choice == '1':
            # Mở kết nối socket
            smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            smtp_socket.connect((HOST, PORT_SMTP))

            # Dùng khối try để gửi mail
            try:
                # Nhận thông tin lời chào từ server
                welcome_message = smtp_socket.recv(1024).decode()

                print("Đây là thông tin soạn mail: (nếu không điền vui lòng nhấn enter để bỏ qua)")
                # Kiểu gửi TO và CC
                to = input('TO: ')
                cc = input('CC: ')
                bcc = input('BCC: ')
                # Nội dung mail
                subject = input("Subject: ")
                content = input("Content: ")
                send_mail(smtp_socket, user_info, to, subject, content, cc, bcc)
                print("SEND SUCCESSFULLY!")
                print('------------------------------------------------------------------')
            # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
            # Thông tin lỗi sẽ lưu vào biến e
            except Exception as e:
                smtp_socket.close() # Đóng kết nối socket để tránh rò rỉ kết nối
                print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
                print("Disconnected from SERVER!")
                return

    # XEM MAIL
        elif choice == '2':
            # Mở kết nối socket
            pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pop3_socket.connect((HOST, PORT_POP3))

            # Dùng khối try để nhận mail
            try:
                # Nhận thông tin lời chào từ server
                welcome_message = pop3_socket.recv(1024).decode()

                # receive_mail(pop3_socket, user_info) # Trong lúc mà có người gửi thì vẫn nhận tiếp được
                watch_mail()

                # Đóng kết nối socket
                pop3_socket.send(b'QUIT\r\n')
                pop3_socket.close()
                print('------------------------------------------------------------------')
            # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
            # Thông tin lỗi sẽ lưu vào biến e
            except Exception as e:
                pop3_socket.close() # Đóng kết nối socket để tránh rò rỉ kết nối
                print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
                print("Disconnected from SERVER!")
                return

    # THOÁT
        elif choice == '3':
            print("Exiting program...")
            return

    # NHẬP SAI
        else:
            print("Invalid choice! Please try again!")
            print('------------------------------------------------------------------')
            continue
            

# CÁC HÀM ĐĂNG NHẬP
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
                        user_info['Password'] = input("Enter password again (Enter 0 to exit): ")
                        if user_info['Password'] == '0':
                            return True
            else:
                print("Wrong username!", end=' - ')
                user_info['Username'] = input("Just enter username again (Enter 0 to exit): ")
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
        
    # Tạo file uidl.json cho chương trình nếu chưa có
    if "uidl.json" not in list_file_folder:
        with open('uidl.json', 'w') as f:
            uidl_content = {
                username: [
                    {"STT": 0,
                    "Code": "Example",
                    "Status": "Unread",
                    "From": "",
                    "Subject": "",
                    "Date": "",
                    "To": "",
                    "CC": "",
                    "BCC": "",
                    "Body": "",
                    "has_attachment": False,
                    "Attachments": ""
                    }
                ]
            }
            json.dump(uidl_content, f, indent=2)
    else:
        with open('uidl.json', 'r') as f:
            data = json.load(f)
        if username not in data:
            uidl_content = {
                username: [
                    {"STT": 0,
                    "Code": "Example",
                    "Status": "Unread",
                    "From": "",
                    "Subject": "",
                    "Date": "",
                    "To": "",
                    "CC": "",
                    "BCC": "",
                    "Body": [],
                    "has_attachment": False,
                    "Attachments": []
                    }
                ]
            }
            data.update(uidl_content)
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


# CÁC HÀM GỬI MAIL
def send_mail(smtp_socket, user_info, to, subject, content, cc=None, bcc=None):
    try:
        msg = MIMEMultipart()
        # Gửi lệnh EHLO để bắt đầu
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
        # language, confidence = langid.classify(content)
        # msg['Content-Language'] = language
        if bcc.strip() and not to.strip() and not cc.strip():
            msg['To'] = 'undisclosed-recipients: ;'
        else:
            if to.strip():
                msg['To'] = ", ".join(to_addresses)
            if cc.strip():
                msg['Cc'] = ",".join(cc_addresses)

        msg['From'] = user_info["Username"]
        msg['Subject'] = subject

        # text/plain: Chỉ định nội dung văn bản của email không chứa định dạng đặc biệt
        body = MIMEText(content + '\r\n', 'plain')
        body.replace_header('Content-Type', 'text/plain; charset=UTF-8; format=flowed')
        # Xóa dòng MIME-Version
        del body['MIME-Version']
        msg.attach(body)

        # Thêm file đính kèm
        choice = input("Do you want to attach files? (1. Yes, 2. No): ")
        if choice == '1':
            MAX_SIZE = 3 * 1024 * 1024
            remain_size = MAX_SIZE
            num = int(input("Number of files: "))

            for i in range(num):
                while True:
                    path = input(f"Enter path for file {i + 1}: ")
                    # Kiểm tra xem tệp có tồn tại và có thể mở được hay không
                    try:
                        file_size = os.path.getsize(path)
                        with open(path, 'rb') as file:
                            pass  # Nếu không có lỗi, tệp có thể mở được

                        if file_size > remain_size:
                            print(
                                f"Attached file exceeds remaining maximum size. Current size: {file_size} bytes, "
                                f"Remaining maximum allowed size: {remain_size} bytes")
                            print("Please try again.")
                        else:
                            send_file(path, msg)
                            remain_size -= file_size
                            break

                    except FileNotFoundError:
                        print(f"File not found: {path}. Please enter a valid file path.")
                    except IOError as e:
                        print(f"Error opening file {path}: {e}")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")

        smtp_socket.sendall(f'{msg.as_string()}.\r\n'.encode(FORMAT))
        smtp_socket.recv(1024)

    finally:
        pass
    
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
def receive_mail(pop3_socket, user_info):
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
    response = pop3_socket.recv(1024).decode()
    
    num_mail = response[4] # Lấy x trong +OK x y
    
    # SEND LIST
    pop3_socket.send(b'LIST\r\n')
    ## TRẢ VỀ: 
    # +OK
    # Thứ tự mail _ size mail
    # .
    response = pop3_socket.recv(2048).decode()

    # SEND UIDL
    pop3_socket.send(b'UIDL\r\n')
    ## TRẢ VỀ: 
    # +OK
    # Thứ tự mail _ <mã độc nhất>.msg
    # .
    response = pop3_socket.recv(int(1e10)).decode()
    
    download_mail(pop3_socket, response, email_address)
    
def download_mail(pop3_socket, response, email_address):            
    # Lấy các dòng phản hồi UIDL từ server
    uidl_lines = response.split('\r\n')
    
    # Đọc các dòng UIDL trừ dòng đầu (+OK) và dòng cuối (.)
    for uidl_line in uidl_lines[1:-2]:
        with open('uidl.json', 'r') as f:
            data = json.load(f)
            check = False
            for email_info in data[str(email_address)]:
                if str(email_info["Code"]) == str(uidl_line[2:]):
                    check = True
                    break
            if check == False:
                pop3_socket.send('RETR {}\r\n'.format(uidl_line[0]).encode())  
                response = pop3_socket.recv(int(1e10)).decode()
                retr_lines = response.split('\r\n')
                email_data = parse_email(retr_lines, uidl_line)
                save_mail_filtered(email_data, response)
                with open('uidl.json', 'r') as f:
                    data = json.load(f)
                    data[str(email_address)].append(email_data)
                with open('uidl.json', 'w') as f:
                    json.dump(data, f, indent=2)

def parse_email(retr_lines, uidl_line):
    email = {
        "STT": int(uidl_line[0]),
        "Code": str(uidl_line[2:]),
        "Status": "Unread",
        "From": "",
        "Subject": "",
        "Date": "",
        "To": "",
        "CC": "",
        "BCC": "",
        "Body": "",
        "has_attachment": False,
        "Attachments": ""
    }
    
    count_emptyLine = 0

    for retr_line in retr_lines:        
        if retr_line.startswith("From"):
            email["From"] = retr_line.split(":")[1].strip()
        
        elif retr_line.startswith("Subject"):
            email["Subject"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("Date"):
            email["Date"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("To"):
            email["To"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("CC"):
            email["CC"] = retr_line.split(":")[1].strip()
        elif retr_line.startswith("BCC"):
            email["BCC"] = retr_line.split(":")[1].strip()
            
        # Kiểm tra mail có file đính kèm hay không
        elif retr_line.startswith("Content-Disposition"):
            disposition = retr_line.split(":")[1].strip()
            if "attachment" in disposition:
                email["has_attachment"] = True
                
        # Kiểm tra mail có nội dung hay không
        elif retr_line == '':
            count_emptyLine += 1
        if count_emptyLine == 2 and retr_line != '':
            email["Body"] += retr_line
        # elif count_emptyLine == 4 and retr_line != '':
        #     email["Attachments"] += retr_line                
    
    return email

def save_mail_filtered(email_data, raw_email_data):
    pass

def watch_mail():#pop3_socket, response):
    while True:
        print('------------------------------------------------------------------')
        print("This is folder list in your mailbox: ")
        print("1. Inbox")
        print("2. Project")
        print("3. Important")
        print("4. Work")
        print("5. Spam")
        print("Enter to exit.")
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
            print("Invalid choice! Please try again!")
            print('------------------------------------------------------------------')
            continue

  
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

def folder_sort(mail_data):
    filters = filter_content
    for email_filter in filters:
        for keyword in email_filter["keywords"]:
            if keyword in mail_data:
                return email_filter["folder"]
    return "Inbox"

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
def auto_load_mail():
    pass    


if __name__ == "__main__":
    main()