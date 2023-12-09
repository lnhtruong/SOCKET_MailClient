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



def main():
    # email_config = load_data_from_fileconfig('GeneralFileConfig.json')
        
    #     # Input user and password.
    # print("Please input username and password to login to your account!")
    # while True:
    #     username = input("Username (Mail): ")
    #     password = input("Password: ")
    #     if username == extract_email(email_config["username"]) and password == email_config["password"]:
    #         break
    #     else:
    #         print("Your username or password is wrong!")
    #     print('------------------------------------------------------------------')
    
    # print('LOG IN SUCCESSFULLY!')
    email_config = {"username" : "",
                    "password" : ""
                    }
    email_config["username"] = "ahihi.gioi@gmail.com"
    email_config["password"] = ""
    username = "ahihi.gioi@gmail.com"
    password = ""
    
    # Activity.
    print("Options Menu:")
    print("1. Send Mail.")
    print("2. View List Of Mail.")
    print("3. Exit.")
    choice = input("Your choice is: ")
    
    # SEND EMAIL.
    if choice == "1":
        # Declare the information of Server.
        HOST = "127.0.0.1"
        PORT = 2225
        # Create Socket.
        s = sk.socket()
        server_address = (HOST, PORT)
        s.connect(server_address)
        try:
            welcome_message = s.recv(1024)
            send_mail(s, email_config)
        except Exception as e:
            s.close()
            print(f"Error: {e}")
            print("Disconnected from SERVER!")
    # RECIEVE EMAIL.
    elif choice == "2":
        folder_isExist()
        # Declare the information of Server.
        HOST = "127.0.0.1"
        PORT2 = 3335
        # Create Socket.
        s1 = sk.socket()
        server_address = (HOST, PORT2)
        s1.connect(server_address)
        try:
            welcome_message = s1.recv(1024)
            receive_mail(s1,username,password)
        except Exception as e:
            s1.close()
            print(f"Error: {e}")
            print("Disconnected from SERVER!")
    
    # EXIT.
    elif choice == "3":
        print("EXIT SUCCESSFULLY!")
        pass
    else:
        print("Your choice is invalid!")

# The function take the data from Config File.
def load_data_from_fileconfig(file_name):
    # Open File Config.
    with open(file_name) as config_file:
        config = json.load(config_file)
    return config["email"]
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

# The function extract the user to take the mail address.
def extract_email(input_string):
    email_pattern = r'<([^>]+)>'
    match = re.search(email_pattern, input_string)
    if match:
        return match.group(1)
    else:
        return None

# The function send mail.
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
        print(boundary)

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

def attachment(path,msg):
    file_name = basename(path)
    with open(path, 'rb') as attachment:
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload(attachment.read())
        encoders.encode_base64(attachment_package)
        attachment_package.add_header('Content-Disposition', 'attachment; filename=' + file_name)
        msg.attach(attachment_package)


def save_attachment(attachment_data, attachment_dir, content_type): 
    attachment_path = os.path.join(attachment_dir, content_type)
    with open(attachment_path, 'wb') as attachment_file:
        attachment_file.write(base64.b64decode(attachment_data))
    attachment_file.close()
    print(f"Attachment saved: {attachment_path}")

if __name__ == "__main__":
    main()
    # Load data of General Config File.
   
 



# # Khai báo thư viện socket rồi gán vào biến sk
# #--------------------------------------------------#
# from msilib.schema import File
# import socket as sk
# from sre_parse import parse_template
# from tkinter.messagebox import RETRY
# from urllib import response
# '''
# - Hàm <tên biến> = sk.socket() : Khởi tạo socket
# - Hàm <tên biến>.connect(địa chỉ server) : tạo kết nối socket 
# - Hàm <tên biến>.send(Nội dung) : gửi nội dung cho socket '''

# # Thư viện hỗ trợ file config kiểu đuổi json
# #--------------------------------------------------#
# import json
# '''
# ...'''

