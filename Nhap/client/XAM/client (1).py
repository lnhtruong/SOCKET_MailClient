# Cung cấp giao điện cấp thấp để giao tiếp mạng
import socket
# Mã hóa và giải mã dữ liệu nhị phân theo định dạng base64
import base64
# Cung cấp tương tác với hệ diều hành (Dùng trong thao tác tệp tin)
import os
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
from email import parser
from email.header import decode_header
import re

FORMAT = 'utf-8'
sent_email = []
HOST = '127.0.0.1'


def send_mail(smtp_socket, user_info):
    msg = MIMEMultipart()
    # Gửi lệnh EHLO để bắt đầu
    message = 'EHLO [{}] \r\n'.format('127.0.0.1').encode()
    smtp_socket.send(message)

    # Gửi lệnh MAIL FROM
    mail_from = 'MAIL FROM:<{}> \r\n'.format(user_info['Username']).encode()
    smtp_socket.send(mail_from)

    # Kiểu gửi TO và CC
    to = input('TO: ')
    cc = input('CC: ')

    to_addresses = []
    # Gửi lệnh RCPT TO cho người nhận TO
    if to.strip():
        to_addresses = to.split(',')  # Lấy mail đã được format lại
        for address in to_addresses:
            # Gửi các mail đã được format lại (Xóa bỏ khoảng trắng, newline, carriage return)
            smtp_socket.send('RCPT TO:<{}> \r\n'.format(address.strip()).encode(FORMAT))

    cc_addresses = []
    # Gửi lệnh RCPT TO cho người nhận CC
    if cc.strip():  # Kiểm tra xem có mail gửi dạng cc không
        cc_addresses = cc.split(',')  # Lấy mail đã được format lại
        for address in cc_addresses:
            smtp_socket.send('RCPT TO:<{}> \r\n'.format(address.strip()).encode(FORMAT))

    # Lệnh DATA
    smtp_socket.sendall(b'DATA\r\n')

    # Nội dung mail
    subject = input("Subject: ")
    content = input("Content: ")
    msg['To'] = ", ".join(to_addresses)
    if cc.strip():
        msg['Cc'] = ",".join(cc_addresses)
    msg['From'] = user_info["Username"]
    msg['Subject'] = subject
    message = f"""{content}
    """
    email_info = f'{message}\r\n'
    # text/plain: Chỉ định nội dung văn bản của email không chứa định dạng đặc biệt
    msg.attach(MIMEText(email_info, 'plain'))
    # Thêm file đính kèm
    choice = input("Do you want to attach files? (1. Yes, 2. No): ")
    if choice == '1':
        num = int(input("Number of files: "))
        MAX_SIZE = 3 * 1024 * 1024  # 3MB
        for i in range(num):
            path = input(f"Enter path for file {i + 1}: ")
            file_size = os.path.getsize(path)
            if file_size > MAX_SIZE:
                print(
                    f"Attached file exceeds maximum size. Current size: {file_size} bytes, "
                    f"Maximum allowed size: {MAX_SIZE} bytes")
            else:
                send_file(path, msg)
                MAX_SIZE -= file_size

    # Gửi mail
    smtp_socket.sendall(f'{msg.as_string()}\r\n.\r\n'.encode(FORMAT))
    smtp_socket.recv(1024)

    print("SEND SUCCESSFULLY!")
    print('------------------------------------------------------------------')


def send_file(path, msg):
    file_name = basename(path)
    # Mở chế độ đọc nhị phân 'rb'
    with open(path, 'rb') as attachment_file:
        last_four_char = file_name[-4:].lower()
        # Xác định Content-Type
        maintype = None
        subtype = None
        if last_four_char == '.txt':
            maintype = 'application'
            subtype = 'octet-stream'
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
        # Set filename in Content-Disposition header
        attachment_package.add_header('Content-Disposition', f'attachment; filename=' + file_name)
        encoders.encode_base64(attachment_package)

        # Xóa dòng MIME-Version (được thêm tự động)
        del attachment_package['MIME-Version']

        msg.attach(attachment_package)


def main():
    # Khởi tạo và nhập thông tin người dùng
    user_info = {'Username': input("Enter username: "),
                 'Password': input("Enter password: "),
                 }

    while True:
        print("Menu:")
        print("1. Send mail")
        print("2. View a list of received emails")
        print("3. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            PORT1 = 2225
            smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            smtp_socket.connect((HOST, PORT1))
            send_mail(smtp_socket, user_info)
            
        elif choice == '2':
            PORT2 = 3335
            pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pop3_socket.connect((HOST, PORT2))
            receive_mail(pop3_socket, user_info)


        elif choice == '3':
            print("Exiting program...")
            break

        else:
            print("Invalid choice! Please try again")


if __name__ == "__main__":
    main()


tao5 file vao inbox 1. (chua doc) <nguoigui> <subject>.txt

1.

email["su"]