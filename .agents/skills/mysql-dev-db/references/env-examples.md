# 数据库环境变量示例

## 通用 `.env`

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=app_dev
DB_USERNAME=root
DB_PASSWORD=
DB_CHARSET=utf8mb4
```

## MySQL 前缀变量

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=app_dev
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_CHARSET=utf8mb4
```

## ThinkPHP / FastAdmin 常见 `.env`

```ini
[DATABASE]
TYPE = mysql
HOSTNAME = 127.0.0.1
DATABASE = test_ai_com
USERNAME = test_ai_com
PASSWORD = password
HOSTPORT = 3306
CHARSET = utf8mb4
PREFIX = fa_
```

## DATABASE_URL

```dotenv
DATABASE_URL=mysql://user:password@127.0.0.1:3306/app_dev
```

## `.ai/config.json` 回退配置

```json
{
  "mysql_dev_db": {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "dev",
    "password": "",
    "database": "app_dev",
    "charset": "utf8mb4"
  }
}
```

只填写需要指定的项；省略项或 `null` 会继续读取数据库专用环境变量。`password: ""` 明确表示空密码。包含真实密码的配置不要提交到仓库。
