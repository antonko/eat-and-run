# GEL

## Run

```bash
docker compose up
```

## Access

http://localhost:5656/ui/

Миграции

```bash
gel migration create --docker
```

```bash
gel migrate --docker
```

Заходим в UI

```bash
gel ui --docker
```

```bash
gel --dsn gel://username:oldpass@hostname.com --password qwerty
```

```bash
gel-py --dsn gel://test:test@localhost:5656/main --tls-security insecure
```
