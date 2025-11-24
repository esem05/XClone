# X-Like Backend System (Course Project)

This project is a backend system inspired by **X (formerly Twitter)**. It was originally developed as a **university course assignment** in collaboration with a team.  

The system provides core social-platform features such as tweeting, favoriting, following users, and searching content in an SQLite database.

---

## Features

### **1. Compose Tweet & Reply to Tweets**
Users can create new tweets, which the backend validates, timestamps, and stores via SQL insert operations.
They can also reply to their own tweets or to tweets from other users.

### **2. Favorite Tweets**
Users can:
- Favorite any tweet  
- View a list of their favorited posts  
- Unfavorite items  
This module uses relational tables and SQL queries to efficiently manage user–tweet relationships.

### **3. Search Functionality**
Implemented full search support for:
- Users  
- Tweets  

The search uses SQL text-based matching, allowing fast lookup across multiple fields.

### **4. User & Tweet Management**
Includes backend workflows for:
- User login and signup  
- Following and unfollowing users  
- Viewing tweets from followed accounts  
- Displaying user profiles and timelines  

### **5. Integrated Backend System**
All components work together through:
- Python functions  
- SQL queries  
- A structured, modular backend design  

---

## Tech Stack
- **Python (Core logic)**
- **SQLite (Database)**
- **SQL (Queries, joins, relational modeling)**

---