# # Thư viện Regular Expressions (biểu thức chính quy)
# # Ví dụ: tìm, so, xử lý chuỗi,...
# #--------------------------------------------------#
# import re
# '''
# - Tiền tố r : xử lý ký tự đặc biệt
# - Hàm re.search(biến lưu tiền tố r, chuỗi ký tự)  : trả về sự khớp đầu tiên
# - Hàm re.findall(biến lưu tiền tố r, chuỗi ký tự) : trả về tất cả sự khớp '''

# # ???
# #--------------------------------------------------#
# import time
# '''
# ...'''

# # ???
# #--------------------------------------------------#
# import uuid
# '''
# ...'''

# # Thư viện để hỗ trợ kiểu dữ liệu base64
# #--------------------------------------------------#
# import base64
# '''
# ...'''

# # Thư viện Operating System (thao tác với hệ điều hành)
# # Ví dụ: quản lý thư mục, đường dẫn, tạo/xóa file, thực hiện các lệnh hệ thống,...
# #--------------------------------------------------#
# import os
# '''
# - os.getcwd(): Trả về đường dẫn thư mục làm việc hiện tại.'''

# # Các khai báo liên quan đến thư viện "email" - hỗ trợ thao tác với email
# #--------------------------------------------------#
# #--------------------------------------------------#
# from os.path import basename
# # os.path : 1 module của os cung cấp các hàm liên quan đến đường dẫn file và thư mục
# # Hàm basename : lấy tên file từ một đường dẫn file
# #--------------------------------------------------#
# from email.mime.multipart import MIMEMultipart
# # email.mime.multipart : 1 module cung cấp lớp và hàm xử lý phần multipart
# # MIMEMultipart : 1 lớp tạo và biểu diễn multipart
# #-------------------------MULTIPART CỦA EMAIL-------------------------#
# '''
# - Phần Boundary (biên giới) : giá trị đặc biệt dùng để tạo ranh giới giữa các phần
# - Phần Text (Văn bản): Đây là phần chứa nội dung văn bản của email
# - Phần HTML (nếu có): Nếu email có cả nội dung HTML, phần này chứa đoạn mã HTML
# - Phần Đính Kèm (Attachments): Nếu có tệp tin, hình ảnh, hoặc bất kỳ đính kèm nào khác, chúng được đặt trong phần này.
# '''
# #--------------------------------------------------#
# from email.mime.text import MIMEText
# # email.mime.text : 1 module cung cấp lớp và hàm xử lý phần text
# # MIMEText : 1 lớp tạo và biểu diễn text
# #--------------------------------------------------#
# from email.mime.base import MIMEBase
# # email.mime.base : 1 module cung cấp lớp và hàm xử lý phần text
# # MIMEBase : 1 lớp tạo và biểu diễn phần base64 (Dùng cho đính kèm file)
# #--------------------------------------------------#
# from email import encoders
# # encoders : 1 module hỗ trọ mã hóa
# # Thường dùng để chuyển kiểu dữ liệu thành định dạng base64 khi đính kèm mail


# #-------------------------HÀM MAIN-------------------------#
# def main():
#     # Đầu tiên nó chạy hàm tải data từ file config để xem thông tin các client đã đăng ký và lưu vào biến email_config
#     # Tên biến   = hàm tải data từ file config
#     # Sau khi chạy xong hàm sẽ trả về trường email trong file config vào biến email_config
#     email_config = load_data_from_fileconfig('GeneralFileConfig.json')
        
#     # Nhập tên và mật khẩu để đăng nhập
#     print("Please input username and password to login to your account!")
    
#     # Lặp đến khi nào nhập đúng username với password để dùng lệnh break thì thôi
#     while True:
#         username = input("Username (Mail): ")
#         password = input("Password: ")
                
#         ##### ĐOẠN NÀY PHẢI XỬ LÝ ĐỌC NHIỀU DỮ LIỆU
#         # Lúc này biến email_config đang lưu trường email mà trong trường email có trường con là username và password
#         # Hàm extract_email để lấy tên gmail trong trường con username có dạng 'Ten <gmail>' trong trường Email
#         if username == extract_email(email_config["username"]) and password == email_config["password"]:
#             break
#         else:
#             print("Your username or password is wrong!")
#         print('------------------------------------------------------------------')
    
