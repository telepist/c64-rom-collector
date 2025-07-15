"""
Repository for managing game-related database operations.
"""
from .database import DatabaseManager


class GameRepository:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the repository with a database manager."""
        self.db_manager = db_manager

    def add_game(self, game_data):
        """
        Add a game and its associated data to the database.

        Args:
            game_data (dict): Game data dictionary.

        Returns:
            tuple: (game_id, version_id, part_id)
        """
        return self.db_manager.insert_game(game_data)

    def insert_game(self, game_data):
        """
        Insert a game and its version into the database.

        Args:
            game_data (dict): Game data dictionary

        Returns:
            tuple: (game_id, version_id, part_id)
        """
        return self.db_manager.insert_game(game_data)

    def get_game_by_name(self, clean_name):
        """
        Retrieve a game by its clean name.

        Args:
            clean_name (str): The clean name of the game.

        Returns:
            dict: Game details or None if not found.
        """
        self.db_manager.execute('SELECT * FROM games WHERE clean_name = ?', (clean_name,))
        return self.db_manager.fetchone()

    def reset_database(self):
        """Reset the database schema."""
        self.db_manager.reset_schema()

    def fetch_all_games(self):
        """Fetch all games from the database."""
        self.db_manager.execute('SELECT * FROM games')
        return self.db_manager.fetchall()

    def get_best_versions(self):
        """
        Retrieve the best version of each game along with its parts.
        Now includes region prioritization.

        Returns:
            list: A list of tuples containing game details and part information.
        """
        self.db_manager.execute('''
            WITH RankedVersions AS (
                SELECT 
                    g.clean_name,
                    v.format,
                    v.format_priority,
                    v.collection,
                    v.region,
                    v.region_priority,
                    v.id as version_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY g.id 
                        ORDER BY v.format_priority DESC, v.region_priority DESC, v.collection ASC
                    ) as rn
                FROM games g
                JOIN game_versions v ON g.id = v.game_id
            )
            SELECT 
                rv.clean_name,
                rv.format,
                p.source_path,
                p.part_number,
                COUNT(*) OVER (PARTITION BY rv.version_id) as total_parts
            FROM RankedVersions rv
            JOIN game_parts p ON rv.version_id = p.version_id
            WHERE rv.rn = 1
            ORDER BY rv.clean_name, p.part_number
        ''')
        return self.db_manager.fetchall()

    # Additional repository methods can be added here as needed.
