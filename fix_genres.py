import csv
import sqlite3

# Task 1
def fix_genres():
    # Connect to the Database
    conn = sqlite3.connect("iMusic.db")
    cursor = conn.cursor()

    # Read the .csv file
    with open("genres.csv", "r", newline='') as f:
      reader = csv.reader(f)
      # Skip the header row
      next(reader)
      try:
        # Iterate over the rows in the file
        for row in reader:
          genre_id = row[0]
          genre_name = row[1]
          # Update the genre names in the database to fix the mistakes
          cursor.execute("UPDATE Genre SET Name = ? WHERE GenreId = ?", (genre_name, genre_id))
      except csv.Error as e:
        # Print the error message if an error occurs
        print(e)
    
    # Save the changes to the Database
    conn.commit()

    # Close the connection to the Database
    conn.close()


if __name__ == '__main__':
    fix_genres()