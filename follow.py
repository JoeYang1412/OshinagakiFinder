import time
from pathlib import Path
from playwright.sync_api import sync_playwright, ElementHandle, Page
from database import DatabaseManager
from logger import LoggerManager
class FollowScraper:
    """
    FollowScraper is responsible for extracting author URLs from followed users and saving them to the database.
    args:
        user_number: Represents the user number, default is 1.

    methods:
        extract_followed_users: Extracts author URLs from followed users.
        insert_followed_users_to_db: Saves the extracted author URLs to the database.
        run: Executes the process of extracting author URLs.
    """
    logger = LoggerManager("follow").get_logger()
    def __init__(self, user_number=None):
        if user_number is None:
            user_number = 1
        index = user_number - 1
        self.storage_path = Path(f"./auth/twitter_storage_{index}.json")
        self.followed_users = []

    def extract_followed_users(self, page:Page):
        max_attempts = 10
        same_count_times = 0
        while True:
            page.wait_for_selector('button[data-testid="UserCell"]', timeout=10000)
            user_cells = page.query_selector_all('button[data-testid="UserCell"]')
            new_count = 0
            for user_cell in user_cells:
                link = user_cell.query_selector('a[href^="/"]')
                if link:
                    href = link.get_attribute("href")
                    if href:
                        full_url = f"https://x.com{href}"
                        if full_url not in self.followed_users:
                            self.followed_users.append(full_url)
                            new_count += 1
            if new_count == 0:
                same_count_times += 1
            else:
                same_count_times = 0
            if same_count_times >= max_attempts:
                break
            page.mouse.wheel(0, 300)
        return self.followed_users

    def insert_followed_users_to_db(self, users):
        db = DatabaseManager()
        for user in users:
            db.add_author_url(user)
        db.close()

    def run(self):
        if not self.storage_path.exists():
            self.logger.info("No login state found.")
            print("無驗證狀態檔案，請先執行驗證。")
            return
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=str(self.storage_path))
            page = context.new_page()
            page.goto("https://x.com/home")
            time.sleep(3)
            profile_link = page.query_selector('a[data-testid="AppTabBar_Profile_Link"]')
            if not profile_link:
                self.logger.info("No profile link found.")
                return
            user_name = profile_link.get_attribute("href").lstrip("/")
            if not user_name:
                self.logger.info("Can't get username.")
                return
            page.goto(f"https://x.com/{user_name}/following")
            time.sleep(3)
            results = self.extract_followed_users(page)
            self.insert_followed_users_to_db(results)
            context.close()
            browser.close()
            self.logger.info("Followed users have been saved to database.")
            print("已將已追蹤的使用者儲存至資料庫。")

if __name__ == "__main__":
    FollowScraper(user_number=0).run()
