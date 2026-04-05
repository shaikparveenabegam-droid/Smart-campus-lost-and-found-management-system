
import streamlit as st
import sqlite3
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database
conn = sqlite3.connect("campus.db",check_same_thread=False)
c = conn.cursor()

# Tables
c.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS lost(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
item TEXT,
description TEXT,
location TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS found(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
item TEXT,
description TEXT,
location TEXT
)
''')

conn.commit()

# Functions

def signup(username,password):
    c.execute("INSERT INTO users(username,password) VALUES (?,?)",
              (username,password))
    conn.commit()


def login(username,password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username,password))
    return c.fetchone()


def add_lost(user,item,desc,loc):
    c.execute("INSERT INTO lost(user,item,description,location) VALUES (?,?,?,?)",
              (user,item,desc,loc))
    conn.commit()


def add_found(user,item,desc,loc):
    c.execute("INSERT INTO found(user,item,description,location) VALUES (?,?,?,?)",
              (user,item,desc,loc))
    conn.commit()


def get_lost():
    c.execute("SELECT * FROM lost")
    return c.fetchall()


def get_found():
    c.execute("SELECT * FROM found")
    return c.fetchall()


# Matching Function

def match(lost_desc,found_desc):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([lost_desc]+found_desc)
    similarity = cosine_similarity(tfidf[0:1],tfidf[1:])
    return similarity


# UI

st.title("Smart Campus Lost and Found System")

menu = ["Login","Signup"]
choice = st.sidebar.selectbox("Menu",menu)

# Signup

if choice == "Signup":

    st.subheader("Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Signup"):
        signup(username,password)
        st.success("Account Created")


# Login

if choice == "Login":

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        result = login(username,password)

        if result:

            st.success("Login Successful")

            menu2 = ["Report Lost","Report Found","Matches"]
            choice2 = st.selectbox("Menu",menu2)

            # Lost

            if choice2 == "Report Lost":

                st.subheader("Report Lost Item")

                item = st.text_input("Item Name")
                desc = st.text_area("Description")
                loc = st.text_input("Location")

                if st.button("Submit"):
                    add_lost(username,item,desc,loc)
                    st.success("Lost Item Added")

            # Found

            if choice2 == "Report Found":

                st.subheader("Report Found Item")

                item = st.text_input("Item Name")
                desc = st.text_area("Description")
                loc = st.text_input("Location")

                if st.button("Submit"):
                    add_found(username,item,desc,loc)
                    st.success("Found Item Added")

            # Matches

            if choice2 == "Matches":

                st.subheader("Matching Results")

                lost = get_lost()
                found = get_found()

                if len(lost)>0 and len(found)>0:

                    found_desc = [i[3] for i in found]

                    for item in lost:

                        similarity = match(item[3],found_desc)

                        best = similarity.argmax()

                        st.write("Lost Item:",item[2])
                        st.write("Lost User:",item[1])
                        st.write("Matched Found:",found[best][2])
                        st.write("Found User:",found[best][1])
                        st.write("Location:",found[best][4])
                        st.write("-------------------")

        else:
            st.error("Invalid Login")


