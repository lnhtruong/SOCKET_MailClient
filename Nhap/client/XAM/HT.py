import socket as sk
import json
import re
import time
import uuid
import base64
import os

from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


#-------------------------HÀM MAIN-------------------------#
def main():
    email_config = load_data_from_fileconfig('GeneralFileConfig.json')
        
    # Nhập tên và mật khẩu để đăng nhập
    print("Please input username and password to login to your account!")
    
    # Lặp đến khi nào nhập đúng username với password để dùng lệnh break thì thôi
    while True:
        username = input("Username (Mail): ")
        password = input("Password: ")
                
        if username == extract_email(email_config["username"]) and password == email_config["password"]:
            break
        else:
            print("Your username or password is wrong!")
        print('------------------------------------------------------------------')
    
    print('LOG IN SUCCESSFULLY!')
    
    # CHOICE.
    print("Options Menu:")
    print("1. Send Mail.")
    print("2. View List Of Mail.")
    print("3. Exit.")
    choice = input("Your choice is: ")
    
    # SEND EMAIL.
    if choice == "1":
        # Khai báo thông tin server SMTP bao gồm địa chỉ HOST và số PORT
        HOST = "127.0.0.1" # Địa chỉ loopback: tức là nó sẽ trả về địa chỉ của máy
        PORT = 2225 # Số port của phương thức SMTP
        
        # Khởi tạo Socket Gửi
        s = sk.socket()
        server_address = (HOST, PORT) # Kiểu dữ liệu tuple dùng để lưu trữ các đối tượng không thay đổi về sau
        s.connect(server_address) # Tạo kết nối server
        
        # Dùng khối try để gửi mail
        try:
            # Nó nhận thông điệp chào đón từ server
            # Vì khi kết nối được thì server thường gửi thông điệp về để cho client biết
            welcome_message = s.recv(1024)
            
            send_mail(s, email_config)
            
        # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
        # Thông tin lỗi sẽ lưu vào biến e
        except Exception as e:
            s.close() # Đóng kết nối socket để tránh rò rỉ kết nối
            print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
            print("Disconnected from SERVER!")

    # RECIEVE EMAIL.
    elif choice == "2":
        folder_isExist()
        
        # Khai báo thông tin server POP3 bao gồm địa chỉ HOST và số PORT1
        HOST = "127.0.0.1" # Địa chỉ loopback: tức là nó sẽ trả về địa chỉ của máy
        PORT1 = 3335 # Số port của phương thức POP3

        # Khởi tạo Socket Nhận
        s1 = sk.socket()
        server_address = (HOST, PORT1)  # Kiểu dữ liệu tuple dùng để lưu trữ các đối tượng không thay đổi về sau
        s1.connect(server_address) # Tạo kết nối server
        
        # Dùng khối try để nhận mail
        try:
            # Nó nhận thông điệp chào đón từ server
            # Vì khi kết nối được thì server thường gửi thông điệp về để cho client biết
            welcome_message = s1.recv(1024)
            
            # Chạy hàm gửi mail với s1 là socket còn lại là thông tin tài khoản
            receive_mail(s1,username,password)
            
        # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
        # Thông tin lỗi sẽ lưu vào biến e
        except Exception as e:
            s1.close() # Đóng kết nối socket để tránh rò rỉ kết nối
            print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
            print("Disconnected from SERVER!")
    
    # EXIT.
    elif choice == "3":
        print("EXIT SUCCESSFULLY!")
        pass # Bỏ qua lệnh else phía dưới
    
    # WRONG CHOICE
    else:
        print("Your choice is invalid!")

#-------------------------HÀM LOAD DATA FROM FILECONFIG-------------------------#
def load_data_from_fileconfig(file_name):
    with open(file_name) as config_file:
        config = json.load(config_file)
    return config["email"]

#-------------------------HÀM GIẢI NÉN TRƯỜNG EMAIL-------------------------#
def extract_email(input_string):
    email_pattern = r'<([^>]+)>' 
    
    match = re.search(email_pattern, input_string)
    if match:
        return match.group(1)
    else:
        return None

