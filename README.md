# Список доступных запросов:
1. создать пользователя
1. активировать пользователя
1. войти в аккаунт и получить токен
1. Войти в аккаунт и удалить токен
1. получить данные всех пользователей
1. получить данные выбранного пользователя
1. изменить данные пользователя
1. удалить своего пользователя
1. сброс пароля - и получить письмо с токеном
1. сброс пароля - подтверждение и установка нового пароля
1. создание подписки на пользователя ("author")  
1. удаление подписки
1. просмотр списка своих подписок
1. просмотр списка своих подписчиков
1. просмотр всех публикаций   -  проверить до какого уровня выдает
1. просмотр публикации(поста или комментария) по id, если указан параметр "nests_down" - выдаст также вложенные комментарии до указанного количества уровней, "nests_down": "all" - до последнего уровня вложенности
1. создание поста, если указатать "parent_id" - публикация будет комментарием к публикации с указанным id
1. Удаление поста по id
1. Для постов сделана фильтрация по автору и дате создания через query string
1. Просмотр ленты (всех постов авторов из списка подписок)

Примеры запросов: [requests_examples.http](https://github.com/headsoft-mikhail/blog_api/blob/master/requests_examples.http)  
  
# Заданные запросы:
- Добавление статьи/комментария:
```
POST {{baseUrl}}/posts/
Content-Type: application/json
Authorization: Token {{session_token}}

{
  "content": "weafiuhewru9fgdfg",
  "parent_id": "1"
}
```
- Просмотр поста по id  с получением комментариев до 3 уровня:
```
GET {{baseUrl}}/posts/2/
Content-Type: application/json
Authorization: Token {{session_token}}

{
  "nests_down": 3
}
```
- Получение всех комментариев к посту/комментарию:
```
GET {{baseUrl}}/posts/2/
Content-Type: application/json
Authorization: Token {{session_token}}

{
  "nests_down": "all"
}
```

# Основной сценарий работы:

1. Пользователь создает аккаунт указав в запросе параметры: first_name, last_name, email, password. Получает на указанную электронную почту письмо с 5-значным токеном подтверждения почтового адреса. Отправляет запрос подтверждения почты с указанием полученного токена.
1. Пользователь входит в созданный аккаунт, получая токен. Дальнейшие запросы выполняются с использованием этого токена.
1. Пользователь может подписываться на других пользователей, просматривать и создавать посты и комментарии к ним.


# Комментарии:

1. Для запуска из директории проекта выполнить
```
docker-compose up
```
2. При этом в файле  [./docker/django/email.env](https://github.com/headsoft-mikhail/blog_api/blob/master/docker/django/email.env) необходимо указать корректные значения параметров
3. Добавлен простой DRF тротлинг
4. Отправка почтовых сообщений вынесена в celery-приложение ([netology_pd_diplom/celery.py](https://github.com/headsoft-mikhail/netology_graduation/blob/master/netology_pd_diplom/celery.py), [backend/tasks.py](https://github.com/headsoft-mikhail/netology_graduation/blob/master/backend/tasks.py)). 


# Планы на дальнейшую проработку

1. Реализовать возможность просматривать публикации и выводить только непросмотренные
1. Проработка прав доступа
1. Обработка ошибок
