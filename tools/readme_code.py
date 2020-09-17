from eventhandler import EventHandler


class ChatRoom:
    """Simulates a chatroom environment with event handler implementation.

    This is just a documented sample without pretensions. It is not a real class implementation.
    """

    def __init__(self):
        """Initialize the chat room."""
        self.__messages = []  # Stores users messages
        self.__users = {'bot': []}  # Stores a dictionary with registered usernames

        # Define the event handler and make it public outside the class to let externals subscriptions to events.
        self.event_handler = EventHandler('onNewuser', 'onMessage')  # Note that events names are cased sensitive.
        # You can set any number of unique events and asing any number of unique callbacks to fire per event.
        # Is not necessary define events names during initialization, also you can register the event names during
        # run time using register_event method.

        # Lets link some internal class methods to those events as callbacks.
        # Limits are available resources.
        self.event_handler.link(self.__on_newuser_join, 'onNewuser')
        self.event_handler.link(self.__on_message, 'onMessage')

    # Now lets define this two methods to dispatch the events
    # Note this methods are not accesible outside class instance
    # This calbback will be called when onNewUser event happens
    def __on_newuser_join(self, user):
        """Shout in the output telling new user has joined chat room, when onNewuser event happens."""
        print(f'** ChatRoom info ** user {user} has joined the chat ** {len(self.user_list())} user/s **')

    # This callback will be called when onMessage event happens
    def __on_message(self, user, msg):
        """Print the user message in the output, when onMessage event happens."""
        print(f'{user} says:\t {msg}')

    # Now let's define the public methods of the chatroom to be used outside the class
    def user_list(self):
        """Return a list of not bot users."""
        return [user for user in self.__users.keys() if user != 'bot']

    def say(self, user, msg=None):
        """Let user (and bots) send a message to the chat room."""
        if not user in self.__users:
            # if user is not registered fire onNewuser event and recibe it inside the class.
            self.__users[user] = []
            self.event_handler.fire('onNewuser', user)
        if not msg:
            return
        if msg != '':
            # Enqueue the message and fire onMessage event to be received internally by __on_message method.
            self.__messages.append((user, msg))
            self.event_handler.fire('onMessage', user, msg)


class ChatBot:
    """Basic chatbot to link/subscribes to the chatroom class events and operate some interactions with users."""

    def __init__(self, chatroom: ChatRoom, name: str = 'bot'):
        self.chatroom = chatroom
        self.name = name

        # Subscribe to external ChatRoom class events
        chatroom.event_handler.link(self.saludate_new_user, 'onNewuser')
        chatroom.event_handler.link(self.read_user_message, 'onMessage')

    # When chatroom fires the onNewUser event our bot will saludate will link this method.
    def saludate_new_user(self, user):
        """Bot saludates the user."""
        chat.say('bot', f'Hello {user}, welcome to the chat room.')

    # When chatroom fires the onNewMessage event process it and broadcast some output to the chatroom if possible.
    def read_user_message(self, user, msg):
        """Read user messages and act in consequece."""
        if user == 'bot':
            # Please don't process yourself messages bot...
            return

        # check if the recibed message is answerable and reply if possible
        if msg == f'Hey {self.name}, are there anyone here?':
            if len(self.chatroom.user_list()) < 1:
                self.chatroom.say(self.name, f'Nope {user}. Just you and me.')
            elif len(self.chatroom.user_list()) == 2:
                self.chatroom.say(self.name, f'Yes {user}. '
                f'there are {len(self.chatroom.user_list()) - 1} non bots users in the room, you, and me.')
            else:
                self.chatroom.say(self.name, f'Yes {user}. '
                f'there are {len(self.chatroom.user_list()) - 2} non bots users in the room, you, and me.')
        return


# Python program starts execution here
if __name__ == '__main__':
    # Create the chatroom
    chat = ChatRoom()

    # Initilize ChatBot class with the ChatRoom instance as param to let subscribe it to the chat events.
    bot = ChatBot(chat)

    # Now the chat simulation. The first user interaction will send a message onNewuser event will be fired and
    # managed by the bot. All messages (onMessage event) will be reached by the bot.
    chat.say('sergio', 'Hello World!')
    chat.say('sergio', 'Hey bot, are there anyone here?')
    chat.say('david', 'Hello everybody!')
    chat.say('david', 'Hey bot, are there anyone here?')
    chat.say('sergio', 'Hi david!')
    chat.say('kate')
    chat.say('kate', 'Hey bot, are there anyone here?')