#     print('LOG IN SUCCESSFULLY!')
    
#     # CHOICE.
#     print("Options Menu:")
#     print("1. Send Mail.")
#     print("2. View List Of Mail.")
#     print("3. Exit.")
#     choice = input("Your choice is: ")
    
#     # SEND EMAIL.
#     if choice == "1":
#         # Khai báo thông tin server SMTP bao gồm địa chỉ HOST và số PORT
#         HOST = "127.0.0.1" # Địa chỉ loopback: tức là nó sẽ trả về địa chỉ của máy
#         PORT = 2225 # Số port của phương thức SMTP
        
#         # Khởi tạo Socket Gửi
#         ##### XEM LẠI CÁI KHỞI TẠO NÀY ĐI
#         s = sk.socket()
#         server_address = (HOST, PORT) # Kiểu dữ liệu tuple dùng để lưu trữ các đối tượng không thay đổi về sau
#         s.connect(server_address) # Tạo kết nối server
        
#         # Dùng khối try để gửi mail
#         try:
#             # Nó nhận thông điệp chào đón từ server
#             # Vì khi kết nối được thì server thường gửi thông điệp về để cho client biết
#             welcome_message = s.recv(1024)
            
#             # Chạy hàm gửi mail với s là socket còn email_config là file config chứa thông tin email
#             send_mail(s, email_config)
            
#         # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
#         # Thông tin lỗi sẽ lưu vào biến e
#         except Exception as e:
#             s.close() # Đóng kết nối socket để tránh rò rỉ kết nối
#             print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
#             print("Disconnected from SERVER!")

#     # RECIEVE EMAIL.
#     elif choice == "2":
#         folder_isExist()
        
#         # Khai báo thông tin server POP3 bao gồm địa chỉ HOST và số PORT1
#         HOST = "127.0.0.1" # Địa chỉ loopback: tức là nó sẽ trả về địa chỉ của máy
#         PORT1 = 3335 # Số port của phương thức POP3

#         # Khởi tạo Socket Nhận
#         ##### XEM LẠI CÁI KHỞI TẠO NÀY ĐI
#         s1 = sk.socket()
#         server_address = (HOST, PORT1)  # Kiểu dữ liệu tuple dùng để lưu trữ các đối tượng không thay đổi về sau
#         s1.connect(server_address) # Tạo kết nối server
        
#         # Dùng khối try để nhận mail
#         try:
#             # Nó nhận thông điệp chào đón từ server
#             # Vì khi kết nối được thì server thường gửi thông điệp về để cho client biết
#             welcome_message = s1.recv(1024)
            
#             # Chạy hàm gửi mail với s1 là socket còn lại là thông tin tài khoản
#             receive_mail(s1,username,password)
            
#         # Nếu khối try có bất kỳ ngoại lệ nào thì sẽ chạy khối except
#         # Thông tin lỗi sẽ lưu vào biến e
#         except Exception as e:
#             s1.close() # Đóng kết nối socket để tránh rò rỉ kết nối
#             print(f"Error: {e}") # Xuất thông tin lỗi lên màn hình
#             print("Disconnected from SERVER!")
    
#     # EXIT.
#     elif choice == "3":
#         print("EXIT SUCCESSFULLY!")
#         pass # Bỏ qua lệnh else phía dưới
    
#     # WRONG CHOICE
#     else:
#         print("Your choice is invalid!")

# #-------------------------HÀM LOAD DATA FROM FILECONFIG-------------------------#
# # Hàm này tải dữ liệu từ file config và trả về dữ liệu ở trường "email"
# # File config sẽ được lưu dưới dạng kiểu dữ liệu dictionary
# def load_data_from_fileconfig(file_name):
#     # Mở file config ra rồi gán dữ liệu vào biến config_file
#     # Lệnh with...as... sẽ giúp mở tệp tin và tự động đóng khi kết thúc
#     with open(file_name) as config_file:
#         # dùng hàm json.load trong thư viện json để load nội dung file json vào config
#         config = json.load(config_file)
#     # Trả về trường "email"
#     return config["email"]

