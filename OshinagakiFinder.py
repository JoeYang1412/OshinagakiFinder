import re
import time
import urllib.request
import os
import random
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, ElementHandle, Page
from fake_useragent import UserAgent
from logger import LoggerManager
from database import DatabaseManager
import requests


class TwitterCrawler:
    """
    TwitterCrawler is a tool for crawling Twitter (X), searching for specific authors' tweets, and downloading images.
    Usage:
    1. Create a TwitterCrawler object.
    2. Use the run() method to start crawling.
    3. Wait for it to finish, then check the output HTML file.
    4. Close the browser.
    args:
        output_html: The name of the HTML file to save the results.
        download_dir: The directory to save downloaded images.
        headless: Whether to run the browser in headless mode.
        sessions_number: The session number used to generate keywords.
        custom_keywords: A list of custom keywords.
    methods:
        generate_keywords: Generate keywords.
        run: Start crawling.
        _crawl_author_until_success: Retry crawling a single author until successful.
        _handle_crawl_error: Error handling logic when an error occurs.
        _handle_error_single_account: Error handling when a single account encounters a loading error.
        _handle_error_multi_account: Error handling in multi-account mode when a loading error occurs.
        _reopen_context_and_test: Reopen context and test.
        _wait_and_reopen_context_first_account: Wait and reopen context.
        _create_new_context: Create a new context.
        crawl_author: Crawl author's tweets and detect loading errors.
        init_browser: Initialize the browser.
        close_context: Close the context.
        close_browser: Close the browser.
        stop_playwright: Stop Playwright.
        _check_empty_state: Check if the page is empty.
        check_cell_divs: Check for loading errors.
        extract_tweet_id: Extract tweet ID.
        smooth_scroll: Scroll to load more tweets.
        generate_twitter_search_url: Generate Twitter search URL.
        download_image: Download image.
        generate_html: Generate HTML file.
    """
    # --------------------------
    # Parameters
    # --------------------------

    # One month in seconds
    ONE_MONTH_SECONDS = 2592000

    # If the same tweet appears consecutively up to this threshold, it is considered "end or stuck"
    DUPLICATE_THRESHOLD = 3

    # Maximum number of retries for the same account in case of errors
    MAX_REOPEN_TIMES = 3

    # First wait for 60 seconds, then 90 seconds for the second time (and thereafter)
    WAIT_SEQUENCE = [60, 90]
    
    logger = LoggerManager("scraper").get_logger()

    def __init__(
        self,
        output_html="output.html",
        download_dir="downloaded_images",
        headless=False,
        sessions_number=None,
        custom_keywords=None
    ):
        self.output_html = output_html
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)

        self.headless = headless
        self.ua = UserAgent()

        # Track the current account index
        self.current_storage_index = 0

        # Query results
        self.all_results = []

        # Playwright related
        self._playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Accumulate error count (used to decide whether to wait 60 or 90 seconds)
        self.global_fail_count = 0

        self.storage_states = self.get_storage_states()
        # generate keywords
        self.KEYWORDS = self.generate_keywords(sessions_number, custom_keywords)

    def get_storage_states(self):
        """
        Get all available storage states (cookies) in the auth directory.
        """
        return sorted([
            str(path) for path in Path("./auth").glob("twitter_storage_*.json")
            if re.match(r"twitter_storage_\d+\.json$", path.name)
    ])
    def generate_keywords(self, sessions_number, custom_keywords):
        """ 
        Generate keywords based on sessions_number, or use custom keywords entirely 
        """

        if custom_keywords:
            # User fully custom mode
            keywords = [word.strip() for word in custom_keywords if word.strip()]
        else:
            # Default keyword mode (but the middle number can change)
            base_keywords = [
                "FancyFrontier{}", "開拓動漫祭{}", "FF{}", "FancyFrontier", "FF", "開拓動漫祭",
                "Fancy Frontier", "FANCEFRONTIER", "FANCE FRONTIER"
            ]
            keywords = [kw.format(sessions_number) if "{}" in kw else kw for kw in base_keywords]

        return keywords

    # --------------------------
    # Core: run
    # --------------------------

    def run(self):
        db = DatabaseManager()
        author_urls = db.get_all_author_urls()

        # Query time range
        until_ts = int(time.time())
        since_ts = until_ts - self.ONE_MONTH_SECONDS

        # Initialize the browser
        init_result=self.init_browser()
        if init_result==False:
            
            return False
        
        # Start crawling
        for author_url in author_urls:
            author_id = author_url.replace("https://x.com/", "")
            self.logger.info(f"Preparing to search author : {author_id}")
            print(f"準備搜尋作者 : {author_id}")

            search_url = self.generate_twitter_search_url(
                self.KEYWORDS, author_id, until_ts, since_ts
            )

            # Keep trying until successful
            self._crawl_author_until_success(search_url, author_url)

        # All authors processed => Output HTML
        self.generate_html(self.all_results, self.output_html)

        # Close the browser
        self.close_browser()
        self.stop_playwright()
        self.logger.info("All authors processed, program finished.")
        print("所有作者處理完畢，程式結束。")

    # --------------------------
    # Core: Search until successful
    # --------------------------
    def _crawl_author_until_success(self, search_url, fallback_author):
        """
        If an error occurs during crawling 
        => enter _handle_crawl_error() 
        => handle errors based on the number of accounts 
        => reopen the page / switch accounts / wait 60-90 seconds, then try again.
        """
        while True:
            # Random wait before each attempt
            sleep_sec = random.uniform(1.0, 3.0)
            self.logger.info(f"Preparing to search {search_url}, waiting for {sleep_sec:.1f} seconds...")
            time.sleep(sleep_sec)

            author_name, images = self.crawl_author(search_url)
            # crawl_author may return:
            # (False, 1) => Error
            # (False, 0) => End of results
            # (None, []) => Empty page
            # (author_name, [paths]) => Success

            # As long as it's not (False, 1), it's considered "successful or acceptable", add the result and exit
            if author_name is False and images == 1:
                self.logger.info("Detected loading error, entering error handling")
                print("偵測到載入錯誤，進入錯誤處理...")
                self._handle_crawl_error(search_url, fallback_author)
            else:
                # Considered successful or acceptable
                self.all_results.append({
                    "author": author_name if author_name else fallback_author,
                    "images": images if isinstance(images, list) else []
                })
                self.logger.info("Author processed successfully")
                print("此作者搜尋處理成功")
                return

    # --------------------------
    # Handling logic after a loading error occurs
    # --------------------------
    def _handle_crawl_error(self, search_url, fallback_author):
        """
        Error handling logic:
          1) If there is only one account (or no account) => 
          reopen the same account 3 times consecutively; if it still fails => 
          wait 60->90 seconds, then retry from the outer loop.

          2) If there are multiple accounts => 
          try 3 times on the "current account", if it fails, switch to the next account... if all fail => 
          wait 60->90 seconds + return to the initial account.

        Throughout the process, only the context is closed/reopened, not the entire browser.
        This function only performs one "round of attempts"; if it fails, it returns to the outer `_crawl_author_until_success()` function, and if an error occurs again, it will enter here again.
        """

        num_accounts = len(self.storage_states)
        if num_accounts <= 1:
            # Single account mode
            self._handle_error_single_account(search_url, fallback_author, account_idx=0 if num_accounts == 1 else None)
        else:
            # Multi-account mode
            self._handle_error_multi_account(search_url, fallback_author)

    def _handle_error_single_account(self, search_url, fallback_author, account_idx):
        """
        Single account mode
        """
        # retry 3 times
        for _ in range(self.MAX_REOPEN_TIMES):
            if self._reopen_context_and_test(search_url, fallback_author, account_idx):
                return  
        # if all fail => wait 60->90 seconds
        self._wait_and_reopen_context_first_account()
        # After waiting, the function ends and returns to the outer _crawl_author_until_success to try again => 
        # if it fails again => it will enter here again

    def _handle_error_multi_account(self, search_url, fallback_author):
        """
        Multi-account mode:
          - Start from current_storage_index, try each account 3 times (reopen context).
          - If any account succeeds => end, and update current_storage_index to the successful account.
          - If all attempts fail => wait 60->90 seconds + return to account 0, until successful.
        """
        start_idx = self.current_storage_index
        n = len(self.storage_states)

        tested_count = 0
        success_account = None
        while tested_count < n:
            acc_idx = (start_idx + tested_count) % n
            self.logger.info(f"Switching to account {acc_idx}...")
            print(f"切換到帳號 {acc_idx}...")
            for _ in range(self.MAX_REOPEN_TIMES):
                if self._reopen_context_and_test(search_url, fallback_author, acc_idx):
                    success_account = acc_idx
                    break
            if success_account is not None:
                break
            tested_count += 1

        if success_account is not None:
            # Success => Update current_storage_index
            self.current_storage_index = success_account
            return
        else:
            # All accounts failed => wait 60->90 seconds, then set the account index to 0
            self.current_storage_index = 0
            self._wait_and_reopen_context_first_account()

    def _reopen_context_and_test(self, search_url, fallback_author, account_idx):
        """
        1) close_context()
        2) Create a new context
        3) Wait briefly, then call crawl_author() to test if it is still (False, 1) error
        4) If not => return True indicating success; if still (False, 1) => return False
        """
        self.close_context()
        self._create_new_context(account_idx)

        wait_s = random.uniform(1, 2)
        self.logger.info(f"Reinitialization complete, waiting for {wait_s:.1f} seconds before continuing...")
        print(f"重新初始化完成，等待 {wait_s:.1f} 秒後繼續...")
        time.sleep(wait_s)

        # Test if the error still exists
        author_name, images = self.crawl_author(search_url)
        if author_name is False and images == 1:
            self.logger.info("Error still occurs after restart, continuing to retry...")
            print("重啟後仍有錯誤，繼續重試...")
            # error still exists
            return False
        else:
            self.logger.info("Successfully restarted, continuing...")
            print("重新啟動後成功，繼續進行...")
            # success
            self.all_results.append({
                "author": author_name if author_name else fallback_author,
                "images": images if isinstance(images, list) else []
            })
            return True

    def _wait_and_reopen_context_first_account(self):
        """
        Wait for 60->90 seconds, then reopen the context with account 0.
        """
        self.global_fail_count += 1
        wait_sec = self.WAIT_SEQUENCE[0] if self.global_fail_count == 1 else self.WAIT_SEQUENCE[1]
        self.logger.info(f"All account tests failed, waiting for {wait_sec} seconds before returning to the initial account...")
        print(f"所有帳號測試失敗，等待 {wait_sec} 秒後回到初始帳號...")
        time.sleep(wait_sec)
        self.close_context()
        self._create_new_context(0)

    def _create_new_context(self, account_idx):
        """
        Create a new context on the existing browser; if no account is found, return False
        """
        try:
            if not self.storage_states:
                raise FileNotFoundError()
            path_candidate = Path(self.storage_states[account_idx])
            if not path_candidate.exists():
                raise FileNotFoundError()
            storage_state_file = str(path_candidate)
        except FileNotFoundError:
            storage_state_file = None
            self.logger.error("No accounts found, unable to search without login status.")
            print(f"找不到任何帳號，無法在無登入狀態下搜尋。")
            return False


        self.context = self.browser.new_context(
            user_agent=self.ua.random,
            storage_state=storage_state_file
        )
        self.page = self.context.new_page()
        self.logger.info(f"Browser context initialized (account index={account_idx}).")
        print(f"瀏覽器參數初始化完成 (帳號索引={account_idx})")
    
    # this function is not used
    """
    def ensure_checkbox_unchecked(page: Page):
       # 等待 checkbox 加載
        page.goto("https://x.com/settings/search")
        page.wait_for_selector('[data-testid="searchSettings-hideSensitiveContent"] input[type="checkbox"]', timeout=5000)

        # 找到 checkbox 和 label
        checkbox_label = page.query_selector('[data-testid="searchSettings-hideSensitiveContent"]')
        checkbox = checkbox_label.query_selector("input[type='checkbox']")

        # 只有在 checkbox 已勾選時，才執行取消勾選
        if checkbox and checkbox.is_checked():
            checkbox_label.click()
            self.logger.info("Checkbox unchecked")
        else:
            self.logger.info("Already unchecked, no action needed")
    """
    # --------------------------
    # Actual crawling logic crawl_author
    # --------------------------
    def crawl_author(self, search_url: str):
        """
        1. page.goto(search_url)
        2. Check for cellInnerDiv or emptyState, otherwise consider it an error -> return (False, 1)
        3. Parse tweets (article[data-testid="tweet"])
        4. If there are keywords + images => download
        5. Return (author_name, downloaded_paths)
        6. If the first tweet after scrolling remains unchanged and the duplicate count reaches the limit, consider it the end
        """
        self.page.goto(search_url)

        # Wait for 5 seconds to see if cellInnerDiv can be loaded
        try:
            self.page.wait_for_selector('div[data-testid="cellInnerDiv"]', timeout=5000)
        except:
            # If emptyState is found, it is considered an empty page
            if self._check_empty_state():
                self.logger.info("No tweets found, should be an empty page")
                print("沒有找到推文，無搜尋結果")
                return None, []
            else:
                # If neither cellInnerDiv nor emptyState is found, it is considered an error
                self.logger.info("Loading error detected, will use error handling")
                return False, 1

        # After the initial check through cellInnerDiv, perform "check_cell_divs" to determine if there are any errors
        if not self.check_cell_divs(self.page):
            self.logger.info("Loading error detected, will use error handling")
            print("載入錯誤，將使用錯誤處理")
            return False, 1
        
        is_first_process = True
        processed_tweet_ids = set()
        downloaded_paths = []
        author_name = ""
        duplicate_count = 0
        last_seen_tweet_id = None 

        while duplicate_count < self.DUPLICATE_THRESHOLD:
            articles = self.page.query_selector_all('article[data-testid="tweet"]')

            if not articles:
                self.logger.info("No results found")
                # No results found
                break  

            current_tweet_ids = set()
            # Record the ID of the first tweet on the current page
            first_tweet_id = None  

            for index, article in enumerate(articles):
                # First tweet ID
                if index == 0:  
                    first_tweet_id = self.extract_tweet_id(article)
                
                # Check if the tweet contains other posts
                if article.query_selector('div[data-testid="testCondensedMedia"]'):
                    self.logger.info("This tweet contains other posts")
                    continue  
                
                raw_tweet_id = self.extract_tweet_id(article)
                if not raw_tweet_id:
                    continue

                if raw_tweet_id in processed_tweet_ids:
                    self.logger.info(f"Tweet {raw_tweet_id} has already been processed, skipping")
                    continue

                current_tweet_ids.add(raw_tweet_id)

                # get author name
                user_div = article.query_selector('div[data-testid="User-Name"]')
                if user_div:
                    name_txt = user_div.inner_text().replace("·", "").strip()
                    name_txt = " ".join(name_txt.split())
                    author_name = name_txt

                # get tweet content
                text_div = article.query_selector('div[data-testid="tweetText"]')
                content = ""
                if text_div:
                    lines = [l.strip() for l in text_div.inner_text().splitlines() if l.strip()]
                    content = "\n".join(lines)

                self.logger.info(f"[New Tweet] tweet_id={raw_tweet_id}, author={author_name}")
                for line in content.splitlines():
                    self.logger.info(f"Content: {line}")

                # Check if it contains keywords, if so, then check if there are images
                if any(re.search(rf"{re.escape(k)}", content) for k in self.KEYWORDS):
                    images = article.query_selector_all('div[data-testid="tweetPhoto"] img')
                    if images:
                        for idx, img_el in enumerate(images, start=1):
                            img_url = img_el.get_attribute("src")
                            if img_url:
                                img_url = re.sub(r"\?.*", "", img_url) + "?format=jpg&name=orig"
                                local_path = self.download_image(img_url, author_name, idx)
                                downloaded_paths.append(local_path)
                    else:
                        self.logger.info("This tweet contains keywords but no images.")

            if first_tweet_id == last_seen_tweet_id and not is_first_process:
                duplicate_count += 1
                self.logger.info(f"First tweet after scrolling remains unchanged, duplicate count: {duplicate_count}/{self.DUPLICATE_THRESHOLD}")
                print(f"滾動後第一篇推文未變，重複次數: {duplicate_count}/{self.DUPLICATE_THRESHOLD}")
                is_first_process = False
            else:
                # Reset the duplicate count
                duplicate_count = 0  
                # Update the last seen tweet ID
                last_seen_tweet_id = first_tweet_id 
                # Update the processed tweet IDs
                processed_tweet_ids.update(current_tweet_ids)  
                is_first_process = False

            # Scroll to load more tweets
            self.smooth_scroll(self.page)

        self.logger.info("Author query completed")
        print("作者查詢完成")
        return author_name, downloaded_paths 

    # --------------------------
    # Browser/Context management
    # --------------------------
    def init_browser(self):
        if not self._playwright:
            self._playwright = sync_playwright().start()

        if self.browser:
            self.close_browser()

        self.browser = self._playwright.chromium.launch(headless=self.headless)
        init_result=self._create_new_context(self.current_storage_index)
        if init_result==False:
            print("初始化瀏覽器失敗")
            self.close_browser()
            self.stop_playwright()
            return False
        self.logger.info("Browser initialization complete.")
        print("瀏覽器初始化完成。")

    def close_context(self):
        if self.page:
            self.page.close()
            self.page = None
        if self.context:
            self.context.close()
            self.context = None

    def close_browser(self):
        self.close_context()
        if self.browser:
            self.browser.close()
            self.browser = None

    def stop_playwright(self):
        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    # --------------------------
    def _check_empty_state(self):
        # Check if the page is empty
        try:
            self.page.wait_for_selector('div[data-testid="emptyState"]', timeout=3000)
            return True
        except:
            return False

    def check_cell_divs(self, page: Page) -> bool:
        """
        Check if there is an error. If there is a button but no tweet/link, it indicates a loading error.
        """
        cell_divs = page.query_selector_all('div[data-testid="cellInnerDiv"]')
        for cell in cell_divs:
            has_link = cell.query_selector('a[href^="/"]') is not None
            has_tweet = cell.query_selector('article[data-testid="tweet"]') is not None
            has_button = cell.query_selector('button') is not None

            if not has_button and not has_link and not has_tweet:
                return True 
            elif has_button and not has_link and not has_tweet:
                # Loading error
                return False  
        return True

    def extract_tweet_id(self, article: ElementHandle) -> str:
        link = article.query_selector('a[href*="/status/"]')
        if link:
            href = link.get_attribute("href") or ""
            match = re.search(r"/status/(\d+)", href)
            if match:
                return match.group(1)
        return ""

    def smooth_scroll(self, page: Page):
        self.logger.info("Scrolling the page...")
        vh = page.evaluate("window.innerHeight")
        for _ in range(10):
            amt = random.uniform(vh/10, vh/2)
            page.mouse.wheel(0, amt)
            time.sleep(random.uniform(0.1, 0.5))

    def generate_twitter_search_url(self, keywords, author, until_ts, since_ts):
        until_date = datetime.fromtimestamp(until_ts).strftime('%Y-%m-%d')
        since_date = datetime.fromtimestamp(since_ts).strftime('%Y-%m-%d')
        kq = " OR ".join([f'"{kw}"' for kw in keywords])
        return (f"https://x.com/search?q=({kq}) (from:{author}) "
                f"until:{until_date} since:{since_date}")

    def download_image(self, img_url: str, author: str, index: int) -> Path:
        safe_author = re.sub(r"[^a-zA-Z0-9_\-]+", "_", author) if author else "unknown"
        filename = f"{safe_author}_{index}.jpg"
        local_path = self.download_dir / filename
        max_retries = 3
        header = {"User-Agent": self.ua.random}
        for attempt in range(max_retries):
            try:
                r = requests.get(img_url, timeout=10, headers=header)
                r.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(r.content)
                self.logger.info(f"Image downloaded: {local_path}")
                print(f"圖片下載完成: {local_path}")
                break
            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP error occurred: {e}")
                self.logger.info(f"Failed to download {img_url}, attempt {attempt + 1} of {max_retries}, error: {e}")
                print(f"無法下載 {img_url}，嘗試 {attempt + 1} 次，共 {max_retries} 次，錯誤: {e}")
            except requests.exceptions.Timeout:
                self.logger.error(f"Request timed out: {img_url}")
                self.logger.info(f"Failed to download {img_url}, attempt {attempt + 1} of {max_retries}, error: {e}")
                print(f"無法下載 {img_url}，嘗試 {attempt + 1} 次，共 {max_retries} 次，錯誤: {e}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error during requests to {img_url}: {e}")
                self.logger.info(f"Failed to download {img_url}, attempt {attempt + 1} of {max_retries}, error: {e}")
                print(f"無法下載 {img_url}，嘗試 {attempt + 1} 次，共 {max_retries} 次，錯誤: {e}")


        return local_path

    def generate_html(self, results: list[dict], output_file: str):
        html_lines = [
            "<html><head><meta charset='utf-8'><title>抓取結果</title></head><body>",
            "<h1>爬取結果</h1>"
        ]
        for item in results:
            author = item["author"]
            images = item["images"]
            html_lines.append(f"<h2>作者: {author}</h2>")
            if not images:
                html_lines.append("<p>沒有找到任何圖片</p>")
                continue
            for img_path in images:
                rel_path = os.path.relpath(img_path, start='.')
                html_lines.append(
                    f"<div><img src='{rel_path}' style='max-width:600px;'/></div>"
                )
        html_lines.append("</body></html>")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(html_lines))
        self.logger.info(f"HTML has been output to {output_file}")
        print(f"HTML 輸出至 {output_file}")
