'''
Aim: 
This project aims to build an X-like system for managing enterprise data in a 
database providing services to users with functionalities like tweeting, 
retweeting, following users, searching up tweets, etc.
'''

#Importing necessary modules
import sys
import sqlite3
import getpass # needed for masking the password
import re
from datetime import datetime

def connect_db(db_file):
    """
    Enables connection to the SQLite database with foreign keys enabled

    Inputs:
    - db_file (str): The path to the SQLite database file

    Returns:
    - sqlite3.Connection: A connection object to the database
    """
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def login_screen(db_file):
    """
    Display the initial login/signup screen and handle user input
    If the user happens to be a returning user.In the event that they are a new user, we display the signup screen and handle user input in accordance


    Inputs:
    - db_file (str): The path to the SQLite database file

    Outcomes:
    - Allows users to log in if they are returning users or sign up if they are new users
    - Otherwise, they have the option to exit the system if they wish to
    - Handles invalid input by prompting the user to enter a valid choice
    """
    while True:
        print("\n=== Main Menu ===")
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            login(db_file)
        elif choice == '2':
            sign_up(db_file)
        elif choice == '3':
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-3.")

def login(db_file):
    """
    handle the login process securely by asking for the user’s ID and password, ensuring passwords are hidden during typing
    Using parameterized queries, we check the database for a match
    If successful, we greet the user and take them to the main menu; otherwise, we let them know the login failed

    Inputs:
    - db_file (str): The path to the SQLite database file

    Oucomes:
    - Prompts the user to enter their User ID and password
    - Checks if the entered credentials match a record in the 'users' table
    - If valid, welcomes the user and directs them to the user menu
    - If invalid, notifies the user of incorrect credentials
    """
    usr = input("User ID: ").strip()
    pwd = getpass.getpass("Password: ") # Uses `getpass.getpass()` to hide password input.
    # case-sensitive password verification
    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            # Case-sensitive check for pwd
            cursor.execute("SELECT * FROM users WHERE usr = ? AND pwd = ?", (usr, pwd))
            user = cursor.fetchone()
            
            if user:
                print(f"\nWelcome {user[1]}!")
                user_menu(db_file, usr)
            else:
                print("\nInvalid credentials or user not found.")
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def sign_up(db_file):
    """
    We guide users through a secure signup process by verifying their email, phone number, and password before saving their details
    Unique credentials are required, and passwords stay hidden
    Once everything checks out, we assign them a user ID and confirm their registration

    Inputs:
    - db_file (str): The path to the SQLite database file

    Outcomes:
    - Validates the email format (must contain '@' and a domain with '.')
    - Ensures the phone number consists of digits only
    - Asks the user to confirm their password before proceeding
    - Generates a unique user ID by incrementing the highest existing ID from users table
    - Inserts the new user into the 'users' table

    Error Handling:
    - Catches integrity errors if the email or phone already exists in the database
    - Handles general database errors gracefully
    """
    print("\n=== New User Registration ===")
    
    # Validate email format
    while True:
        email = input("Email: ").strip().lower()
        if '@' in email and '.' in email.split('@')[-1]:
            break
        print("Invalid email - must contain '@' and domain with '.'")
    
    # Validate phone number
    while True:
        phone = input("Phone (numbers only): ").strip()
        if phone.isdigit():
            break
        print("Invalid phone - numbers only")
    
    name = input("Full Name: ").strip()
    
    # Password confirmation
    while True:
        pwd = getpass.getpass("Password: ") # Uses `getpass.getpass()` to hide password input.
        confirm = getpass.getpass("Confirm Password: ") # Ensures passwords match before storing them.
        if pwd == confirm:
            break
        print("Passwords don't match!")
    
    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            
            # Get next user ID
            cursor.execute("SELECT MAX(usr) FROM users")
            max_usr = cursor.fetchone()[0]
            new_usr = max_usr + 1 if max_usr else 1
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (usr, name, email, phone, pwd)
                VALUES (?, ?, ?, ?, ?)
            """, (new_usr, name, email, phone, pwd))
            
            print(f"\nRegistration successful! Your user ID is: {new_usr}")
            
    except sqlite3.IntegrityError:
        print("Error: Email or phone already exists!")
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def user_menu(db_file, usr):
    """
    After logging in, users land on this menu, their central hub for navigating the system
    From here, they can access different features based on their permissions, and the menu remains active until they choose to log out

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the logged-in user.

    Returns:
    - Provides options for the user to:
      0. View your feed 
      1. Compose a tweet.
      2. Search for tweets.
      3. Search for other users.
      4. Create a favorite list.
      5. View favorite lists.
      6. List their followers.
      7. Logout.
    - Calls the corresponding function based on the user's choice.
    - Repeats the menu until the user chooses to log out.

    Error Handling:
    - Ensures the user enters a valid option (1-7).
    - Displays an error message if an invalid choice is made.

    """
    show_feed(db_file, usr) #We automatically show the first 5 tweets/retweets that are made through the function call
    while True:
        print("\n=== Welcome to Your Dashboard ===")
        print("1. View your feed (tweets & retweets from followed users)")
        print("2. Compose a Tweet")
        print("3. Search Tweets")
        print("4. Search Users")
        print("5. Create Favorite Lists")
        print("6. List Favourite Lists")
        print("7. List Followers")
        print("8. Log out")
        choice = input("Choose an option (1-8): ").strip()
        if choice == '1':
            show_feed(db_file, usr)
        elif choice == '2':
            compose_tweet(db_file, usr)  
        elif choice == '3':
            search_tweets(db_file, usr)
        elif choice == '4':
            search_users(db_file, usr)
        elif choice == '5':
            create_favorite_list(db_file, usr)
        elif choice == '6':
            list_favorite_lists(db_file, usr)
        elif choice == '7':
            list_followers(db_file, usr)
        elif choice == '8':  
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

def show_feed(db_file, usr):
    """Displays the user's feed: latest tweets and retweets from followed users, excluding spam.
    
    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the logged-in user.

    Outcomes: 
    - Paignation of latest tweets
    """

    query = """
        SELECT 'tweet' AS type, tid, tdate, ttime, 0 AS spam, text 
        FROM tweets 
        WHERE writer_id IN (SELECT flwee FROM follows WHERE flwer = ?) 

        UNION ALL

        SELECT 'retweet' AS type, r.tid, r.rdate AS tdate, '' AS ttime, r.spam, t.text
        FROM retweets r 
        
        JOIN tweets t ON r.tid = t.tid
        WHERE r.retweeter_id IN (SELECT flwee FROM follows WHERE flwer = ?) 
        AND r.spam = 0  

        ORDER BY tdate DESC, ttime DESC
        LIMIT 5 OFFSET ?;
    """

    offset = 0  # allows tracking if more than 5 tweets exist
    while True:
        try:
            with connect_db(db_file) as conn:
                cursor = conn.cursor()
                print("\n=== Your Feed ===")
                # Check if there are any tweets at all
                cursor.execute(query, (usr, usr, 0))
                first_batch = cursor.fetchall()
                if not first_batch:
                    print("No tweets to display.")
                    while True:
                        choice = input("Type 'b' for dashboard or 'q' to quit: ").strip().lower()
                        # dashboard
                        if choice == 'b':
                            return  
                        elif choice == 'q':
                            print("Exiting feed...")
                            login_screen(db_file)
                            return
                        else:
                            print("Invalid input. Please enter 'b' or 'q'.")

                cursor.execute(query, (usr, usr, offset))
                feed = cursor.fetchall()

                if not feed:
                    print("No more tweets available.")
                    while True:
                        choice = input("Type 'b' for dashboard or 'q' to quit: ").strip().lower()
                        if choice == 'b':
                            return  
                        elif choice == 'q':
                            print("Exiting feed...")
                            login_screen(db_file)
                            return
                        else:
                            print("Invalid input. Please enter 'b' or 'q'.")

                # Display tweets
                for i, (tweet_type, tid, date, time, spam, text) in enumerate(feed, start=offset + 1):
                    print(f"[{i}] {tweet_type.upper()} | ID: {tid} | Date: {date} | Time: {time if time else 'None'} | Spam: {spam}")
                    print(f"    {text}\n")

                # Check if there are more tweets beyond this batch
                cursor.execute(query, (usr, usr, offset + 5))
                more_tweets = cursor.fetchall()

                # Provide options based on availability of more tweets
                while True:
                    #print("\n===Your Feed===")
                    if more_tweets:
                        choice = input("Type 'n' for next 5 tweets, 'b' for dashboard, or 'q' to quit: ").strip().lower()
                        if choice == 'n':
                            offset += 5  # Load next 5 tweets
                            break
                        elif choice == 'b':
                            return  # Go back to dashboard
                        elif choice == 'q':
                            print("Exiting feed...")
                            login_screen(db_file)
                            return
                        else:
                            print("Invalid input. Please enter 'n', 'b', or 'q'.")
                    else:
                        choice = input("Type 'b' for dashboard or 'q' to quit: ").strip().lower()
                        if choice == 'b':
                            return  # Go back to dashboard
                        elif choice == 'q':
                            print("Exiting feed...")
                            login_screen(db_file)
                            return
                        else:
                            print("Invalid input. Please enter 'b' or 'q'.")
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            return

def list_followers(db_file, current_usr):
    """
    This function displays the main user menu after login, allowing access to key features like tweeting, searching, and managing lists
    It runs until the user logs out, ensuring only valid options are selected
    Display a paginated list of users who follow the currently logged-in user

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - current_usr (str): The user ID of the currently logged-in user.

    Returns:
    - Retrieves all followers (users who follow `current_usr`) from the database.
    - Displays followers in pages of 5 at a time.
    - Allows the user to navigate through the list and view more followers.
    - Provides an option to select a follower to view additional details.
    - Offers an option to exit the listing process.

    Error Handling:
    - Displays a message if the user has no followers.
    - Ensures that only valid numeric inputs are accepted for follower selection.
    - Catches and reports database errors.

    """
    query = """
        SELECT users.usr, users.name
        FROM follows
        JOIN users ON follows.flwer = users.usr
        WHERE flwee = ?
        ORDER BY users.usr
    """
    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (current_usr,))
            followers = cursor.fetchall() 

            if not followers:
                print("\nYou have no followers.")
                return

            # Paginate in batches of 5
            start_index = 0
            while start_index < len(followers):
                end_index = min(start_index + 5, len(followers)) # We paginate by capping the end_index at start_index+5 during the iteration process
                print("\n=== Your Followers ===")
                for i, (f_usr, f_name) in enumerate(followers[start_index:end_index], start=start_index + 1):
                    print(f"[{i}] User ID: {f_usr} | Name: {f_name}")
                
                start_index = end_index

                # If user wants to view more followers
                if start_index < len(followers):
                    more = input("\nMore followers available. Do you want to see more? (y/n): ").strip().lower() # Giving the  user the choice to select a follower to view their details
                    if more != 'y':
                        break

            # Ask user to select a follower
            choice = input("\nSelect a follower by number to view details or 'q' to quit: ").strip().lower()
            if choice == 'q':
                return

            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(followers):
                    selected_usr = followers[choice_num - 1][0]
                    view_user_details(db_file, selected_usr, current_usr)
                else:
                    print("Invalid selection.")
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def search_tweets(db_file, usr):
    """
    Search for tweets containing specific keywords, matching both text and hashtags and display results in a paginated format
    Results appear from newest to oldest in pages of five, with options to load more or view tweet details.

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the currently logged-in user.

    Returns:
    - Prompts the user to enter one or more keywords (comma-separated).
    - Searches for tweets that contain the keywords in their text (case-insensitive).
    - Also searches for tweets associated with hashtags matching the keywords.
    - Combines both types of results using a UNION query and sorts them by date and time (descending).
    - Displays search results in pages of 5 tweets at a time.
    - Allows the user to navigate through additional results.
    - Provides an option to select a tweet for further details.

    Error Handling:
    - Displays an error message if no keywords are entered.
    - Informs the user if no tweets match the search criteria.
    - Catches and reports database errors.
    """
    keywords_input = input("Enter one or more keywords (separated by commas): ").strip()
    keywords = [kw.strip().lower() for kw in keywords_input.split(',') if kw.strip()]

    if not keywords:
        print("No keywords provided.")
        return
    placeholders = ', '.join(['?'] * len(keywords))

    # The query checks tweets by matching text with LIKE (case-insensitive),
    # and also checks if there are matching hashtags in hashtag_mentions
    # that match the provided keywords exactly (lowercased).
    # We use UNION to combine both sets of results.
    query = f"""
        SELECT tid, writer_id, text, tdate, ttime
        FROM tweets
        WHERE {" OR ".join(["LOWER(text) LIKE ?"] * len(keywords))}
        UNION
        SELECT tweets.tid, tweets.writer_id, tweets.text, tweets.tdate, tweets.ttime
        FROM tweets
        JOIN hashtag_mentions ON tweets.tid = hashtag_mentions.tid
        WHERE LOWER(hashtag_mentions.term) IN ({placeholders})
        ORDER BY tdate DESC, ttime DESC
    """

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # Prepare search parameters for the text LIKE part and then hashtags
            params = [f"%{kw}%" for kw in keywords] + keywords

            cursor.execute(query, tuple(params))
            tweets = cursor.fetchall()

            print("\n=== Search Results ===")
            if not tweets:
                print("No tweets found matching the keywords.")
                return

            # Display tweets in a paginated format (5 at a time)
            def display_tweets(start_index):
                end_index = min(start_index + 5, len(tweets))
                for i in range(start_index, end_index):
                    tid, writer_id, text, tdate, ttime = tweets[i]
                    time_str = f"at {ttime}" if ttime else ""
                    print(f"\n[{i+1}] Tweet ID: {tid} | Writer ID: {writer_id} | {tdate} {time_str}")
                    print(f"{text}")

            start_index = 0
            display_tweets(start_index)

            while len(tweets) > start_index + 5:
                more = input("\nMore tweets available. Do you want to see more? (y/n): ").strip().lower()
                if more != 'y':
                    break
                start_index += 5
                display_tweets(start_index)

            # Let the user select a tweet for statistics
            tweet_choice = input("\nSelect a tweet by number for more details or 'q' to quit: ").strip()
            if tweet_choice.lower() == 'q':
                return
            if tweet_choice.isdigit():
                tweet_choice = int(tweet_choice)
                if 1 <= tweet_choice <= len(tweets):
                    tid = tweets[tweet_choice - 1][0]
                    view_tweet_statistics(db_file, tid, usr)

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def view_tweet_statistics(db_file, tid, usr):
    """
    Provides tweet performance stats, including retweet and reply counts
    Users can interact by replying, retweeting, or saving the tweet to favorites, with the menu staying open until they exit

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - tid (int): The tweet ID for which statistics are displayed.
    - usr (str): The user ID of the currently logged-in user.

    Returns:
    - Retrieves and displays the number of retweets and replies for the given tweet.
    - Provides the user with interaction options:
        1. Reply to the tweet.
        2. Retweet the tweet.
        3. Add the tweet to a favorite list.
        4. Go back to the previous menu.
    - Handles invalid input gracefully.

    Error Handling:
    - Catches and reports any SQLite database errors.

    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            # Get retweet count
            cursor.execute("SELECT COUNT(*) FROM retweets WHERE tid = ?", (tid,))
            retweet_count = cursor.fetchone()[0]

            # Get reply count
            cursor.execute("SELECT COUNT(*) FROM tweets WHERE replyto_tid = ?", (tid,))
            reply_count = cursor.fetchone()[0]

            print(f"\n=== Tweet Statistics ===")
            print(f"Tweet ID: {tid}")
            print(f"Retweets: {retweet_count}")
            print(f"Replies: {reply_count}")

            while True:
                print("\nActions:")
                print("1. Reply to this tweet")
                print("2. Retweet this tweet")
                print("3. Add to a favorite list")
                print("4. Go back")

                action = input("Choose an action (1-4): ").strip()
                
                if action == '1':
                    compose_reply(db_file, tid, usr)
                elif action == '2':
                    retweet(db_file, tid, usr)
                elif action == '3':
                    add_to_favorite_list(db_file, usr, tid)
                elif action == '4':
                    break
                else:
                    print("Invalid choice. Please try again.")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def create_favorite_list(db_file, usr):
    """
    Allows the user to create a new favorite list
    Before adding it to the database, we check that the list name is unique and confirm successful creation

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the currently logged-in user.

    Returns:
    - Provides feedback to the user, confirming the successful creation or notifying them of any issues (e.g., list name is empty or already exists).

    Error Handling:
    - Catches and reports any SQLite database errors.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            list_name = input("Enter a name for your favorite list: ").strip()

            if not list_name:
                print("List name cannot be empty.")
                return

            # Check if the list already exists
            cursor.execute("""
                SELECT 1 FROM lists WHERE owner_id = ? AND lname = ?
            """, (usr, list_name))
            
            if cursor.fetchone():
                print("A list with this name already exists.")
                return

            # Insert new list
            cursor.execute("""
                INSERT INTO lists (owner_id, lname) VALUES (?, ?)
            """, (usr, list_name))
            
            conn.commit()
            print(f"Favorite list '{list_name}' created successfully.")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def add_to_favorite_list(db_file, usr, tid):
    """
    Add a tweet to a selected favorite list
    If no lists exist, we prompt them to create one
    To keep things tidy, we check for duplicates before adding the tweet.

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the currently logged-in user.
    - tid (int): The tweet ID of the tweet to be added to the favorite list.

    Returns:
    - Fetches the user's existing favorite lists from the database.
    - Checks if the tweet is already in the selected favorite list.
    - If not, adds the tweet to the chosen list in the database.

    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            # Fetch user's favorite lists
            cursor.execute("SELECT lname FROM lists WHERE owner_id = ?", (usr,))
            fav_lists = cursor.fetchall()

            # If no lists exist, prompt the user to create one
            if not fav_lists:
                print("You have no favorite lists. Create one first.")
                create_favorite_list(db_file, usr)

                # Re-fetch lists after creation
                cursor.execute("SELECT lname FROM lists WHERE owner_id = ?", (usr,))
                fav_lists = cursor.fetchall()

                if not fav_lists:  # User may have chosen not to create one
                    return

            print("\n=== Your Favorite Lists ===")
            for idx, (lname,) in enumerate(fav_lists, start=1):
                print(f"{idx}. {lname}")

            list_choice = input("Select a list by number or 'q' to cancel: ").strip()
            if list_choice.lower() == 'q':
                return

            if list_choice.isdigit():
                list_idx = int(list_choice) - 1
                if 0 <= list_idx < len(fav_lists):
                    lname = fav_lists[list_idx][0]

                    # Check if tweet is already in the list
                    cursor.execute("""
                        SELECT 1 FROM include WHERE owner_id = ? AND lname = ? AND tid = ?
                    """, (usr, lname, tid))
                    
                    if cursor.fetchone():
                        print("This tweet is already in the selected list.")
                        return

                    # Insert into include table
                    cursor.execute("""
                        INSERT INTO include (owner_id, lname, tid) VALUES (?, ?, ?)
                    """, (usr, lname, tid))
                    
                    conn.commit()
                    print(f"Tweet added to '{lname}'.")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def compose_reply(db_file, tid, usr):
    """
    Compose and post a reply to a selected tweet
    Each reply is timestamped and saved in the database

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - tid (int): The tweet ID of the tweet being replied to.
    - usr (str): The user ID of the currently logged-in user.

    Returns:
    - Prompts the user to enter a reply message.
    - If the reply text is not empty, the reply is inserted into the `tweets` table with the current date and time, and a reference to the original tweet (`replyto_tid`).
    - The reply is posted successfully if there are no errors in the database operations.

    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    reply_text = input("Enter your reply: ").strip()
    if reply_text:
        try:
            with connect_db(db_file) as conn:
                cursor = conn.cursor()
                
                # Insert the reply tweet
                cursor.execute("""
                    INSERT INTO tweets (writer_id, text, tdate, ttime, replyto_tid)
                    VALUES (?, ?, CURRENT_DATE, CURRENT_TIME, ?)
                """, (usr, reply_text, tid))
                print("Reply posted successfully!")
                
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")

def retweet(db_file, tid, usr):
    """
    Retweet a selected tweet, limited to sharing with followers only
    To prevent spam, we check if they’ve already retweeted before adding it to the retweets table with a timestamp. 
    
    Inputs:
    - db_file (str): The path to the SQLite database file.
    - tid (int): The tweet ID of the tweet being retweeted.
    - usr (str): The user ID of the currently logged-in user.
    
    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    # Get current date and time
    now = datetime.now()
    rdate = now.strftime("%Y-%m-%d")
    
    try:
        # Connect to the database properly
        conn = connect_db(db_file)
        cursor = conn.cursor()
        
        try:
            # Check if the user has already retweeted this tweet
            cursor.execute("""
                SELECT COUNT(*) 
                FROM retweets 
                WHERE tid = ? AND retweeter_id = ?
            """, (tid, usr))
            if cursor.fetchone()[0] > 0:
                print("You have already retweeted this tweet.")
                return
            
            # First check if the tweet exists
            cursor.execute("SELECT writer_id FROM tweets WHERE tid = ?", (tid,))
            result = cursor.fetchone()
            if not result:
                print(f"Tweet with ID {tid} not found.")
                return
            
            writer_id = result[0]
            
            # Insert the retweet
            cursor.execute("""
                INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate)
                VALUES (?, ?, ?, 0, ?)
            """, (tid, usr, writer_id, rdate))
            
            rows_affected = cursor.rowcount
            print(f"Rows affected by INSERT: {rows_affected}")
            
            conn.commit()
            print("Retweet posted successfully!")
            
        finally:
            # Make sure to close the connection
            conn.close()
            
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def get_new_tid(cursor):
    """
    Get the next available tweet ID by finding the highest current tweet ID and incrementing it
    Prevents duplication
    If table is empty, start at 1

    Inputs:
    - cursor (sqlite3.Cursor): The SQLite cursor used to execute queries on the database.

    Returns:
    - int: The next available tweet ID, which is one more than the highest existing tweet ID.
    """
    cursor.execute("SELECT MAX(tid) FROM tweets")
    max_tid = cursor.fetchone()[0]
    return (max_tid or 0) + 1  # Return the next available ID

