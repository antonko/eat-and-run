# Жри и беги

## Описание

Бот для телеграмма для отслеживания потребления еды и тренировок

# Development

В качестве базы данных используется gel.

## Запуск базы данных gel

```bash
docker compose up
```

## Access

http://localhost:5656/ui/

* login: test
* password: test

Миграции

```bash
gel migration create --dsn gel://test:test@localhost:5656/main --tls-security insecure
```

```bash
gel migrate --dsn gel://test:test@localhost:5656/main --tls-security insecure
```

Генерация функций

```bash
gel-py --dsn gel://test:test@localhost:5656/main --tls-security insecure
```
