from pathlib import Path
from playwright.sync_api import sync_playwright
from logger import LoggerManager
class TwitterAuthenticator:
    """
    TwitterAuthenticator is responsible for manually logging into Twitter (X) and saving the login state to a local JSON file.

    Usage steps:
    1. Create a TwitterAuthenticator object.
    2. Call the authenticate() method, which will automatically open a browser (non-headless mode).
    3. Manually log in to Twitter (X) in the browser.
    4. After logging in, the program will save the browser's login state to a JSON file.
    5. In the future, you can directly use this file as the login state without logging in again.

    Note:
    - By default, it will check if "twitter_storage_X.json" exists in the current program execution path,
      and if so, it will continue to increment the number. For example: twitter_storage_0.json, twitter_storage_1.json...
    - By default, it will save the state only after detecting a successful login (i.e., redirecting to "https://x.com/home*").

    methods:
        
        _get_next_storage_path: Finds the next available filename (twitter_storage_X.json).
        authenticate: Executes the manual login process.

    """

    logger = LoggerManager("authenticate").get_logger()

    def __init__(self):
        """
        Initialize TwitterAuthenticator, no parameters are required by default.
        """
        self.storage_state_path = None

    def _get_next_storage_path(self) -> Path:
        """
        Finds the next available filename (twitter_storage_X.json).
        If twitter_storage_0.json already exists, it will generate twitter_storage_1.json, and so on.
        """
        auth_dir = Path("./auth")
        auth_dir.mkdir(parents=True, exist_ok=True)  # 確保 `auth` 目錄存在

        i = 0
        while Path(f"./auth/twitter_storage_{i}.json").exists():
            i += 1
        return Path(f"./auth/twitter_storage_{i}.json")

    def authenticate(self) -> None:
        """
        Execute the manual login process:
        1. Open the Chromium browser (non-headless mode).
        2. Ask the user to manually log in to Twitter (X) in the browser.
        3. Wait until the URL changes to "https://x.com/home*", indicating a successful login.
        4. Save the current browser's login state to a JSON file.
        5. Display a success message and close the browser.
        """
        self.storage_state_path = self._get_next_storage_path()

        with sync_playwright() as p:
            # Launch Chromium browser, headless=False means the browser interface will be displayed
            browser = p.chromium.launch(headless=False)
            
            # Create a new browser context
            context = browser.new_context()

            # Create a new page
            page = context.new_page()

            # Navigate to the Twitter (X) homepage
            page.goto("https://x.com/")  

            self.logger.info("Please manually log in to Twitter (X) in the browser...")
            print("請在瀏覽器中手動登入 Twitter (X)。")
            self.logger.info("Waiting for the page to navigate to https://x.com/home ...")
            print("等待網頁跳轉至 https://x.com/home ...")

            # Wait for the URL to change to "https://x.com/home*"
            page.wait_for_url("https://x.com/home*", timeout=0)

            self.logger.info(f"Detected URL change: {page.url}, login successful!")
            print(f"網址已跳轉至 {page.url}，登入成功！")
            self.logger.info("Starting to save login state...")
            print("儲存登入狀態...")

            # Save the current browser's login state to a JSON file
            context.storage_state(path=str(self.storage_state_path))
            self.logger.info(f"Login state has been saved to {self.storage_state_path}, you can load this file directly in the future to skip logging in again.")
            print(f"登入狀態已儲存，下次可省略再次登入。")
            context.close()
            browser.close()
            print("瀏覽器已關閉，驗證結束。")