def compose_tweet(db_file, usr):
    """
    Allows the user to compose a tweet, add hashtags (optional), and store it in the database
    Hashtags are extracted, checked for uniqueness, and saved alongside the tweet using a new tweet ID.

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the person composing the tweet.

    Functionality:
    - Prompts the user to enter the content of a tweet.
    - Validates that the tweet is not empty and checks for duplicate hashtags.
    - Extracts hashtags (case-insensitive) from the tweet and stores them separately in the `hashtag_mentions` table.
    - Inserts the tweet into the `tweets` table with a unique tweet ID and timestamp.
    - Ensures that each hashtag is stored only once for the tweet.

    Returns:
    - None: This function prints messages based on the success or failure of the tweet creation process.

    Errors:
    - The function will print an error message if the tweet is empty or if duplicate hashtags are found.
    - Any database errors are caught and displayed as a message.
    """
    tweet_text = input("Compose your tweet: ").strip()

    if not tweet_text:
        print("Tweet cannot be empty.")
        return

    # Extract hashtags (case-insensitive, stored in lowercase)
    hashtags = re.findall(r"#\w+", tweet_text.lower())

    # Check for duplicate hashtags
    duplicate_hashtags = [hashtag for hashtag in hashtags if hashtags.count(hashtag) > 1]
    if duplicate_hashtags:
        print(f"Error: The following hashtags are duplicated: {', '.join(set(duplicate_hashtags))}")
        return

    # Get current date and time
    now = datetime.now()
    tdate = now.strftime("%Y-%m-%d")
    ttime = now.strftime("%H:%M:%S")

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            # Get a new tweet ID
            tid = get_new_tid(cursor)

            # Insert tweet into the tweets table
            cursor.execute("""
                INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
                VALUES (?, ?, ?, ?, ?, NULL)
            """, (tid, usr, tweet_text, tdate, ttime))

            # Insert each unique hashtag into the hashtag_mentions table
            for hashtag in set(hashtags):  # Use set to ensure uniqueness
                cursor.execute("""
                    INSERT INTO hashtag_mentions (tid, term)
                    VALUES (?, ?)
                """, (tid, hashtag[1:]))  # Remove '#' before storing

            conn.commit()
            print("\nTweet posted successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def search_users(db_file, usr):
    """
    users find others by searching for names or parts of names
    Searches aren’t case-sensitive, and results are sorted by shortest name first
    We show matches in groups of five, letting users select one for more details

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the person performing the search.

    Returns:
    - None: This function prints messages based on the success or failure of the search.
    - If a user is selected, the `view_user_details` function is called to display the details of the selected user.
    
    Errors:
    - A database error is caught and printed if there is an issue with the query or connection.
    """
    keyword = input("Enter a keyword to search for users: ").strip().lower()

    query = """
        SELECT usr, name
        FROM users
        WHERE name COLLATE NOCASE LIKE ?
        ORDER BY LENGTH(name) ASC
    """
    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{keyword}%",))
            users = cursor.fetchall()

            if not users:
                print("No users found matching the keyword.")
                return

            # Pagination 5 users max
            start_index = 0
            while start_index < len(users):
                end_index = min(start_index + 5, len(users))
                print("\n=== Search Results ===")
                for i, (user_id, name) in enumerate(users[start_index:end_index], start=start_index + 1):
                    print(f"[{i}] User ID: {user_id} | Name: {name}")

                start_index = end_index

                # If there are more users, ask if the user wants to continue
                if start_index < len(users):
                    more = input("\nMore users available. Do you want to see more? (y/n): ").strip().lower()
                    if more != 'y':
                        break

            # Ask user to select a user for details
            user_choice = input("\nSelect a user by number to view details or 'q' to quit: ").strip()
            if user_choice.lower() == 'q':
                return
            if user_choice.isdigit():
                user_choice = int(user_choice)
                if 1 <= user_choice <= len(users):
                    selected_user_id = users[user_choice - 1][0]
                    view_user_details(db_file, selected_user_id, usr)

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def view_user_details(db_file, target_usr, current_usr):
    """
    View details of a selected user, including their tweet count, followers, following, and 3 most recent tweets
    After checking out the profile, users can choose to follow them, view more tweets, or go back.

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - target_usr (str): The user ID of the target user whose details are to be viewed.
    - current_usr (str): The user ID of the current user who is viewing the details.

    Returns:
    - Displays the total number of tweets, followers, and following for the target user.
    - Fetches and displays the 3 most recent tweets of the target user, if available.
    - Provides the current user with options to:
        1. Follow the target user (calls `follow_user`).
        2. View more of the target user's tweets (calls `view_more_tweets`).
        3. Return to the previous screen.
    """
    query_user_details = """
        SELECT 
            (SELECT COUNT(*) FROM tweets WHERE writer_id = ?) AS tweet_count,
            (SELECT COUNT(*) FROM follows WHERE flwee = ?) AS follower_count,
            (SELECT COUNT(*) FROM follows WHERE flwer = ?) AS following_count
    """

    query_recent_tweets = """
        SELECT tid, text, tdate, ttime
        FROM tweets
        WHERE writer_id = ?
        ORDER BY tdate DESC, ttime DESC
        LIMIT 3
    """

    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query_user_details, (target_usr, target_usr, target_usr))
            tweet_count, follower_count, following_count = cursor.fetchone()

            print("\n=== User Details ===")
            print(f"User ID: {target_usr}")
            print(f"Total Tweets: {tweet_count}")
            print(f"Followers: {follower_count}")
            print(f"Following: {following_count}")
            
            # Display up to 3 recent tweets
            cursor.execute(query_recent_tweets, (target_usr,))
            tweets = cursor.fetchall()

            print("\n=== Recent Tweets ===")
            if tweets:
                for tid, text, tdate, ttime in tweets:
                    time_str = f"at {ttime}" if ttime else ""
                    print(f"\nTweet ID: {tid} | {tdate} {time_str}")
                    print(f"{text}")
            else:
                print("No recent tweets available.")

            print("\nOptions:")
            print("1. Follow this user")
            print("2. View more tweets")
            print("3. Go back")

            choice = input("Choose an option (1-3): ").strip()
            if choice == '1':
                follow_user(db_file, current_usr, target_usr)
            elif choice == '2':
                view_more_tweets(db_file, target_usr)
            elif choice == '3':
                return
            else:
                print("Invalid choice.")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def follow_user(db_file, current_usr, target_usr):
    """
    Follow a user if not already following
    If they try to follow themselves, we block it
    Before adding a new follow, we check if they’re already following the user
    If not, we add the follow and confirm it.

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - current_usr (str): The user ID of the current user who wants to follow another user.
    - target_usr (str): The user ID of the user to be followed.

    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    query_check = "SELECT 1 FROM follows WHERE flwer = ? AND flwee = ?"
    query_insert = "INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, DATE('now'))"

    if current_usr == str(target_usr):
        print("You cannot follow yourself.")
        return

    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query_check, (current_usr, target_usr))
            if cursor.fetchone():
                print("You are already following this user.")
                return

            cursor.execute(query_insert, (current_usr, target_usr))
            conn.commit()
            print("You are now following this user!")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def view_more_tweets(db_file, target_usr):
    """
    We show all tweets by a user in groups of five so things don’t get overwhelming
    Tweets are listed from newest to oldest
    If the user has no tweets, we let them know
    Otherwise, they can keep loading more in batches

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - target_usr (str): The user ID of the user whose tweets are to be viewed.

    Returns:
    - Displays the tweets in batches of 5. After displaying each batch, prompts the user to decide if they want to see more tweets.
    - If the user chooses to see more, the next 5 tweets are displayed. This process continues until all tweets have been shown or the user opts to stop.

    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    query = """
        SELECT tid, text, tdate, ttime
        FROM tweets
        WHERE writer_id = ?
        ORDER BY tdate DESC, ttime DESC
    """

    try:
        with connect_db(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (target_usr,))
            tweets = cursor.fetchall()

            if not tweets:
                print("No tweets available.")
                return

            start_index = 0
            while start_index < len(tweets):
                end_index = min(start_index + 5, len(tweets))
                print("\n=== More Tweets ===")
                for i, (tid, text, tdate, ttime) in enumerate(tweets[start_index:end_index], start=start_index + 1):
                    time_str = f"at {ttime}" if ttime else ""
                    print(f"\nTweet ID: {tid} | {tdate} {time_str}")
                    print(f"{text}")

                start_index = end_index

                if start_index < len(tweets):
                    more = input("\nDo you want to see more tweets? (y/n): ").strip().lower()
                    if more != 'y':
                        break

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