#-------------------------HÀM GỬI MAIL-------------------------#
def send_mail(s, email_config):
    msg = MIMEMultipart()
    # REQUEST TO CONNECT
    message = 'EHLO [{}] \r\n'.format("127.0.0.1").encode()
    s.send(message)
    response = s.recv(1024)

    # MAIL FROM
    mail_add = extract_email(email_config["username"])
    mail_from = 'MAIL FROM:<{}> \r\n'.format(mail_add).encode()
    s.send(mail_from)
    response = s.recv(1024)

    # RCPT TO
    mail_to = input('RCPT TO: ')
    rcpt_to = 'RCPT TO:<{}> \r\n'.format(mail_to).encode()
    s.send(rcpt_to)
    response = s.recv(1024)
    
    # REQUEST TO INPUT DATA
    s.sendall(b'DATA\r\n')
    response = s.recv(1024)
    
    # START TO INPUT DATA
    subject = input("Subject: ")
    content = input("Content: ")
    unique_id = uuid.uuid4()
    named_tuple = time.localtime()
    local_time = time.strftime("%a, %d %b %Y %H:%M:%S", named_tuple)
    
    message = f"""Message ID: <{unique_id}@gmail.com>
Date: {local_time} +0700
MIME-Version: 1.0 
User-Agent: Mozilla Thunderbird
Content-Language: vi-x-KieuCu.[Chuan]
To: Toi <{mail_to}>
From: Tu <{mail_add}>
Subject: {subject}

{content}
            
"""
    email_info = f'{message}\r\n'
    msg.attach(MIMEText(email_info,"plain"))
    choice = input("Co gui file dinh kem (1. Co, 2. Khong): ")
    if choice == '1':
        num = int(input("Gui bao nhieu file: "))
        max_size = 3 * 1024 * 1024 #3MB
        for i in range(num):
            path = input(f"Nhap duong dan file thu {i+1}: ")
            file_size = os.path.getsize(path)
            if file_size > max_size:
                print(f"Tệp đính kèm quá dung lượng. Dung lượng hiện tại: {file_size} bytes, Dung lượng tối đa cho phép: {max_size} bytes")
            else:
                print("Dung lượng tệp đính kèm hợp lệ.")
                attachment(path,msg)
                max_size = max_size - file_size
    s.sendall(f'{msg.as_string()}\r\n.\r\n'.encode())
    response = s.recv(1024)
    print(response.decode())
    print("SEND SUCCESSFULLY!")
    print('------------------------------------------------------------------')

#-------------------------HÀM NHẬN MAIL-------------------------#
def receive_mail(s1, username, password):
    # SEND CAPA.
    s1.send(b'CAPA\r\n')
    response = s1.recv(1024).decode() 

    # SEND USER.
    s1.send(f'USER {username}\r\n'.encode())
    response = s1.recv(1024).decode()

    # SEND PASSWORD.
    s1.send(f'PASS {password}\r\n'.encode())
    response = s1.recv(1024).decode()

    # SEND STAT.
    s1.send(b'STAT\r\n')
    response = s1.recv(1024).decode()
    num_of_mail = response[4]
    # Print number of mail in the mail box.
    print(f"Total of mail is: {num_of_mail}")

    # SEND LIST.
    s1.send(b'LIST\r\n')
    response = s1.recv(1024).decode()

    # SEND UIDL.
    s1.send(b'UIDL\r\n')
    response = s1.recv(1024).decode()
    # SEND RETR.
    choose = input("Input file number which you want to open: ")
    s1.send('RETR {}\r\n'.format(choose).encode())
    response = s1.recv(int(1e10)).decode()
    if 'Content-Disposition: attachment' in response:
    # Get the boundary string for parsing multipart content
        boundary = response.split('\r\n--')[1].split('==\r\n')[0]

    # Split the response into parts using the boundary
        parts = response.split(boundary)[1:]

    # Create a directory to store attachments
        attachment_dir = os.path.join(os.getcwd(), 'Attachments')
        os.makedirs(attachment_dir, exist_ok=True)

    # Iterate over the parts and look for attachments
        for part in parts:
            if 'Content-Disposition: attachment' in part:
                content_type = part.split('filename=')[1].split('\r\n')[0]
                attachment_data = part.split(f'{content_type}')[1].split('\r\n--')[0].strip()
                save_attachment(attachment_data, attachment_dir, content_type)

    list_info_mail = response.splitlines()[1:]
    for item in list_info_mail:
        print(item)

    # SEND QUIT.
    s1.send(b'QUIT\r\n')
    response = s1.recv(1024).decode()

    # PRINT NOTIFICATION.
    print('OPEN SUCCESSFULLY!')
    print('------------------------------------------------------------------')
    
#-------------------------HÀM ...-------------------------#
# The function check the folder exist or not.
def folder_isExist():
    folder_address = os.getcwd()
    list_file_folder = os.listdir(folder_address)
    if "Project" not in list_file_folder:
        os.makedirs("Project")
    if "Attachments" not in list_file_folder:
        os.makedirs("Attachments")
    if "Important" not in list_file_folder:
        os.makedirs("Important")
    if "Work" not in list_file_folder:
        os.makedirs("Work")
    if "Spam" not in list_file_folder:
        os.makedirs("Spam")
    if "Inbox" not in list_file_folder:
        os.makedirs("Inbox")

#-------------------------HÀM ...-------------------------#
def attachment(path,msg):
    file_name = basename(path)
    with open(path, 'rb') as attachment:
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload(attachment.read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', 'attachment; filename=' + file_name)
        msg.attach(attachment_package)

#-------------------------HÀM ...-------------------------#
def save_attachment(attachment_data, attachment_dir, content_type): 
    attachment_path = os.path.join(attachment_dir, content_type)
    with open(attachment_path, 'wb') as attachment_file:
        attachment_file.write(base64.b64decode(attachment_data))
    attachment_file.close()
    print(f"Attachment saved: {attachment_path}")

#-------------------------HÀM ...-------------------------#
if __name__ == "__main__":
    main()
    # Load data of General Config File.
   
 
