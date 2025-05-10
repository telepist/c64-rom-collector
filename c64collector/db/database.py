"""
Database operations for the ROM collector.
"""
import sqlite3


class DatabaseManager:
    def __init__(self, db_path='c64_games.db'):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self.conn
        
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            
    def commit(self):
        """Commit changes to the database."""
        if self.conn:
            self.conn.commit()
            
    def execute(self, sql, params=None):
        """
        Execute a SQL statement.
        
        Args:
            sql (str): The SQL statement
            params (tuple, optional): Parameters for the SQL statement
            
        Returns:
            The cursor object after execution
        """
        if params:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
        
    def executemany(self, sql, params_list):
        """
        Execute a SQL statement with many parameter sets.
        
        Args:
            sql (str): The SQL statement
            params_list (list): List of parameter tuples
            
        Returns:
            The cursor object after execution
        """
        return self.cursor.executemany(sql, params_list)
        
    def fetchall(self):
        """Fetch all results from the last query."""
        return self.cursor.fetchall()
        
    def fetchone(self):
        """Fetch one result from the last query."""
        return self.cursor.fetchone()
        
    def create_schema(self):
        """Create the database schema."""
        # Create games table
        self.execute('''CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            source_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            clean_name TEXT NOT NULL,
            format TEXT NOT NULL,
            collection TEXT NOT NULL,
            format_priority INTEGER NOT NULL DEFAULT 0,
            is_multi_part INTEGER NOT NULL DEFAULT 0,
            part_number INTEGER NOT NULL DEFAULT 0
        )''')
            
        # Create indexes
        self.execute('CREATE INDEX IF NOT EXISTS idx_games_clean_name ON games (clean_name)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_games_format_priority ON games (format_priority)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_games_format ON games (format)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_games_collection ON games (collection)')
        
        self.commit()
        
    def reset_schema(self):
        """Drop and recreate the schema."""
        self.execute('DROP TABLE IF EXISTS games')
        self.create_schema()
        
    def insert_game(self, game_data):
        """
        Insert a game into the database.
        
        Args:
            game_data (dict): Game data dictionary
            
        Returns:
            int: The inserted row ID
        """
        self.execute('''
            INSERT INTO games (
                source_path, original_name, clean_name, format, 
                collection, format_priority, is_multi_part, part_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_data['source_path'],
            game_data['original_name'],
            game_data['clean_name'],
            game_data['format'],
            game_data['collection'],
            game_data['format_priority'],
            game_data['is_multi_part'],
            game_data['part_number']
        ))
        return self.cursor.lastrowid
