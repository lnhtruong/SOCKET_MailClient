# Thư viện tạo luồng chạy song song
import threading
import Other
import Login
import SendMail
import ViewMail

from AutoloadMail import auto_load_mail, set_exit_flag
# from AutoloadMail import exit_flag

'''QUY TẮC ĐẶT TÊN
- Tên biến: chữ thường, cách nhau bởi dấu gạch dưới (_)
- Tên hàm: chữ thường, cách nhau bởi dấu gạch dưới (_)
- Tên hằng số: chữ in hoa, cách nhau bởi dấu gạch dưới (_)
- Tên biến toàn cục: chữ thường, cách nhau bởi dấu gạch dưới (_)

- Kết thúc bằng "mail" còn nằm giữa thì là "email"
- Thêm số nhiều ở cuối tên là danh sách
- Động từ tobe hoặc giới từ thì viết thường dính liền từ đứng sau viết hoa chữ cái đầu
'''
'''DANH SÁCH CÁC BIẾN
- password: mật khẩu
- email_server: địa chỉ mail server
- auto_load: thời gian tự động tải mail
- unique_id: mã độc nhất
- from: người gửi (from_)
- to: người nhận to
- cc: người nhận cc
- bcc: người nhận bcc
- subject: tiêu đề
- content/body: nội dung
- attachment: nội dung file đính kèm
- msg: nội dung mail  
- smtp: giao thức smtp
    + smtp_port: cổng smtp
    + smtp_socket: socket smtp
- pop3: giao thức pop3
    + pop3_port: cổng pop3
    + pop3_socket: socket pop3

- name: tên
    + user_name: tên người dùng
    + attached_name: tên file đính kèm
    + folder: tên thư mục
    + msg_name: tên file mail

- info: thông tin
    + user_info: thông tin người dùng (bao gồm username, password, email_server, smtp, pop3, auto_load)
    + server_info: thông tin server (bao gồm email_server, smtp, pop3, auto_load)
    + email_info: thông tin email (bao gồm unique_id, from, to, cc, bcc, subject, content, attached_files,...)

- data: dữ liệu
    + raw_data: dữ liệu gốc
    + email_data: dữ liệu email
    + attached_data: dữ liệu file đính kèm
    
- choice: lựa chọn của người dùng
    + menu_choice: lựa chọn menu
    + folder_choice: lựa chọn thư mục
    + mail_choice: lựa chọn mail
    + save_choice: lựa chọn có lưu mail hay không
    + attached_choice: lựa chọn có gửi file đính kèm hay không
    
- path: đường dẫn
    + program_path: đường dẫn chương trình
    + email_path: đường dẫn file email
    + attached_path: đường dẫn file đính kèm
    + input_path: đường dẫn file đính kèm nhập vào
    + output_path: đường dẫn file đính kèm xuất ra
  
- address: địa chỉ email
    + email_address: địa chỉ email
    + to_address: địa chỉ email người nhận to
    + cc_address: địa chỉ email người nhận cc
    + bcc_addre: địa chỉ email người nhận bcc
    
- response: phản hồi từ server
    + uidl_response: phản hồi UIDL
    + retr_response: phản hồi RETR
    + list_response: phản hồi LIST
    + welcome_message: phản hồi lời chào
    
- line: dòng
    + list_line: dòng phản hồi LIST
    + uidl_line: dòng phản hồi UIDL
    + retr_line: dòng phản hồi RETR
  
- size: kích thước
    + email_size: kích thước mail
    + remain_size: kích thước còn lại
    + attached_size: kích thước file đính kèm
    + MAX_SIZE: kích thước tối đa của file đính kèm (hằng số)
    + remain_size: kích thước còn lại của file đính kèm

- attached: file đính kèm
    + attached_file: file đính kèm
    + attached_package: gói đính kèm
        
- count: đếm
    + count_empty_line: đếm số dòng trống
    + count_file: đếm số file đính kèm
    + i: biến đếm
    
- check: kiểm tra
    + check_account: kiểm tra tài khoản
    + check_account_again: kiểm tra tài khoản lần 2
    
- filter: lọc
    + filter_content: nội dung lọc
    + filter_item: từng filter
          
- num: số lượng
    + num_attached: số lượng file đính kèm
    
- exit_flag: biến thoát chương trình
- message: thông điệp gửi đến server
- file_folder: tập tin hoặc thư mục    

- now: ngày giờ hiện tại
- formatted_date: ngày giờ định dạng
- language: ngôn ngữ
- confidence: độ chính xác
- maintype: loại chính
- subtype: loại phụ
- keyword: từ khóa
- last_four_char: 4 ký tự cuối cùng (định dạng file)
'''

# HÀM MAIN
def main(user_info, server_info):
    global exit_flag
    # Lấy địa chỉ email từ username
    email_address = Other.extract_email_address(user_info["Username"])
    
    # Bắt đầu giao diện người dùng
    while True:
        print("Menu:")
        print("1. Send mail")
        print("2. View a list of received emails")
        print("3. Exit")
        menu_choice = input("Enter your choice: ")
        
        # GỬI MAIL
        if menu_choice == '1':
            SendMail.menu_send_mail(user_info, server_info)

        # XEM MAIL
        elif menu_choice == '2':
            ViewMail.menu_view_mail(email_address)      

        # THOÁT
        elif menu_choice == '3':
            set_exit_flag()
            print("Exiting program...")
            break

        # NHẬP SAI
        else:
            print("Invalid choice! Please try again!")
            print('------------------------------------------------------------------')
            continue
            
if __name__ == "__main__":
    user_info = Login.login()
    if user_info["Username"] != "0" and user_info["Password"] != "0":
        email_address = Other.extract_email_address(user_info["Username"])
        Other.folder_isExist(email_address)
        server_info = Other.get_server_info(user_info)
        
        main_thread = threading.Thread(target=main,args=(user_info, server_info))
        auto_thread = threading.Thread(target=auto_load_mail,args=(user_info, server_info))
        
        main_thread.start()
        auto_thread.start()
        
        main_thread.join()
    else:
        print("Login failed!")