# #-------------------------HÀM GIẢI NÉN TRƯỜNG EMAIL-------------------------#
# # Hàm lấy tên gmail trong trường con username có dạng 'Tên <gmail>' trong trường Gmail
# def extract_email(input_string):
#     # <...>: trích xuất trong cặp dấu '<>'
#     # (...): chứa một biểu thức
#     # ^: không hoặc khác 
#     # [^>]+: ký tự khác > thì lấy
#     # => trích xuất chuỗi ký tự trong cặp dấu '<>'
#     # Tương tự: r'\(([^)]+)\)' // Do cặp dấu '()' là ký tự đặc biệt nên thêm '\' ở phía trước
#     email_pattern = r'<([^>]+)>' # r là tiền tố để xử lý ký tự đặc biệt mà kh xóa chúng
    
#     match = re.search(email_pattern, input_string)
#     if match:
#         # Số 1 có nghĩa là nó trả về chuỗi khớp đầu tiên
#         # Nếu thay bằng 0 thì nó sẽ trả về toàn bộ chuỗi
#         # Nếu để trống thì nó sẽ tự thay 0 nếu không tìm thấy và 1 nếu tìm thấy
#         return match.group(1)
#     else:
#         return None

# #-------------------------HÀM GỬI MAIL-------------------------#
# def send_mail(s, email_config):
#     msg = MIMEMultipart()
#     # REQUEST TO CONNECT
#     message = 'EHLO [{}] \r\n'.format("127.0.0.1").encode()
#     s.send(message)
#     response = s.recv(1024)

#     # MAIL FROM
#     mail_add = extract_email(email_config["username"])
#     mail_from = 'MAIL FROM:<{}> \r\n'.format(mail_add).encode()
#     s.send(mail_from)
#     response = s.recv(1024)

#     # RCPT TO
#     mail_to = input('RCPT TO: ')
#     rcpt_to = 'RCPT TO:<{}> \r\n'.format(mail_to).encode()
#     s.send(rcpt_to)
#     response = s.recv(1024)
    
#     ##### THIẾU RCPT CC
#     # mail_cc = input('RCPT CC: ')
#     # rcpt_cc = 'RCPT CC:<{}> \r\n'.format(mail_cc).encode()
#     # s.send(rcpt_cc)
#     # response = s.recv(1024)
#     ##### THIẾU RCPT BCC
#     # mail_bcc = input('RCPT BCC: ')
#     # rcpt_bcc = 'RCPT BCC:<{}> \r\n'.format(mail_bcc).encode()
#     # s.send(rcpt_bcc)
#     # response = s.recv(1024)
    
#     # REQUEST TO INPUT DATA
#     s.sendall(b'DATA\r\n')
#     response = s.recv(1024)
    
#     # START TO INPUT DATA
#     subject = input("Subject: ")
#     content = input("Content: ")
#     ##### CHƯA HIỂUUUUU
#     unique_id = uuid.uuid4()
#     named_tuple = time.localtime()
#     local_time = time.strftime("%a, %d %b %Y %H:%M:%S", named_tuple)
#     ##### CHƯA HIỂU    

#     message = f"""Message ID: <{unique_id}@gmail.com>
# Date: {local_time} +0700
# MIME-Version: 1.0 
# User-Agent: Mozilla Thunderbird
# Content-Language: vi-x-KieuCu.[Chuan]
# To: Toi <{mail_to}>
# From: Tu <{mail_add}>
# Subject: {subject}

# {content}
            
# """
#     email_info = f'{message}\r\n'
#     msg.attach(MIMEText(email_info,"plain"))
#     choice = input("Co gui file dinh kem (1. Co, 2. Khong): ")
#     if choice == '1':
#         num = int(input("Gui bao nhieu file: "))
#         max_size = 3 * 1024 * 1024 #3MB
#         for i in range(num):
#             path = input(f"Nhap duong dan file thu {i+1}: ")
#             file_size = os.path.getsize(path)
#             if file_size > max_size:
#                 print(f"Tệp đính kèm quá dung lượng. Dung lượng hiện tại: {file_size} bytes, Dung lượng tối đa cho phép: {max_size} bytes")
#             else:
#                 print("Dung lượng tệp đính kèm hợp lệ.")
#                 attachment(path,msg)
#                 max_size = max_size - file_size
#     s.sendall(f'{msg.as_string()}\r\n.\r\n'.encode())
#     response = s.recv(1024)
#     print(response.decode())
#     print("SEND SUCCESSFULLY!")
#     print('------------------------------------------------------------------')

