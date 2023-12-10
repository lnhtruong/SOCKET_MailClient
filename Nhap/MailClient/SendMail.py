import socket
import os
import uuid
import datetime
##### import langid
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

import Other

FORMAT = 'utf-8'

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
    
    # Phần nhập attached file
    attached_choice = input("Do you want to send attached files? (1. Yes, 2. No): ")
    if attached_choice == '1':
        MAX_SIZE = 3 * 1024 * 1024
        remain_size = MAX_SIZE
        num_attached = int(input("Number of attached files: "))

        for i in range(num_attached):
            while True:
                attached_path = input(f"Enter path for attached file {i + 1}: ")
                try:
                    attached_size = os.path.getsize(attached_path)

                    if attached_size > remain_size:
                        print(f"Attached file exceeds remaining maximum size. "
                              f"Current size: {attached_size} bytes, Remaining maximum allowed size: {remain_size} bytes")
                        print("Please try again.")
                    else:
                        attached_files.append(attached_path)  # Thêm đường dẫn tệp vào danh sách đính kèm
                        remain_size -= attached_size

                except FileNotFoundError:
                    print(f"File not found: {attached_path}. Please enter a valid attached file path.")
                except IOError as e:
                    print(f"Error opening file {attached_path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")

    # Gọi hàm send_mail với danh sách tệp đính kèm
    send_mail(user_info, server_info, to, subject, content, cc, bcc, attached_files)
    print("SEND SUCCESSFULLY!")
    print('------------------------------------------------------------------')

def send_mail(user_info, server_info, to, subject, content, cc=None, bcc=None, attached_files=None):
    global FORMAT
    # Dùng khối try để gửi mail
    try:
        # Mở kết nối socket
        smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        smtp_socket.connect((server_info["MailServer"], int(server_info["SMTP"])))
        # Nhận thông tin lời chào từ server
        welcome_message = smtp_socket.recv(1024).decode()

        try:
            if attached_files:
                msg = MIMEMultipart()
            else:
                msg = MIMEText(content + '\r\n', 'plain')
                msg.replace_header('Content-Type', 'text/plain; charset=UTF-8; format=flowed')
                # Xóa dòng MIME-Version
                del msg['MIME-Version']

            # Gửi lệnh EHLO để bắt đầu
            message = 'EHLO [{}] \r\n'.format(str(user_info['MailServer'])).encode(FORMAT)
            smtp_socket.send(message)
            # Tách email từ username
            email_address = Other.extract_email_address(user_info['Username'])
            # Gửi lệnh MAIL FROM
            message = 'MAIL FROM:<{}> \r\n'.format(email_address).encode(FORMAT)
            smtp_socket.send(message)

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
            if attached_files:
                # text/plain: Chỉ định nội dung văn bản của email không chứa định dạng đặc biệt
                body = MIMEText(content + '\r\n', 'plain')
                body.replace_header('Content-Type', 'text/plain; charset=UTF-8; format=flowed')
                # Xóa dòng MIME-Version
                del body['MIME-Version']
                msg.attach(body)
            # Thêm file đính kèm
            if attached_files:
                for attached_path in attached_files:
                    send_file(attached_path, msg)

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

def send_file(attached_path, msg):
    # Lấy tên file từ đường dẫn
    attached_name = basename(attached_path)
    
    # Mở chế độ đọc nhị phân 'rb'
    with open(attached_path, 'rb') as attached_file:
        # Lấy 4 ký tự cuối cùng của tên file (định dạng file)
        last_four_char = attached_name[-4:].lower()
        
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

        attached_package = MIMEBase(maintype, subtype, name=f'{attached_name}')
        # Đặt dữ liệu tệp tin đã được mã hóa vào đối tượng MIMEBase
        attached_package.set_payload(attached_file.read())
        attached_package.add_header('Content-Disposition', f'attachment; filename="{attached_name}"')
        encoders.encode_base64(attached_package)

        # Xóa dòng MIME-Version (được thêm tự động)
        del attached_package['MIME-Version']

        msg.attach(attached_package)
