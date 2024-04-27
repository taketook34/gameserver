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
типо информативная

####/register 
регистрация, пол. токена

####/login 
авторизация

####/tic-tac-toe/creategame GET
ДОСТУП: любой пользователь не в игре (проверять по токену)
создание игры, регистрирует пользователя под токеном как хоста, возвращает токен комнаты

####/tic-tac-toe/joingame/<токен игровой сессии> GET
ДОСТУП: Любой пользователь кроме хоста не в игре (проверять по токену)
присоиденение пользователя гостя, начало игры. возвращает True/False если подключение получилось/не вышло

####/tic-tac-toe/game-turn/<токен игровой сессии> POST
ДОСТУП: игрок хост и игрок гост у которого ход (проверять по токену)
Пользователь отправляет на сервер свое измение игровой карты

<pre>
request:
POST {
    "X": 1,
    "Y": 1, 
}

response:
{
    # елси запрос верный 
    "is_succesful": "True",
    .... game data ... 
}

{
    # елси запрос верный 
    "is_succesful": "False",
    "error-message": "Some message",
}
</pre>

####/tic-tac-toe/game-info/<токен игровой сессии> GET
ДОСТУП: игрок хост и игрок гост (проверять по токену)
возвращение всех игровых данных сессии. если игра окончена то происходит выведение окончательных данных игры которые не изменяются

<pre>
response:
{

    #.... game data ... 
    "game-started": "True",
    "game-ended": "False",
    "map":
    [
        ['', '', ''],
        ['', '', ''],
        ['', '', ''],
    ],
    "turn-num": n,
    "user-turn": &lt; id пользователя &gt;
    "winner": None,

}
</pre>

####/tic-tac-toe/deletegame/<токен игровой сессии> DELETE
ДОСТУП: игрок хост и игрок гость  (проверять по токену) 
удаление игры (удаление записи в базе данных)