# #-------------------------HÀM NHẬN MAIL-------------------------#
# def receive_mail(s1, username, password):
#     # SEND CAPA.
#     #  
#     # Kiểu chào á, nói chuyện được thì nói tiếp
#     s1.send(b'CAPA\r\n')
#     response = s1.recv(1024).decode()

#     # SEND USER.
#     s1.send(f'USER {username}\r\n'.encode())
#     response = s1.recv(1024).decode()

#     # SEND PASSWORD.
#     s1.send(f'PASS {password}\r\n'.encode())
#     response = s1.recv(1024).decode()

#     # SEND STAT.
#     s1.send(b'STAT\r\n')
#     response = s1.recv(1024).decode()
#     # response = +OK x y: x là số lượng y là tổng kích thước
#     num_of_mail = response[4]
#     # Print number of mail in the mail box.
#     print(f"Total of mail is: {num_of_mail}")

#     # SEND LIST.
#     s1.send(b'LIST\r\n')
#     response = s1.recv(1024).decode()
#     ## kèm theo số thứ tự và kích thước của mỗi tin nhắn

#     ##### Có thể giải quyết kích thước, thằng nào lớn quá thì cook

#     # SEND UIDL.
#     s1.send(b'UIDL\r\n')
#     response = s1.recv(1024).decode()
#     ## Có thể dùng để xử lý mail đã hay chưa tải xuống máy

#     ##### Code đọc nội dung + lọc + tải mail về máy

#     ##### Code giao diện

#     #---------------------------------    
#     # SEND RETR.
#     choose = input("Input file number which you want to open: ")
#     s1.send('RETR {}\r\n'.format(choose).encode())
#     response = s1.recv(int(1e10)).decode()
#     #---------------------------------    

#     if 'Content-Disposition: attachment' in response:
#     # Get the boundary string for parsing multipart content
#         boundary = response.split('\r\n--')[1].split('==\r\n')[0]

#     # Split the response into parts using the boundary
#         parts = response.split(boundary)[1:]

#     # Create a directory to store attachments
#         attachment_dir = os.path.join(os.getcwd(), 'Attachments')
#         os.makedirs(attachment_dir, exist_ok=True)

#     # Iterate over the parts and look for attachments
#         for part in parts:
#             if 'Content-Disposition: attachment' in part:
#                 content_type = part.split('filename=')[1].split('\r\n')[0]
#                 attachment_data = part.split(f'{content_type}')[1].split('\r\n--')[0].strip()
#                 save_attachment(attachment_data, attachment_dir, content_type)

#     list_info_mail = response.splitlines()[1:]
#     for item in list_info_mail:
#         print(item)

#     # SEND QUIT.
#     s1.send(b'QUIT\r\n')
#     response = s1.recv(1024).decode()

#     # PRINT NOTIFICATION.
#     print('OPEN SUCCESSFULLY!')
#     print('------------------------------------------------------------------')
    
# #-------------------------HÀM ...-------------------------#
# # The function check the folder exist or not.
# def folder_isExist():
#     folder_address = os.getcwd()
#     list_file_folder = os.listdir(folder_address)
#     if "Project" not in list_file_folder:
#         os.makedirs("Project")
#     if "Attachments" not in list_file_folder:
#         os.makedirs("Attachments")
#     if "Important" not in list_file_folder:
#         os.makedirs("Important")
#     if "Work" not in list_file_folder:
#         os.makedirs("Work")
#     if "Spam" not in list_file_folder:
#         os.makedirs("Spam")
#     if "Inbox" not in list_file_folder:
#         os.makedirs("Inbox")

