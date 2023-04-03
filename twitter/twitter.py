from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:
    """
    The menu to print once a user has logged in
    """
    def __init__(self, currentUser = None):
        self.currentUser = None

    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        registering = True
        username = ""
        password = ""
        while(registering):
            usernaming = True
            passwording = True
            while(usernaming):
                username = input("\nWhat will your twitter handle be?\n")
                if db_session.query(User).where(User.username == username).first() is None:
                    usernaming = False
                else:
                    print("\nThis Username has already been chosen :(")
            
            password = input("\nEnter a password:\n")
            if (input("\nRe-enter your password:\n") == password):
                registering = False
            else:
                print("\nThe passwords don't match. Try again.")
        
        print("Welcome " + username + "!")
        user = User(username = username, password = password)
        db_session.add(user)
        self.currentUser = user
        db_session.commit()

    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        logingIn = True
        while(logingIn):
            username = input("Username: ")
            password = input("Password: ")
            user = db_session.query(User).where((User.username == username)&(User.password == password)).first()
            if user is None:
                print("Invalid username or password")
            else:
                logingIn = False
        self.currentUser = user
        print("Welcome " + username + "!")

    def logout(self):
        self.currentUser = None
        self.run()

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        startingUp = True

        print("\nWelcome to Justin's ATCS Twitter!")
        while(startingUp):
            startingUp = False
            selected = input("\nPlease select a menu option:\n 1. Register user \n 2. Login \n 3. Exit\n")
            if  selected == "1":
                self.register_user()
            elif selected == "2":
                self.login()
            elif selected == "3":
                self.end()
            else:
                print("That's not an option!")
                startingUp = True
            

    def follow(self):
        inputedUser = input("\nWho would you like to follow?\n")
        toFollow = db_session.query(User).where(User.username == inputedUser).first()
        if toFollow is None:
            print("\nThat user does not exist!")
        elif toFollow in self.currentUser.following:
            print("\nYou already follow this user!")
        else:
            self.currentUser.following.append(toFollow)
            print("\nYou are now following " + toFollow.username)
            db_session.commit()
            

    def unfollow(self):
        inputedUser = input("\nWho would you like to unfollow?\n")
        toUnfollow = db_session.query(User).where(User.username == inputedUser).first()
        if toUnfollow is None:
            print("\nThat user does not exist!")
        elif toUnfollow not in self.currentUser.following:
            print("\nYou don't follow that user!")
        else:
            self.currentUser.following.remove(toUnfollow)
            print("\nYou no longer follow " + toUnfollow.username)
            db_session.commit()

    def tweet(self):
        content = input("\nCreate Tweet: ")
        tags = input("\nEnter your tags seperated by spaces: ")
        tagList = tags.split()
        tweet = Tweet(content = content, timestamp = datetime.now(), username = self.currentUser.username)
        db_session.add(tweet)
        db_session.flush()
        for t in tagList:
            existing = db_session.query(Tag).where(Tag.content == t).first()
            if existing is None:
                tag = Tag(content = t)
                db_session.add(tag)
                db_session.flush()
                tweet.tags.append(tag)
            else:
                tweet.tags.append(existing)
        db_session.commit()



        db_session.commit()
        
    def view_my_tweets(self):
        tweets = db_session.query(Tweet).where(Tweet.username == self.currentUser.username)
        self.print_tweets(tweets)
    
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        tweets = db_session.query(Tweet).all()
        following = list(map(lambda x: x.username, self.currentUser.following))
        tweets = list(filter(lambda x: x.username in following, tweets))[-5:]
        self.print_tweets(tweets)


    def search_by_user(self):
        usernameToSearch = input("Search user: ")
        user = db_session.query(User).where(User.username == usernameToSearch).first()
        if user is None:
            print("\nThat user doesn't exist!")
        else:
            tweets = db_session.query(Tweet).where(Tweet.username == user.username)
            self.print_tweets(tweets)
        

    def search_by_tag(self):
        tagToSearch = input("Search tag: ").replace("#", "")
        tag = db_session.query(Tag).where(Tag.content == tagToSearch).first()
        tweets = db_session.query(Tweet).all()
        tweets = list(filter(lambda x: tag in x.tags, tweets))
        if len(tweets) == 0:
            print("That tag doesn't have any tweets yet!")
        else:
            self.print_tweets(tweets)


    """
    Allows the user to select from the 
    ATCS Twitter Menucu
    """
    def run(self):
        init_db()

        running = True
        print("Welcome to ATCS Twitter!")
        self.startup()

        while(running):
            self.print_menu()
            option = int(input(""))
            if option == 1:
                self.view_feed()
            elif option == 2:
                self.view_my_tweets()
            elif option == 3:
                self.search_by_tag()
            elif option == 4:
                self.search_by_user()
            elif option == 5:
                self.tweet()
            elif option == 6:
                self.follow()
            elif option == 7:
                self.unfollow()
            else:
                self.logout()
                running = False
        
        self.end()
