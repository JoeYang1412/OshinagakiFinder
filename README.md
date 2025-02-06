# OshinagakiFinder

This project is a query tool based on `playwright`, primarily used to look up Oshinagaki on Twitter.  
Users can set custom keywords to find Oshinagaki for a specific event, or use default search conditions.

## Features
- **Terminal Interface**: Simple and user-friendly, no need to manually define parameters
- **Automatic Login Management**: Uses `playwright` to handle Twitter login sessions, reducing repeated manual logins
- **Author Management**: Manage author URLs through a database, supporting both manual input or automatic account import
- **Keyword Search**: Allows custom or default keywords to find Oshinagaki
- **Image Download**: Any tweet that matches the criteria will have its images automatically downloaded to the `downloaded_images` directory
- **Error Handling & Stability**: Includes retry mechanisms and logging, ensuring stable data collection
- **Multi-account Support**: Supports switching between multiple accounts to bypass restrictions

## Installation and Setup
### Using Release
Download the release version directly.

### Using Source Code
#### 1. Clone the repository
```
git clone https://github.com/JoeYang1412/OshinagakiFinder.git
```
#### 2. Install required packages
Make sure your environment has Python 3.8+ installed, then run:
```sh
pip install -r requirements.txt
playwright install
```
#### 3. Run the main program
```sh
python main.py
```

## How to Use
Warning: The automatic login uses `playwright` and stores session data in `./auth`. Keep it secure and do not share it.  
Warning: The automatic login uses `playwright` and stores session data in `./auth`. Keep it secure and do not share it.  
Warning: The automatic login uses `playwright` and stores session data in `./auth`. Keep it secure and do not share it.

Note: This tool only looks up results from one month prior to “now.”

If an error occurs during the data collection process, the tool will attempt to switch accounts to continue (if multiple accounts are available).

Below is just a general workflow.  
For more details, see `manual.md`.  
Data collection results will be saved to `output.html`. Open it directly after the process finishes.  

**Note:**
This tool requires users to log in to Twitter to perform operations. The access permissions (cookies/session) after logging in will be stored on your local machine. The developer cannot access or control your account information. Please ensure the security of your login. The developer is not responsible for any account anomalies or data loss resulting from the use of this tool.  
For more details, please refer to the disclaimer.For more details, please refer to the disclaimer.

The following interface is actually in Chinese, and this is the translated version:
```
1. Login Validation
2. Author Database
3. Query All Authors’ Oshinagaki
4. Exit
Enter an option:

# 1 Login Validation
# This will launch the browser to request login. After successful login, the session will be saved.

# 2 Author Database
1. Use followed accounts to import (log in first, uses the first logged-in account by default)
# Opens the browser to grab followed accounts from the logged-in account
2. Manually input author URLs
# Manually add author URLs. Note: if option 1 was used, new URLs will be appended
3. List all records
# Lists all entries in the database
4. Query a record
# Checks if a given URL exists in the database
5. Exit

# 3 Query All Authors’ Oshinagaki
1. Query FF events
# Default is 44; enter another number for a different event
2. Query others (you will enter your own keyword)
# Can query other keywords such as C105 or CWT
3. Exit

# 4 Exit
```

## Known Issues
1. Finding Oshinagaki is heavily dependent on keywords
2. Any tweet containing the keyword with an image is captured, so irrelevant posts might be included
3. If an interruption occurs, no data is saved to `output.html` prior to the failure; only images are retained
4. Unknown errors may occur

## Disclaimer
1. **This project is for academic research and personal purposes only**; do not use for **commercial activities or privacy violations**.
2. **Follow Twitter’s Terms of Service**; this tool is for research and testing only, and the developer **bears no legal responsibility** for user behavior.
3. **Avoid excessive scraping** to prevent unnecessary strain on Twitter’s servers.
4. If Twitter changes its site structure or security policies, causing this tool to fail, the developer **is not obligated to fix or maintain it**.
5. Using this project means **you accept all risks**, including account suspension or IP restriction.

## Contributing
Found an issue or have suggestions? You can help by:  

- Reporting issues: Check the Issues page or create a new issue if not listed.  
- Submitting modifications: Fork the project, make improvements, and create a Pull Request.  
- Updating documentation: If you find errors or omissions, feel free to contribute fixes.  

Thank you for your contributions to improve this project!😊

## 簡介
本專案是一個基於 `playwright` 的查詢工具，主要用來查詢 Twitter 上的同人展品書 。  
使用者可以自訂關鍵字來查詢特定場次的品書資訊，或是使用預設的搜尋條件。

