DATABASE_NAME = "library.db"
KEY_ID = "id"

TABLE_USERS = "users"
KEY_USER_ID = KEY_ID
KEY_USER_NAME = "userName"
KEY_USER_PSWD = "userPswd"
KEY_USER_STATUS_ID = "userStatusID"

TABLE_BOOKS = "books"
KEY_BOOK_ID = KEY_ID
KEY_BOOK_NAME = "bookName"
KEY_BOOK_AUTHOR_ID = "authorID"
KEY_BOOK_USER_ID = "userID"
KEY_BOOK_GENRE_ID = "genreID"
KEY_BOOK_DESCRIPTION = "bookDescription"        # UNREQUIRED
KEY_BOOK_IMAGE = "bookImage"                    # UNREQUIRED
KEY_BOOK_FILE = "bookFile"                      # UNREQUIRED

TABLE_AUTHORS = "authors"
KEY_AUTHOR_ID = KEY_ID
KEY_AUTHOR_NAME = "authorName"
KEY_AUTHOR_DESCRIPTION = "authorDescription"    # UNREQUIRED
KEY_AUTHOR_IMAGE = "authorImage"                # UNREQUIRED

TABLE_GENRES = "genres"
KEY_GENRE_ID = KEY_ID
KEY_GENRE_NAME = "genreName"

TABLE_STATUSES = "statuses"
KEY_STATUS_ID = KEY_ID
KEY_STATUS_NAME = "statusName"