def list_favorite_lists(db_file, usr):
    """
    Retrieve and display all favorite lists of a user along with their stored tweet IDs (TIDs)
    Even empty lists still show up, with appropriate message
    Everything is sorted alphabetically

    Inputs:
    - db_file (str): The path to the SQLite database file.
    - usr (str): The user ID of the currently logged-in user.

    Returns:
    - Displays the favorite lists and their associated TIDs to the user. If a list contains no tweets, it displays a message indicating that.

    Error Handling:
    - Catches and reports any SQLite database errors during the execution.
    """
    query = """
        SELECT l.lname, i.tid
        FROM lists l
        LEFT JOIN include i ON l.owner_id = i.owner_id AND l.lname = i.lname
        WHERE l.owner_id = ?
        ORDER BY l.lname;
    """

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (usr,))
            results = cursor.fetchall()

            if not results:
                print("You have no favorite lists.")
                return

            # Organize results into a dictionary {list_name: [tid1, tid2, ...]}
            fav_lists = {}
            for list_name, tid in results:
                if list_name not in fav_lists:
                    fav_lists[list_name] = []
                if tid:  # Ensure that we don't add None values (empty lists)
                    fav_lists[list_name].append(tid)

            # Print the lists and their TIDs
            print("\n=== Your Favorite Lists ===")
            for list_name, tids in fav_lists.items():
                tids_display = ", ".join(map(str, tids)) if tids else "No tweets in this list."
                print(f"{list_name}: {tids_display}")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <database_file>")
        sys.exit(1)
    
    db_file = sys.argv[1]
    try:
        login_screen(db_file)
    except KeyboardInterrupt:
        print("\n\nExiting system. Goodbye!")
        sys.exit(0)