## 功能概覽
- **終端介面**：提供簡單易用的終端操作，無需手動編寫參數
- **自動登入管理**：透過 `playwright` 自動管理 Twitter 登入狀態，避免頻繁手動登入
- **作者管理功能**，可透過資料庫管理作者網址，支援手動輸入或從帳號自動加入
- **關鍵字搜尋**：允許使用者 **自訂關鍵字** 或使用 **預設關鍵字** 來搜尋品書資訊
- **圖片下載**：符合條件的推文圖片會自動下載到 `downloaded_images` 目錄
- **錯誤處理與穩定運行**：具備多次重試機制與日誌記錄，確保抓取過程穩定
- **支援使用多帳號**：可支援多帳號切換，遇到限制時可切換至其他帳號


## 安裝與環境設定
### 使用 release 版本
直接至 release 下載即可

### 使用 原始碼執行
#### 1. 下載或 clone 本專案
```
git clone https://github.com/JoeYang1412/OshinagakiFinder.git
```
#### 2. 安裝必要套件
請確保你的環境已安裝 Python 3.8 以上，然後執行：
```sh
pip install -r requirements.txt
playwright install
```
#### 3 執行主程式
```sh
python main.py
```

## 使用方式
警告:自動登入的實作方式由 `playwright` 處理，但登入狀態保存在本地 `./auth` 中，請保存好，勿任意外流  
警告:自動登入的實作方式由 `playwright` 處理，但登入狀態保存在本地 `./auth` 中，請保存好，勿任意外流  
警告:自動登入的實作方式由 `playwright` 處理，但登入狀態保存在本地 `./auth` 中，請保存好，勿任意外流

注意:本工具只能尋找由"現在"往前一個月的結果

若抓取過程中遇到錯誤，會嘗試切換帳號來繼續抓取(若有多個帳號可用的話)

底下僅為大致流程  
需要更詳細的說明請至 `manual.md` 查看  
抓取結果將會儲存至 `output.html`，抓取完後請直接打開即可 

注意事項：
本工具需要使用者登入 Twitter 來執行操作，登入後的存取權限（cookies/session）將儲存在您的本機，開發者無法存取或控制您的帳戶資訊。請自行確保登入安全性，若因使用本工具導致帳戶異常或資料遺失，開發者不承擔任何責任。  
詳請請參閱免責聲明
```
1.登入驗證
2.作者資料庫
3.查詢所有作者品書
4.離開
請輸入選項:

# 1 登入驗證
# 會直接啟動瀏覽器要求登入，登入完成後會儲存登入狀態

# 2 作者資料庫
1.使用帳號內已跟隨的人做匯入(請先執行登入帳號，預設使用第一個登入的) 
# 開啟瀏覽器抓取已登入帳號中已跟隨的人
2.手動輸入作者網址
# 可以手動加入作者網址。注意:若是已使用選項　1　者，則會往後面加
3.列出所有資料
# 列出資料庫中所有資料
4.查詢資料
# 查詢某網址是否位於資料庫中
5.離開

# 3 查詢所有作者品書
1.查詢FF場次
# 可查詢FF場次，預設使用44，若需查詢其他屆，請直接輸入屆數
2.查詢其他(將由使用者自行輸入關鍵字)
#可查詢其他關鍵字，如　C105，CWT　之類的
3.離開

# 4 離開

```

## 已知問題或錯誤
1. 抓取的品書非常依賴關鍵字
2. 只要有包含關鍵字且有帶圖片的都會被抓下來，所以可能會抓到不相關的東西
3. 抓取過程中可能因意外導致中斷，此前所有資料並不會保存至 `output.html`，而是只會保存品書圖片
4. 可能會發生未知錯誤

## 免責聲明

1. **本專案僅供學術研究與個人用途**，請勿用於**任何商業行為或侵犯隱私的用途**。
2. **請遵守 Twitter 的使用條款**，本工具僅作為技術研究與測試使用，開發者**不對使用者的行為負任何法律責任**。
3. **請勿過度爬取**，避免對 Twitter 伺服器造成不必要的負擔。
4. 若 Twitter 改變其網站架構或安全策略，導致本專案無法正常運行，開發者**無義務提供修復或維護**。
5. 使用本專案即代表**您同意自行承擔所有風險**，包括但不限於帳號被封鎖、IP 被限制等風險。

## 貢獻方式
發現問題或有建議？
您可以協助以下事項：  
回報問題：查看 Issues 頁面，或如果尚未回報，請創建新的 Issue。  
提交修改：Fork 專案、修改原始碼，並發起 Pull Request。  
增修相關文檔：若發現文件錯誤或缺失，歡迎進行補充並提交。  
感謝您的貢獻，讓這個專案變得更好！😊