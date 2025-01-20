## Домашнее задание к лекции «Создание REST API на FastApi» часть 1
### FastApi сервис объявлений купли/продажи
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
Создание: POST /advertisement
Обновление: PATCH /advertisement/{advertisement_id}
Удаление: DELETE /advertisement/{advertisement_id}
Получение по id: GET  /advertisement/{advertisement_id}
Поиск по полям: GET /advertisement?{query_string}
```
Авторизация и аутентификация будет реализована во [второй части](https://github.com/Alonsole/FastApi_test_one/tree/task_2) 

### Ссылка на официальный ресурс: [FastApi](https://fastapi.tiangolo.com/ru/)

[Прочитать Документацию проекта](https://github.com/Alonsole/FastApi_test_one/blob/main/Documentation.md)

### Требования
Python 3.10 +  
PostgreSQL  
Docker Desktop (опционально)  

### Лицензия
Это учебный проект вне коммерческих целей.

### Контакты
Проект не предполагает взаимодействий с пользователями.
