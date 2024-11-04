import tkinter as tk
from tkinter import messagebox
import random
import sqlite3

class HangmanGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Hangman Game")
        self.db_connection = sqlite3.connect('hangman.db')
        self.cursor = self.db_connection.cursor()
        self.create_database()
        self.word = self.select_word()
        self.guessed_letters = set()
        self.attempts_remaining = 6
        self.incorrect_guesses = set()
        self.games_played = 0
        self.games_won = 0

        self.create_widgets()
        self.load_stats()

    def create_database(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS words
                              (id INTEGER PRIMARY KEY, word TEXT UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS stats
                              (id INTEGER PRIMARY KEY, games_played INTEGER, games_won INTEGER)''')
        
        # Add some initial words if the table is empty
        self.cursor.execute("SELECT COUNT(*) FROM words")
        if self.cursor.fetchone()[0] == 0:
            words = ["python", "hangman", "challenge", "programming", "developer"]
            self.cursor.executemany("INSERT OR IGNORE INTO words (word) VALUES (?)", [(w,) for w in words])
        
        self.db_connection.commit()

    def select_word(self):
        self.cursor.execute("SELECT word FROM words ORDER BY RANDOM() LIMIT 1")
        return self.cursor.fetchone()[0]

    def create_widgets(self):
        self.word_label = tk.Label(self.master, text=self.display_game_state(), font=("Arial", 24))
        self.word_label.pack(pady=20)

        self.info_label = tk.Label(self.master, text=f"Incorrect guesses remaining: {self.attempts_remaining}", font=("Arial", 14))
        self.info_label.pack(pady=10)

        self.stats_label = tk.Label(self.master, text=f"Games Played: {self.games_played}, Games Won: {self.games_won}", font=("Arial", 12))
        self.stats_label.pack(pady=5)

        self.guess_entry = tk.Entry(self.master, font=("Arial", 14))
        self.guess_entry.pack(pady=10)

        self.guess_button = tk.Button(self.master, text="Guess", command=self.make_guess, font=("Arial", 14))
        self.guess_button.pack(pady=10)

        self.add_word_entry = tk.Entry(self.master, font=("Arial", 14))
        self.add_word_entry.pack(pady=10)

        self.add_word_button = tk.Button(self.master, text="Add New Word", command=self.add_new_word, font=("Arial", 14))
        self.add_word_button.pack(pady=10)

    def display_game_state(self):
        return ' '.join([letter if letter in self.guessed_letters else '_' for letter in self.word])

    def make_guess(self):
        guess = self.guess_entry.get().lower()
        self.guess_entry.delete(0, tk.END)

        if len(guess) != 1 or not guess.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter a single alphabetic character.")
            return

        if guess in self.guessed_letters:
            messagebox.showinfo("Already Guessed", "You've already guessed that letter.")
            return

        self.guessed_letters.add(guess)

        if guess in self.word:
            self.word_label.config(text=self.display_game_state())
            if all(letter in self.guessed_letters for letter in self.word):
                self.games_won += 1
                self.update_stats()
                messagebox.showinfo("Congratulations", f"You've guessed the word: {self.word}")
                self.reset_game()
        else:
            self.incorrect_guesses.add(guess)
            self.attempts_remaining -= 1
            self.info_label.config(text=f"Incorrect guesses remaining: {self.attempts_remaining}")
            if self.attempts_remaining == 0:
                messagebox.showinfo("Game Over", f"The word was: {self.word}")
                self.reset_game()

    def reset_game(self):
        self.games_played += 1
        self.update_stats()
        self.word = self.select_word()
        self.guessed_letters.clear()
        self.incorrect_guesses.clear()
        self.attempts_remaining = 6
        self.word_label.config(text=self.display_game_state())
        self.info_label.config(text=f"Incorrect guesses remaining: {self.attempts_remaining}")

    def add_new_word(self):
        new_word = self.add_word_entry.get().lower()
        self.add_word_entry.delete(0, tk.END)

        if not new_word.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter a valid word (only alphabetic characters).")
            return

        try:
            self.cursor.execute("INSERT INTO words (word) VALUES (?)", (new_word,))
            self.db_connection.commit()
            messagebox.showinfo("Success", f"The word '{new_word}' has been added to the database.")
        except sqlite3.IntegrityError:
            messagebox.showinfo("Duplicate Word", f"The word '{new_word}' is already in the database.")

    def load_stats(self):
        self.cursor.execute("SELECT games_played, games_won FROM stats WHERE id = 1")
        result = self.cursor.fetchone()
        if result:
            self.games_played, self.games_won = result
        else:
            self.cursor.execute("INSERT INTO stats (id, games_played, games_won) VALUES (1, 0, 0)")
        self.update_stats_label()

    def update_stats(self):
        self.cursor.execute("UPDATE stats SET games_played = ?, games_won = ? WHERE id = 1", (self.games_played, self.games_won))
        self.db_connection.commit()
        self.update_stats_label()

    def update_stats_label(self):
        self.stats_label.config(text=f"Games Played: {self.games_played}, Games Won: {self.games_won}")

    def __del__(self):
        self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    game = HangmanGame(root)
    root.mainloop()