import json
import Other

### CÁC HÀM ĐĂNG NHẬP
def login():
    # Khởi tạo và nhập thông tin người dùng
    email_address = input("Enter email address: ")
    user_name = input("Enter username: ")
    user_info = {'Username': user_name + " <" + email_address + ">",
                 'Password': input("Enter password: "),
                 'MailServer': '127.0.0.1',
                 'SMTP': 2225,
                 'POP3': 3335,
                 'AutoLoad': 10
                 }
      
    # Kiểm tra tài khoảng người dùng
    check_account(user_info)
    
    # Trả về thông tin người dùng sau khi đăng nhập
    return user_info
    
def check_account(user_info):
    # Dùng khối try để kiểm tra tài khoản
    try:
        with open('account.json', 'r') as f:
            data = json.load(f)
            # Vòng lặp để duyệt qua từng tài khoản trong file account.json
            for account in data['account']:
                # Check xem tài khoản đã tồn tại hay chưa
                if check_account_again(account, user_info) == True:
                    return
            # Nếu chưa thì tạo tài khoản mới 
            create_account(user_info)
            return
    # Nếu file account.json chưa tồn tại thì tạo và đăng ký tài khoản mới
    except FileNotFoundError:
        data = {'account': []}
        data['account'].append(user_info)
        with open('account.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Account created successfully!")
        print('------------------------------------------------------------------')
        
def check_account_again(account_inJson, user_info):
    try:
        # Tách email từ account
        email_inJson = Other.extract_email_address(account_inJson['Username'])
        # Tách email từ username
        email_ofUser = Other.extract_email_address(user_info['Username'])

        # Nếu người dùng nhập đúng email thì kiểm tra username
        if email_inJson == email_ofUser:
            # Nếu username đúng thì kiểm tra password
            if account_inJson['Username'] == user_info['Username']:
                while True:
                    # Nếu password đúng thì thông báo đăng nhập thành công
                    if account_inJson['Password'] == user_info['Password']:
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
                user_info['Username'] += ' <{}>'.format(email_ofUser)
                if check_account_again(account_inJson, user_info):
                    return True
    except AttributeError:
        return False

def create_account(user_info):
    with open('account.json', 'r') as f:
        data = json.load(f)
        data['account'].append(user_info)
    with open('account.json', "w") as f:
        json.dump(data, f, indent=2)
    print("Account created successfully!")
    print('------------------------------------------------------------------')
