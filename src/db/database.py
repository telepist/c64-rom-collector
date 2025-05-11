"""
Database operations for the ROM collector.
"""
import sqlite3
from ..config import DATABASE_PATH


class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        """Initialize the database manager."""
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
        """Execute a SQL statement."""
        if params:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
        
    def executemany(self, sql, params_list):
        """Execute a SQL statement with many parameter sets."""
        return self.cursor.executemany(sql, params_list)
        
    def fetchall(self):
        """Fetch all results from the last query."""
        return self.cursor.fetchall()
        
    def fetchone(self):
        """Fetch one result from the last query."""
        return self.cursor.fetchone()
        
    def create_schema(self):
        """Create the database schema."""
        # Create games table - stores unique games
        self.execute('''CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            clean_name TEXT NOT NULL
        )''')

        # Create game_versions table - stores collection-specific versions
        self.execute('''CREATE TABLE IF NOT EXISTS game_versions (
            id INTEGER PRIMARY KEY,
            game_id INTEGER NOT NULL,
            collection TEXT NOT NULL,
            format TEXT NOT NULL,
            format_priority INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )''')

        # Create game_parts table - stores individual files
        self.execute('''CREATE TABLE IF NOT EXISTS game_parts (
            id INTEGER PRIMARY KEY,
            version_id INTEGER NOT NULL,
            part_number INTEGER NOT NULL DEFAULT 0,
            source_path TEXT NOT NULL,
            original_name TEXT NOT NULL,
            FOREIGN KEY (version_id) REFERENCES game_versions(id)
        )''')
            
        # Create indexes
        self.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_games_clean_name ON games (clean_name)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_versions_game_id ON game_versions (game_id)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_versions_format ON game_versions (format)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_versions_collection ON game_versions (collection)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_versions_format_priority ON game_versions (format_priority)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_parts_version_id ON game_parts (version_id)')
        self.execute('CREATE INDEX IF NOT EXISTS idx_parts_part_number ON game_parts (part_number)')
        
        self.commit()
        
    def reset_schema(self):
        """Drop and recreate the schema."""
        self.execute('DROP TABLE IF EXISTS game_parts')
        self.execute('DROP TABLE IF EXISTS game_versions')
        self.execute('DROP TABLE IF EXISTS games')
        self.create_schema()
        
    def insert_game(self, game_data):
        """
        Insert a game and its version into the database.
        
        Args:
            game_data (dict): Game data dictionary
            
        Returns:
            tuple: (game_id, version_id, part_id)
        """
        # First, try to insert or get the game
        self.execute('''
            INSERT OR IGNORE INTO games (clean_name)
            VALUES (?)
        ''', (game_data['clean_name'],))
        
        # Get the game ID (whether it was just inserted or already existed)
        self.execute('SELECT id FROM games WHERE clean_name = ?', (game_data['clean_name'],))
        game_id = self.fetchone()[0]
        
        # Check if a version already exists for this game in this collection with this format
        self.execute('''
            SELECT id FROM game_versions 
            WHERE game_id = ? AND collection = ? AND format = ?
        ''', (game_id, game_data['collection'], game_data['format']))
        
        version_row = self.fetchone()
        if version_row:
            version_id = version_row[0]
        else:
            # Insert new version
            self.execute('''
                INSERT INTO game_versions (
                    game_id, collection, format, format_priority
                ) VALUES (?, ?, ?, ?)
            ''', (
                game_id,
                game_data['collection'],
                game_data['format'],
                game_data['format_priority']
            ))
            version_id = self.cursor.lastrowid
        
        # Insert the part
        self.execute('''
            INSERT INTO game_parts (
                version_id, part_number, source_path, original_name
            ) VALUES (?, ?, ?, ?)
        ''', (
            version_id,
            game_data['part_number'],
            game_data['source_path'],
            game_data['original_name']
        ))
        part_id = self.cursor.lastrowid
        
        return game_id, version_id, part_id
