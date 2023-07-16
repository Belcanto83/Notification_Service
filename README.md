# Сервис уведомлений

## Решаемая задача

Сервис управления рассылками сообщений клиентам на внешнее `API` и получения статистики по выполненным рассылкам.
Для увеличения скорости работы сервиса рассылки осуществляются параллельно в асинхронном режиме с использованием `Celery` и `Celery beat`.

## Описание

Реализовано `API` для:

* добавления нового клиента в справочник со всеми его атрибутами
* обновления данных атрибутов клиента
* удаления клиента из справочника
* добавления новой рассылки со всеми её атрибутами
* получения общей статистики по созданным рассылкам и количеству отправленных сообщений по ним с группировкой по статусам
* получения детальной статистики отправленных сообщений по конкретной рассылке
* обновления атрибутов рассылки
* удаления рассылки
* обработки активных рассылок и отправки сообщений клиентам

## Логика рассылки

* После создания новой рассылки, если текущее время больше времени начала и меньше времени окончания - выбираются из справочника все клиенты, которые подходят под значения фильтра, указанного в этой рассылке и запускается отправка сообщений для всех этих клиентов на внешнее API.
* Если создаётся рассылка с временем старта в будущем - отправка сообщений начинается автоматически по наступлению этого времени без дополнительных действий со стороны пользователя системы.
* По ходу отправки сообщений собирается статистика для последующего формирования отчётов.

## Выполненные дополнительные задания
* (1) организовано тестирование написанного кода (минимальное покрытие кода тестами на данный момент)
* (2) организована автоматическая сборка/тестирование с помощью GitHub Actions
* (3) подготовлен docker-compose для запуска всех сервисов проекта одной командой (в начальной стадии)
* (5) по адресу /docs/ открывается страница Swagger UI и в ней отображается описание разработанного API
* (6) частично реализован администраторский Web UI для управления рассылками и получения статистики по отправленным сообщениям
* (9) удаленный сервис может быть недоступен, долго отвечать на запросы или выдавать некорректные ответы. Организована обработка ошибок и откладывание запросов при неуспехе для последующей повторной отправки. Задержки в работе внешнего сервиса никак не должны оказывать влияние на работу сервиса рассылок.

## Предпосылки

* установлен `git`
* установлены `python3 & pip`
* установлена СУБД `PostgreSQL`
* установлены `docker & docker-compose`
* установлен `менеджер баз данных` (например, DBeaver)

## Запуск проекта в тестовом режиме на `localhost`

Для запуска проекта необходимо:

1. Клонировать репозиторий проекта

```bash
git clone https://...
```

2. Перейти в папку проекта, активировать виртуальное окружение и установить зависимости:

```bash
. venv/Scripts/activate && \
pip install -r requirements.txt
```

3. В корне проекта создать файл `.env` и указать в нём переменные окружения:

```base
SECRET_KEY=...
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=notification_service
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
API_TOKEN=...
```

4. Создать базу данных (БД) в PostgreSQL с именем **notification_service**:

```bash
createdb -U <username> notification_service
```

5. Применить миграции к БД:

```bash
python manage.py migrate
```

6. Выполнить команду:

```bash
docker-compose up -d
```

7. Выполнить команду:

```bash
celery -A notification_service worker -l info # Linux
celery -A notification_service worker -l info -P threads # Windows
```

8. Выполнить команду:

```bash
python manage.py runserver
```

9. Выполнить команду:

```bash
celery -A notification_service beat -l info
```
