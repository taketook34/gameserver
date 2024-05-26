##Игровой веб сервер:

Игры:
1. Крестики нолики

###Структура проекта:

Веб сервер который выдает данные игровой сесси и веб клиент который берет эти данные и выводит их пользователю.

###Структура БД:

####Пользователь:
Имя 
пароль
В игре (да/нет)
У пользователя будет свой токен при авторизации.

####Игровая сессия крестиков-ноликов:
Токен комнаты
статус начала игры (да/нет)
статус окончания игры(да/нет)
пользователь-хоста
пользователь-гостя
очередь хода (пользователь)
номер хода
данные игровой карты (надо продумать как их хранить)
победитель (пользователь)

###Ендпоинты:

####/home 
информативный ендпоинт, просто тестовый

####/register POST
Регистрация 
ДОСТУП: все юзеры
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

####/login 
Авторизация 
ДОСТУП: все 
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

####/tic-tac-toe/creategame GET
Создание игры
ДОСТУП: зарегистрированый пользователь

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

203 (если пользователь нахоится в другой игре уже):
{
    "message": "User currently in another game"
}


</pre>

####/tic-tac-toe/joingame/<токен игровой сессии> GET
ДОСТУП: Любой пользователь кроме хоста не в игре (проверять по токену)
присоиденение пользователя гостя, начало игры. возвращает True/False если подключение получилось/не вышло

<pre>
SEND: GET

200: 
{"message": f"You conneted to {game_token} game"}

403 (если пользователь нахоится в другой игре уже):
{
    "message": "User currently in another game"
}

403 (Если хост подклчается к своей же игре):
{"error": f"Host cant be a guest!"}

403 (если игра не найдена)
{"error": f"Game is not available"}


</pre>


####/tic-tac-toe/game-turn/<токен игровой сессии> POST
ДОСТУП: игрок хост и игрок гост у которого ход (проверять по токену)
Пользователь отправляет на сервер свое измение игровой карты

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

403 (игра не существует):
{"error": "Game not found"}

403 (если юзер не участник игры) 
{"error": "Wrong user"}

403 (игра уже окончена)
{"error": "Game is over", "winner": &lt;айди юзера&gt;}

403 (игра не начата)
{"error": "Game not started"}

203 (если хо другого игрока)
{"error": "Not user turn"}

203
{"error": "Cage is filled"}


</pre>

####/tic-tac-toe/game-info/<токен игровой сессии> GET
ДОСТУП: игрок хост и игрок гост (проверять по токену)
возвращение всех игровых данных сессии. если игра окончена то происходит выведение окончательных данных игры которые не изменяются

<pre>
200 (запрос успешный):
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
</pre>

####/tic-tac-toe/deletegame/<токен игровой сессии> DELETE
ДОСТУП: игрок хост и игрок гость  (проверять по токену) 
удаление игры (удаление записи в базе данных)

<pre>
200 (запрос успешный):
{"message": f"Succes deletion game sdfsdf123"}

403 (пользователь не хост игры)
{"error": "You cannot delete game!"}

403 (пользователь )
{"error": "Game with this token doesn\'t exist"}
</pre>