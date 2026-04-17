# TZ Mobile Backend

Обычный backend на Django + DRF + PostgreSQL для тестового задания.

Тут есть регистрация, логин, JWT токены, роли, права и всё такое.

## Как запустить проект (по шагам)

### 1. Скачать проект

```bash
git clone <ссылка_на_репозиторий>
cd tz_mobile_backend
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

### 3. Активировать окружение

Для Windows:

```bash
.venv\Scripts\activate
```

Для Mac/Linux:

```bash
source .venv/bin/activate
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

### 5. Создать файл .env

Скопируй пример:

```bash
copy .env.example .env
```

Открой `.env` и пропиши там:

```
SECRET_KEY=твой_секретный_ключ
DEBUG=True
DB_NAME=имя_бд
DB_USER=пользователь
DB_PASSWORD=пароль
DB_HOST=localhost
DB_PORT=5432
```

### 6. Создать базу данных PostgreSQL

Зайди в psql или pgAdmin и создай базу с именем, которое указал в `DB_NAME`.

### 7. Применить миграции

```bash
python manage.py migrate
```

### 8. Заполнить роли и права тестовыми данными

```bash
python manage.py seed_roles_permissions
```

### 9. Запустить сервер

```bash
python manage.py runserver
```

Сервер запустится на `http://127.0.0.1:8000/`

## Как проверять руками

1. Зарегистрируй пользователя

   `POST /api/auth/register/`

   Отправь JSON:

   ```json
   {
     "first_name": "Иван",
     "last_name": "Иванов",
     "middle_name": "Иванович",
     "email": "ivan@example.com",
     "password": "123456",
     "password_repeat": "123456"
   }
   ```

2. Войди

   `POST /api/auth/login/`

   ```json
   {
     "email": "ivan@example.com",
     "password": "123456"
   }
   ```

   Получишь токен.

3. Скопируй токен и добавь в заголовки:

   ```
   Authorization: Bearer твой_токен
   ```

4. Проверь профиль:

   `GET /api/users/me/`

5. Посмотри товары, магазины, заказы:

   `GET /api/products/`
   `GET /api/stores/`
   `GET /api/orders/`

6. Выйди:

   `POST /api/auth/logout/`

7. Удали аккаунт:

   `DELETE /api/users/me/`

## Какие есть роли

- `admin` — может всё
- `manager` — может управлять товарами и заказами
- `user` — обычный пользователь
- `guest` — только смотрит товары и магазины

## Важные моменты

- Логин по `email`, а не по имени пользователя
- Токен — это JWT access token, без refresh
- Токены умирают при logout (попадают в blacklist)
- Удаление аккаунта — мягкое (просто блокируется)
- Права проверяются через роли и `AccessRule`

## Структура папок (если интересно)

```
tz_mobile_backend/
├── users/              # пользователи, роли, права
├── products/           # товары (mock)
├── stores/             # магазины (mock)
├── orders/             # заказы (mock)
├── tz_mobile_backend/  # настройки проекта
├── requirements.txt
├── .env.example
└── manage.py
```