# #-------------------------HÀM ...-------------------------#
# def attachment(path,msg):
#     file_name = basename(path)
#     with open(path, 'rb') as attachment:
#         attachment_package = MIMEBase('application', 'octet-stream')
#         attachment_package.set_payload(attachment.read())
#         encoders.encode_base64(attachment_package)
#         attachment_package.add_header('Content-Disposition', 'attachment; filename=' + file_name)
#         msg.attach(attachment_package)

# #-------------------------HÀM ...-------------------------#
# def save_attachment(attachment_data, attachment_dir, content_type): 
#     attachment_path = os.path.join(attachment_dir, content_type)
#     with open(attachment_path, 'wb') as attachment_file:
#         attachment_file.write(base64.b64decode(attachment_data))
#     attachment_file.close()
#     print(f"Attachment saved: {attachment_path}")

# #-------------------------HÀM ...-------------------------#
# if __name__ == "__main__":
#     main()
#     # Load data of General Config File.


# def receive_mail(pop3_socket, user_info):
#     # SEND CAPA
#     pop3_socket.send(b'CAPA\r\n')
#     pop3_socket.recv(1024).decode()

#     # SEND USER
#     pop3_socket.send(f'USER {user_info["Username"]}\r\n'.encode())
#     pop3_socket.recv(1024).decode()

#     # SEND PASS
#     pop3_socket.send(f'PASS {user_info["Password"]}\r\n'.encode())
#     pop3_socket.recv(1024).decode()
    
#     # SEND STAT
#     pop3_socket.send(b'STAT\r\n')
#     ## TRẢ VỀ: +OK x y (x là số mail, y là tổng kích thước theo byte)
#     response = pop3_socket.recv(1024).decode()
    
#     num_mail = response[4]
    
#     # SEND LIST
#     pop3_socket.send(b'LIST\r\n')
#     ## TRẢ VỀ: 
#     # +OK
#     # Thứ tự mail _ size mail
#     response = pop3_socket.recv(1024).decode()

#     # SEND UIDL
#     pop3_socket.send(b'UIDL\r\n')
#     ## TRẢ VỀ: 
#     # +OK
#     # Thứ tự mail _ <mã độc nhất>.msg
#     response = pop3_socket.recv(1024).decode()
    
#     uidl_list = []
    
#     # Duyệt qua các dòng trong response
#     for line in response.splitlines():
#         # Bỏ qua dòng đầu tiên và dòng cuối cùng
#         if line != "+OK" and line != ".":
#             # Tách dòng theo khoảng trắng
#             line_list = line.split()
                
#             # Lấy phần tử thứ hai, đó là mã định danh
#             uidl = line_list[1]
                
#             # Thêm mã định danh vào danh sách
#             uidl_list.append(uidl)
    
    
#     # SEND RETR
#     for i in range(0, num_mail):
#         if isUIDL_Exist(uidl_list[i], ''):
#             pop3_socket.send('RETR {}\r\n'.format(i+1).encode())
#             # response = b'' # Gán biến rỗng dạng byte
#             # while True:
#             #     temp = pop3_socket.recv(1024)
#             #     response += temp
#             #     if b'\r\n.\r\n' in temp:
#             #         break
#             # response = response.decode()
#             response = pop3_socket.recv(int(1e10)).decode()
#             mail_processing(response, 'MailList.json')
            

# def mail_processing(response, file_name):
#     subject = ""
#     from_ = ""
#     to = ""
#     date = ""
#     content_type = ""
#     body = ""
#     email = {subject: "", from_: "", to: "", date: "", content_type: "", body: ""}
    
#     # Tách response thành một danh sách các dòng
#     lines = response.splitlines()
#     # Bỏ qua dòng đầu tiên và dòng cuối cùng
#     lines = lines[1:-1]
    
#     # Tạo một biến boolean để kiểm tra xem có attachment không
#     has_attachment = False
    
