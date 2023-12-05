import base64
import os
import socket

MAX_SIZE = 1024  # Define your maximum size constant
FORMAT = 'utf-8'  # Define your encoding format
# Danh sách để lưu trữ thông tin về các email đã gửi
sent_emails = []
smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def send_to(user_info, to, subject, content, attachment_path):
    # Gửi lệnh EHLO để bắt đầu phiên làm việc
    smtp_socket.send(f'EHLO {user_info["MailServer"]}\r\n'.encode(FORMAT))
    smtp_response = smtp_socket.recv(1024).decode()
    print(smtp_response)
    if smtp_response[:3] != '250':
        print('250 reply not received from server')

    # Gửi lệnh MAIL FROM và RCPT TO để xác định người gửi và người nhận
    smtp_socket.send(f'MAIL FROM: <{user_info["Username"]}>\r\n'.encode(FORMAT))
    smtp_response = smtp_socket.recv(1024).decode()
    print(smtp_response)
    if smtp_response[:3] != '250':
        print('250 reply not received from server')
    for recipient in to:
        smtp_socket.send(f'RCPT TO: <{recipient}>\r\n'.encode(FORMAT))
        smtp_response = smtp_socket.recv(1024).decode()
        print(smtp_response)
    # Gửi lệnh DATA để bắt đầu nội dung email
    smtp_socket.send(f'DATA\r\n'.encode(FORMAT))
    smtp_response = smtp_socket.recv(1024).decode(FORMAT)
    print(smtp_response)
    if smtp_response[:3] != '354':
        print('354 reply not received from server')
    # Gửi dữ liệu email
    for i in to:
        smtp_socket.send(b'To: ' + i.encode(FORMAT) + b'\r\n')
    smtp_socket.send(b'From: ' + user_info['Username'].encode(FORMAT)+b'\r\n')
    smtp_socket.send(b'Subject: ' + subject.encode(FORMAT) + b'\r\n')
    smtp_socket.send(b'Content-Type:multipart/mixed; boundary="boundary"\r\r\n\n')
    # Gửi phần text của email
    smtp_socket.send(b'--boundary\r\n')
    # Xác định loại nội dung là văn bản thuần - Đặt bảng mã ký tự UTF-8 - Định dạng lại là flowed(Làm đẹp tự động)
    smtp_socket.send(b'Content-Type:text/plain;charset=UTF-8; format=flowed\r\n')
    smtp_socket.send(content.encode(FORMAT) + b'\r\n')

    # Đọc nội dung file đính kèm và mã hóa
    if attachment_path:
        send_file(attachment_path)

    # Kết thúc mail
    smtp_socket.send(b'--boundary--\r\r.\r\n')

    smtp_response = smtp_socket.recv(1024).decode(FORMAT)
    print(smtp_response)
    # Gửi lệnh RSET để làm mới trạng thái của phiên làm việc
    smtp_socket.send(b'RSET\r\n')
    smtp_response = smtp_socket.recv(1024).decode(FORMAT)
    print(smtp_response)
    # Gửi lệnh QUIT dừng phiên làm việc
    smtp_socket.send(b'QUIT\r\n')
    recv_quit = smtp_socket.recv(1024).decode(FORMAT)
    print(recv_quit)


def send_file(attachment_path_list):
    size = sum(os.path.getsize(attachment_path) for attachment_path in attachment_path_list) / 1024

    if size > MAX_SIZE:
        print("Dung lượng file vượt quá giới hạn tối đa.")
        return

    for attachment_path in attachment_path_list:
        if not os.path.exists(attachment_path):
            print(f"Không tìm thấy file: {attachment_path}")
            continue

        attachment_name = os.path.basename(attachment_path)

        with open(attachment_path, 'rb') as attachment_file:
            attachment_data = attachment_file.read()

        encoded_attachment = base64.b64encode(attachment_data).decode(FORMAT)

        last_four_char = attachment_name[-4:].lower()

        smtp_socket.send(b'--boundary\r\n')

        # Xác định Content-Type dựa trên phần mở rộng của tên file
        content_type = None
        if last_four_char == '.txt':
            content_type = 'application/octet-stream'
        elif last_four_char == '.pdf':
            content_type = 'application/pdf'
        elif last_four_char == 'docx':
            content_type = 'application/msword'
        elif last_four_char == '.jpg':
            content_type = 'image/jpeg'
        elif last_four_char == '.zip':
            content_type = 'application/zip'

        if content_type:
            smtp_socket.send(f'Content-Type:{content_type}; name="{attachment_name}"\r\n'.encode(FORMAT))
            smtp_socket.send(f'Content-Disposition:attachment; filename="{attachment_name}"\r\n'.encode(FORMAT))
            smtp_socket.send(f'Content-Transfer-Encoding: base64\r\n\r\n'.encode(FORMAT))
            # Gửi dữ liệu base64 của file
            smtp_socket.send(encoded_attachment.encode(FORMAT) + b'\r\n')


def get_recipients(recipient_type):
    recipients_input = input(f"{recipient_type}: ")
    if not recipients_input:
        return []
    return [recipient.strip() for recipient in recipients_input.split(',')]


def main():
    # Khởi tạo và nhập thông tin người dùng
    user_info = {'Username': input("Nhập tên đăng nhập: "),
                 'Password': input("Nhập mật khẩu: "),
                 'MailServer': input("Nhập địa chỉ mail server: "),
                 'SMTP': int(input("Nhập cổng SMTP: ")),
                 'POP3': int(input("Nhập cổng POP3: ")),
                 'Autoload': int(input("Nhập khoảng thời gian tự động tải email (giây): "))}

    while True:
        print("Vui lòng chọn Menu:")
        print("1. Để gửi email")
        print("2. Để xem danh sách các email đã nhận")
        print("3. Thoát")

        choice = input("Bạn chọn: ")
        if choice == '1':
            smtp_socket.connect((user_info['MailServer'], user_info['SMTP']))
            to = get_recipients("To")
            subject = input("Subject: ")
            content = input("Content: ")

            attachments = []
            attach_choice = input("Có gửi kèm file (1. có, 2. không): ")
            if attach_choice == '1':
                num_attachments = int(input("Số lượng file muốn gửi: "))
                for i in range(num_attachments):
                    file_path = input(f"Đường dẫn file thứ {i + 1}: ")
                    attachments.append(file_path)

            if to:
                recv = smtp_socket.recv(1024).decode(FORMAT)
                print(recv)
                if recv[:3] != '220':
                    print('\n 220 reply not received from server')
                send_to(user_info, to, subject, content, attachments)
            print("Đã gửi email thành công")

        # elif choice == '2':
        #     while True:
        #         download_email(user_info)
        #         time.sleep(user_info['Autoload'])

        elif choice == '3':
            print("Thoát chương trình.")
            break

        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")


if __name__ == "__main__":
    main()