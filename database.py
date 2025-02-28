import sqlite3

class DatabaseManager:
    """
    Manage the SQLite database for Twitter author URLs
    """

    def __init__(self, db_path="twitter_authors.db"):
        """
        Initialize the database connection
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        Create the 'authors' table if it does not exist
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE
            )
        ''')
        self.conn.commit()

    def get_all_author_urls(self):
        """
        Retrieve all author URLs from the database
        """
        self.cursor.execute("SELECT url FROM authors")
        return [row[0] for row in self.cursor.fetchall()]
    
    def search_author_url(self, url: str):
        """
        Check if the specified author URL exists
        """
        self.cursor.execute("SELECT url FROM authors WHERE url = ?", (url,))
        return self.cursor.fetchone() is not None

    def add_author_url(self, url: str):
        """
        Add an author URL to the database
        """
        try:
            self.cursor.execute("INSERT INTO authors (url) VALUES (?)", (url,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # URL already exists, ignore

    def remove_author_url(self, url: str):
        """
        Remove the specified author URL from the database
        """
        self.cursor.execute("DELETE FROM authors WHERE url = ?", (url,))
        self.conn.commit()

    def close(self):
        """
        Close the database connection
        """
        self.conn.close()