#     # Duyệt qua các dòng còn lại
#     for line in lines:
#         # Kiểm tra nếu dòng bắt đầu bằng Subject
#         if line.startswith("Subject"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#             email["subject"] = line.split(":")[1].strip()
#         # Kiểm tra nếu dòng bắt đầu bằng From
#         elif line.startswith("From"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#              email["from_"] = line.split(":")[1].strip()
#         # Kiểm tra nếu dòng bắt đầu bằng To
#         elif line.startswith("To"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#              email["to"] = line.split(":")[1].strip()
#         # Kiểm tra nếu dòng bắt đầu bằng Date
#         elif line.startswith("Date"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#              email["date"] = line.split(":")[1].strip()
#         # Kiểm tra nếu dòng bắt đầu bằng Content-Type
#         elif line.startswith("Content-Type"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#              email["content_type"] = line.split(":")[1].strip()    
#         # Kiểm tra nếu dòng bắt đầu bằng Content-Disposition
#         elif line.startswith("Content-Disposition"):
#             # Tách dòng theo dấu hai chấm và lấy phần tử thứ hai
#             disposition = line.split(":")[1].strip()
#             # Kiểm tra nếu giá trị của disposition có chứa attachment
#             if "attachment" in disposition:
#                 # Gán biến kiểm tra attachment là True
#                 has_attachment = True
#         # Kiểm tra nếu dòng bắt đầu bằng một dấu gạch ngang
#         elif line.startswith("-"):
#             # Bỏ qua dòng đó
#             continue
#         # Nếu dòng không bắt đầu bằng một trường header nào
#         else:
#             # Coi dòng đó là nội dung của tin nhắn
#             body += line + "\n"
    
#     with open(file_name, "w+") as f:
#         # Đưa con trỏ file về đầu file
#         f.seek(0)
#         # Ghi lại danh sách vào file json
#         json.dump(email, f)
#         # Xóa nội dung thừa ở cuối file
#         f.truncate()
    

    


            
            
# # attachment_path = os.path.join(attachment_dir, content_type)
# # with open(attachment_path, 'wb') as attachment_file:
# # attachment_file.write(base64.b64decode(attachment_data))
# # attachment_file.close()
# # print(f"Attachment saved: {attachment_path}")            
            

# # Định nghĩa hàm lưu uidl vào file json
# def save_uidl(response, file_name):
#     # Mở file json để đọc và ghi
#     with open(file_name, "r+") as f:
#         # Đọc nội dung file json vào một danh sách
#         uidl_list = json.load(f)
        
#         # Duyệt qua các dòng trong response
#         for line in response.splitlines():
#             # Bỏ qua dòng đầu tiên và dòng cuối cùng
#             if line != "+OK" and line != ".":
#                 # Tách dòng theo khoảng trắng
#                 line_list = line.split()
#                 # Lấy phần tử thứ hai, đó là mã định danh
#                 uidl = line_list[1]
#                 # Kiểm tra nếu mã định danh chưa có trong danh sách
#                 if uidl not in uidl_list:
#                     # Thêm mã định danh vào danh sách
#                     uidl_list.append(uidl)
#         # Đưa con trỏ file về đầu file
#         f.seek(0)
#         # Ghi lại danh sách vào file json
#         json.dump(uidl_list, f)
#         # Xóa nội dung thừa ở cuối file
#         f.truncate()

            

# def recv_attachment():
#     input()
                
#     ##### LỌC MAIL CHƯA TẢI -> TẢI VỀ -> CHIA FOLDER
#     #### Trong lọc mail chưa tải:
#     ### Lưu danh sách uidl vào 1 list
#     ### Mở file json
#     ### So sánh list với file json bằng vòng lặp
#     ## Nếu mà đã có thì bỏ qua
#     ## Nếu mà chưa có thì lưu vào file json (có ký hiệu chưa đọc)
#     #-------------------- rồi nó tải về (phân loại), trong lúc tải về lấy from, subject, data (lưu vào file txt)



# def isUIDL_Exist(uidl, file_name):
#     # Mở file json để đọc và ghi
#     with open(file_name, "r+") as f:
#         # Đọc nội dung file json vào một danh sách
#         uidl_list = json.load(f)
        
#         if uidl not in uidl_list:
#             return True
#         return False
        



    
