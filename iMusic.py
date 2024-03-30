from flask import Flask, request, redirect, render_template, url_for
import sqlite3

app = Flask(__name__)

# I did not write this function. It is from:
# https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
def is_number(s):
    """
    Check if a string is a number (regardless of it being an int, long, float or complex number)
    :param s: string The string to check if it is a number
    :return: True if string is a number, False otherwise
    """
    try:
        complex(s)
    except ValueError:
        return False
    return True

def is_integer(s):
    """
    Check if a string is an integer
    :param s: string The string to check if it is an integer
    :return: True if string is an integer, False otherwise
    """
    try:
        int(s)
    except ValueError:
        return False
    return True
    
def string_to_int(s):
    """
    Convert a string to an integer
    :param s: string The string to convert to an int
    :return: int The int value of the string
    """
    if is_number(s):
        return int(s)
    else:
        return s

def string_length(s):
    """
    Get the length of a string
    :param s: string The string to get the length of
    :return: int The length of the string
    """
    return len(s)

# The root URL (home page)
@app.route('/')
def index():
    return render_template('index.html')


# Task 2
@app.route('/statistics/')
def statistics():
    # Connect to the database
    conn = sqlite3.connect('IMusic.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Retrieve the required data list and store it in the variable "prices"
    query = """
      SELECT UnitPrice as Price, COUNT(*) as Tracks, COUNT(DISTINCT AlbumId) as Albums, COUNT(DISTINCT ArtistId) as Artists, SUM(Milliseconds)/1000 as Duration, UnitPrice * COUNT(*) as TotalValue
      FROM Track NATURAL JOIN Album
      GROUP BY UnitPrice
      ORDER BY UnitPrice ASC
    """
    cursor.execute(query)
    prices = cursor.fetchall()

    # Retrieve and use the variable "total" to store the required data of the last row of the table
    query = """
      SELECT "Total" as Price, COUNT(*) as Tracks, COUNT(DISTINCT AlbumId) as Albums, COUNT(DISTINCT ArtistId) as Artists, SUM(Milliseconds)/1000 as Duration, SUM(UnitPrice) as TotalValue
      FROM Track NATURAL JOIN Album
    """
    cursor.execute(query)
    total = cursor.fetchone()

    # Append the "total" row to the "prices" list
    prices.append(total)

    # Close the connection to the Database
    conn.close()

    # Render the template (and pass the variable "prices")
    return render_template('statistics.html', prices=prices)


# Task 3
@app.route('/add/')
def add_track_form():
    # Connect to the database
    conn = sqlite3.connect('iMusic.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Retrieve the required data for the "track_album" drop down list and store it in the variable "albums"
    cursor.execute('SELECT AlbumId, Title FROM Album ORDER BY Title ASC')
    albums = cursor.fetchall()

    # Retrieve the required data for the "track_genre" drop down list and store it in the variable "genres"
    cursor.execute('SELECT GenreId, Name FROM Genre ORDER BY Name ASC')
    genres = cursor.fetchall()

    # Close the connection to the Database
    conn.close()

    # Render the template
    return render_template('add_track.html', albums=albums, genres=genres)

@app.route('/add/track', methods=['POST'])
def add_track():
    # Connect to the database
    conn = sqlite3.connect('iMusic.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create a list to store the error messages
    messages = []

    # Validate the form data
    # Check the validity of the "track_name" field
    track_name = request.form['track_name']
    if not track_name:
        messages.append("Track name is empty")
    elif len(track_name) > 200:
        messages.append("Track name is too long")
    
    # Check the validity of the "track_album" field
    track_album = request.form['track_album']
    if not track_album or not is_integer(track_album):
        messages.append("Album ID is invalid")
    else:
        # Check if the AlbumId exists in the database
        try:
          cursor.execute('SELECT 1 FROM Album WHERE AlbumId = ?', (track_album,))
          if not cursor.fetchone():
              messages.append("Album does not exist")
        # When sqlite3 errors occur, add the error report to "messages"
        except sqlite3.Error as e:
          messages.append(f"An sqlite3 error occurred: {e}")

    # Check the validity of the "track_genre" field
    track_genre = request.form['track_genre']
    if not track_genre or not is_integer(track_genre):
        messages.append("Genre ID is invalid")
    else:
        # Check if the GenreId exists in the database
        try:
          cursor.execute('SELECT 1 FROM Genre WHERE GenreId = ?', (track_genre,))
          if not cursor.fetchone():
              messages.append("Genre does not exist")
        # When sqlite3 errors occur, add the error report to "messages"
        except sqlite3.Error as e:
          messages.append(f"An sqlite3 error occurred: {e}")

    # Check the validity of the "track_composer" field
    track_composer = request.form['track_composer']
    if track_composer and len(track_composer) > 220:
        messages.append("Composer name is too long")

    # Check the validity of the "track_duration" field
    track_duration = request.form['track_duration']
    if not track_duration or not is_number(track_duration):
        messages.append("Duration is invalid")
    else:
        try:
            int(float(track_duration))
            if int(float(track_duration)) <= 0:
                messages.append("Duration must be a positive number")
        except ValueError:
            messages.append("Duration is invalid")

    # Check the validity of the "track_price" field
    track_price = request.form['track_price']
    if not track_price or not is_number(track_price):
        messages.append("Price is invalid")
    else:
        try:
            float(track_price)
            if float(track_price) <= 0 or float(track_price) > 10:
                messages.append("Price must be more than zero and less than or equal to 10")
        except ValueError:
            messages.append("Price is invalid")

    # If there are any errors, render the "error.html" template with the error messages
    if messages:
        return render_template('error.html', messages=messages)

    # Construct a SQL query to insert the new track into the Track table
    query = 'INSERT INTO Track (Name, AlbumId, GenreId, Composer, Milliseconds, UnitPrice) VALUES (?, ?, ?, ?, ?, ?)'
    values = (track_name, track_album, track_genre, track_composer, int(float(track_duration))*1000, track_price)

    # Execute the SQL query and commit the transaction if there are no sqlite3 errors
    try:
        cursor.execute(query, values)
        conn.commit()
    # When sqlite3 errors occur, render the "error.html" template with the error messages
    except sqlite3.Error as e:
        return render_template('error.html', messages=[f"An sqlite3 error occurred: {e}"])

    # Close the connection to the Database
    conn.close()

    # Redirect the user to the root URL
    return redirect(url_for('index'))


@app.route('/album/')
@app.route('/album/<album_id>')
def list_album(album_id=None):
    return render_template('error.html', messages=["Album listing is not implemented yet. Another developer is working on it."])


def main():
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()
