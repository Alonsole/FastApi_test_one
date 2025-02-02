## Домашнее задание к лекции «Создание REST API на FastApi» часть 2
### Доработка FastApi сервиса объявлений купли/продажи - [Часть 1](https://github.com/Alonsole/FastApi_test_one)

У объявлений реализованы следующие поля:
```
заголовок
описание
цена
автор
дата создания
```
Реализованы следующе методы:
```
Создание Объявления: POST /advertisement
Обновление Объявления: PATCH /advertisement/{advertisement_id}
Удаление Объявления: DELETE /advertisement/{advertisement_id}
Получение Объявления по id: GET  /advertisement/{advertisement_id}
Поиск Объявления по полям: GET /advertisement?{query_string}
Создание пользователя POST /user/create 
Авторизация пользовалетя POST /user/login 
Получить информцию о юзере по ID GET /user/{user_id?}
Обновление логина или пароля пользователя по ID PATCH /user/{user_id}
Удаление аккаунта DELETE /user/{user_id}
```
Реализованы 2 роли: admin и user.  
Описание прав:  

Права неавторизованного пользователя (клиент может токен не передавать):
```
Создание пользователя POST /user/create 
Вход пользователя POST /user/login 
Получение пользователя по id GET /user/{user_id} 
Получение объявления по id GET /advertisement/{advertisement_id} 
Поиск объявления по полям GET /advertisement?{query_string}  
```
Права авторизованного пользователя с группой user:
```
все права неавторизованного пользователя
обновление своих данных PATCH /user/{user_id}
удаление себя DELETE /user/{user_id}
создание объявления POST /advertisement  
обновление своего объявления PATCH /advertisement/{advertisement_id}
удаление своего объявления DELETE /advertisement/{advertisement_id}
```
Права авторизованного пользователя с группой admin:
```
любые действия с любыми сущностям
Если у пользователя недостаточно прав для выполнения операции, то возвращается ошибка 403
```
Срок действия токена настраивается.

Для шифрования паролей используется [bcrypt](https://github.com/pyca/bcrypt/)

### Ссылка на официальный ресурс: [FastApi](https://fastapi.tiangolo.com/ru/)

[Прочитать Документацию проекта](https://github.com/Alonsole/FastApi_test_one/blob/task_2/Documentation.md)

### Требования
Python 3.10 +  
PostgreSQL  
Docker Desktop (опционально)  

### Лицензия
Это учебный проект вне коммерческих целей.

### Контакты
Проект не предполагает взаимодействий с пользователями.