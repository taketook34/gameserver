<p style="font-size: 24px;">Game server:</p>

Games:
1. Tic-Tac-Toe

<p style="font-size: 20px;">Структура проекта:</p>

A web server that outputs data to the game session and a web client that takes that data and outputs it to the user.


<p style="font-size: 20px;">Endpoints:</p>


<b>/register POST</b>
Registration
Acces: all users
<pre>
SEND: 
{
    "nickname": "somename",
    "email": "someemail3@gmail.com.com",
    "password": "some password"
}

200:
{
    "message": "succes",
    "user_data": 
        {
            "id": 1,
            "nickname": "some nickname",
            "email": "someemail3@gmail.com.com",
        }

}
</pre>

<b>/login </b>
Autorisation
Access: all
<pre>
SEND: POST
{
    "nickname": "somename",
    "password": "somepassword"
}

200: 
{
    "access_token": "&lt;token&gt;",
    "message": "succes login"
}

400:
{
    "error": "error message"
}


</pre>

<b>/tic-tac-toe/creategame GET</b>
Game room creation
Access: autorised user

<pre>
SEND: GET

200: 
{
    "id": 1, 
    "game_token": "sdfsdfsdf"
    "user_host_id": 1,
    "is_game_started": 0,
    "turn": 0,
    "date": "Fri, 24 May 2024 08:57:55 GMT",
}

203 (if user in another game):
{
    "message": "User currently in another game"
}


</pre>

####/tic-tac-toe/joingame/&lt;game session token&gt; GET
ACCESS: Any user except the host not in the game (check by token)
Joining a guest user, starting the game. Returns True/False if the connection was successful/failed

<pre>
SEND: GET

200:
{"message": f"You conneted to {game_token} game"}

403 (if the user is already in another game):
{
    "message": "User currently in another game"
}

403 (If the host connects to his own game):
{"error": f"Host cant be a guest!"}

403 (if game not found)
{"error": f"Game is not available"}


</pre>


<b>/tic-tac-toe/game-turn/&lt;game session token&gt; POST</b>
ACCESS: host player and guest player whose turn (check by token)
The user sends their game map change to the server

<pre>
SEND: POST 
{
    "X": 1,
    "Y": 1, 
}

200 
{
    "message": "Succesful attempt to make turn", 
    "game_data": 
    {
        "id": 12,
        "game_token": sdfgsf123,
        "is_game_started": 1,
        "is_game_ended": 0,
        "user_host_id": 1,
        "user_guest_id": 4,
        "user_turn": 1,
        "game_turn": 12,
        "game_data": [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        "winner": none,
    },

}

403 (game does not exist):
{"error": "Game not found"}

403 (if user is not a game participant)
{"error": "Wrong user"}

403 (game is over)
{"error": "Game is over", "winner": &lt;айди юзера&gt;}

403 (game not started)
{"error": "Game not started"}

203 (another pkayer turn)
{"error": "Not user turn"}

203
{"error": "Cage is filled"}


</pre>

/tic-tac-toe/game-info/&lt;game session token&gt; GET
ACCESS: host player and guest player (check by token)
Returns all game session data. If the game is over, the final game data is displayed, which does not change.

<pre>
200 (successful request):
{
    "message": "Successful attempt to get game info",
    "game_data":
    {
        "id": 12,
        "game_token": "sdfgsf123",
        "is_game_started": 1,
        "is_game_ended": 0,
        "user_host_id": 1,
        "user_guest_id": 4,
        "user_turn": 1,
        "game_turn": 12,
        "game_data": [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ],
        "winner": "none",
    },

}
</pre>

/tic-tac-toe/deletegame/&lt;game session token&gt; DELETE
 ACCESS: host player and guest player (check by token)
 Deletes the game (deletes the record from the database)

<pre>
200 (successful request):
{"message": f"Successful deletion of game sdfsdf123"}

403 (user is not the game host)
{"error": "You cannot delete game!"}

403 (wrong game session token )
{"error": "Game with this token doesn't exist"}
</pre>
