from database import add_user, get_active_users

def main():
    print("正在初始化云端用户...")
    add_user("your_email@sjtu.edu.cn", "管理员", ["计算机学院", "教务处"])
    
    users = get_active_users()
    print(f"云端现有用户: {users}")

if __name__ == "__main__":
    main()