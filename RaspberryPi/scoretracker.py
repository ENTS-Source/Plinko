import sqlite3 as db
import os.path


class ScoreTracker:
    def __init__(self, num_players=2):
        print("Setting up database...")
        db_name = "../plinko.db"
        file_missing = not os.path.isfile(db_name)
        self.__db = db.connect(db_name)
        self.__db.row_factory = db.Row
        if file_missing:
            print("Creating tables...")
            cursor = self.__db.cursor()
            # TODO: Read from file (plinko.sql)
            cursor.execute("CREATE TABLE scores(id INTEGER PRIMARY KEY, score NUMERIC, player NUMERIC, recorded DATETIME)")
            self.__db.commit()
        print("Collecting player statistics...")
        # Collect top scores
        self.playerScores = []
        for i in range(num_players):
            cursor = self.__db.cursor()
            cursor.execute("SELECT SUM(score) as total FROM scores WHERE player=?", (i,))
            record, = cursor.fetchone()
            if record is not None:
                self.playerScores.append(record)
            else:
                self.playerScores.append(0)
            print("Player #" + str(i) + " has a total of " + str(self.playerScores[i]) + " points")
        # Collect number of games per player
        self.gameCounts = []
        for i in range(num_players):
            cursor = self.__db.cursor()
            cursor.execute("SELECT COUNT(id) as total FROM scores WHERE player=?", (i,))
            record, = cursor.fetchone()
            if record is not None:
                self.gameCounts.append(record)
            else:
                self.gameCounts.append(0)
            print("Player #" + str(i) + " has a played a total of " + str(self.gameCounts[i]) + " games")
        # Collect total number of games
        cursor = self.__db.cursor()
        cursor.execute("SELECT COUNT(id) as total FROM scores")
        record, = cursor.fetchone()
        if record is not None:
            self.totalGames = record
        else:
            self.totalGames = 0
        print("Total games played: " + str(self.totalGames))

    def recordScore(self, player, score):
        cursor = self.__db.cursor()
        print("Recording score " + str(score) + " for player " + str(player))
        cursor.execute("INSERT INTO scores (score, player, recorded) VALUES (?, ?, datetime('now'))", (score, player,))
        self.__db.commit()
        self.playerScores[player] += score
        self.totalGames += 1

    def close(self):
        self.__db.close()
