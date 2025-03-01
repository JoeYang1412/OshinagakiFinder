from database import DatabaseManager
from follow import FollowScraper
from authenticate import TwitterAuthenticator
from OshinagakiFinder import TwitterCrawler
def main():
    """
    Main functionality options of this program:
    1. Login Authentication: 
    Users can manually log in to Twitter to obtain authentication status, 
    and multiple authentication status files can be created (e.g., for two accounts).

    2. Author Database: 
    Users can store author URLs in the database, 
    providing automatic scraping of the current account's followed users, or manually adding them.

    3. Query All Author Works: 
    Users can query all authors' works and choose to query FF sessions or other keywords 
    (such as CWT, this is a Beta option).

    4. Exit
    
    """
    while True:
        print("\n1.登入驗證")
        print("2.作者資料庫")
        print("3.查詢所有作者品書")
        print("4.離開")
        while True:
            choice = input("請輸入選項:")
            if choice in ["1", "2", "3", "4"]:
                break
            else:
                print("無效的選項，請輸入1到4之間的數字。")
        
        if choice == "1":
            auth = TwitterAuthenticator()
            auth.authenticate()
            print(f"回到主選單")

        elif choice == "2":
            print("\n1.使用帳號內已跟隨的人做匯入(請先執行登入帳號，預設使用第一個登入的)")
            print("2.手動輸入作者網址")
            print("3.列出所有資料")
            print("4.查詢資料")
            print("5.離開")
            while True:
                choice = input("請輸入選項:")
                if choice in ["1", "2", "3", "4", "5"]:
                    break
                else:
                    print("無效的選項，請輸入1到5之間的數字。")
            database = DatabaseManager()
            if choice == "1":
                database.close()
                follow = FollowScraper()
                follow.run()
            elif choice == "2":
                while True:
                    url = input("請輸入作者網址(輸入完成後請按兩次 Enter 即可):")
                    if url:
                        database.add_author_url(url)
                    else:
                        break
            elif choice == "3":
                urls = database.get_all_author_urls()
                print("所有作者網址:")
                for url in urls:
                    print(url)
            elif choice == "4":
                url = input("請輸入作者網址:")
                result=database.search_author_url(url)
                if result:
                    print(f"{url}存在")
                else:
                    print("作者網址不存在")
            elif choice == "5":
                database.close()
                break
                
        elif choice == "3":
            print("\n請問查詢場次")
            print("1.查詢FF場次")
            print("2.查詢其他(將由使用者自行輸入關鍵字)")
            print("3.離開")
            while True:
                choice = input("請輸入選項:")
                if choice in ["1", "2", "3"]:
                    break
                else:
                    print("無效的選項，請輸入1到3之間的數字。")
            if choice == "1":
                while True:
                    session_choice = input("請問要查詢哪一場次?(預設為FF44)\n請輸入場次(預設為FF44，使用預設直接 Enter 即可):") or "44"
                    if session_choice.isdigit():
                        break
                    else:
                        print("無效的選項，請輸入數字。")
                crawler = TwitterCrawler(
                    output_html="output.html",
                    download_dir="downloaded_images",
                    headless=False,
                    sessions_number=session_choice
                )
                crawler.run()
            elif choice == "2":
                keywords = []
                while True:
                    keyword = input("請輸入關鍵字(輸入完成後請按兩次 Enter 即可):")
                    if keyword:
                        keywords.append(keyword)
                    else:
                        break
                crawler = TwitterCrawler(
                    output_html="output.html",
                    download_dir="downloaded_images",
                    headless=False,
                    sessions_number=None,
                    custom_keywords=keywords
                )
                crawler.run()
            
        elif choice == "4":
            break

if __name__ == "__main__":
    main()

