# Depoly

## How to depoly in fly.io:

reference
*  [https://testdriven.io/blog/django-fly/](https://testdriven.io/blog/django-fly/)
*  [https://github.com/tomwojcik/django-fly.io-example-project](https://github.com/tomwojcik/django-fly.io-example-project)
*  [https://fly.io/docs/reference/redis/](https://fly.io/docs/reference/redis/)


### requirements

1. [Flyctl](https://fly.io/docs/flyctl/installing/)

### Step
1.  ```$ flyctl auth login```
    > to create account and log in 

1. ```$ flyctl launch```

    ```
    An existing fly.toml file was found for app amex-map
    ? Would you like to copy its configuration to the new app? No
    Creating app in D:\AMEX
    Scanning source code
    Detected a Django app
    ? Overwrite "D:\AMEX\Dockerfile"? No
    ? Create .dockerignore from 2 .gitignore files? No
    ? Choose an app name (leave blank to generate one):
    PS D:\AMEX> flyctl launch
    An existing fly.toml file was found for app amex-map
    ? Would you like to copy its configuration to the new app? Yes
    Creating app in D:\AMEX
    Scanning source code
    ? Create .dockerignore from 2 .gitignore files? No
    ? Choose an app name (leave blank to generate one): amex-map
    automatically selected personal organization: ..@gmail.com
    ? Choose a region for deployment: Hong Kong, Hong Kong (hkg)
    ```

1. ```$ flyctl pg create```

    ```
    ? Choose an app name (leave blank to generate one): amex-map-db
    automatically selected personal organization: @gmail.com
    ? Select region: Hong Kong, Hong Kong (hkg)
    ? Select configuration: Development - Single node, 1x shared CPU, 256MB RAM, 1GB disk

    ...

    Postgres cluster amex-map-db created
    Username:    postgres
    Password:    password
    Hostname:    amex-map-db.internal
    Proxy port:  5432
    Postgres port:  5433
    Connection string: postgres://postgres:password@amex-map-db.internal:5432
    ```

1. ```$ flyctl redis create```
    ```
    ? Choose a Redis database name (leave blank to generate one): amex-map-redis

    ? Choose a primary region (can't be changed later) Hong Kong, Hong Kong (hkg)

    Upstash Redis can evict objects when memory is full. This is useful when caching in Redis. This setting can be changed later.
    Learn more at https://fly.io/docs/reference/redis/#memory-limits-and-object-eviction-policies
    ? Would you like to enable eviction? Yes
    ? Optionally, choose one or more replica regions (can be changed later):
    ? Select an Upstash Redis plan Free: 100 MB Max Data Size
    Your Upstash Redis database amex-map-redis is ready.
    Apps in the personal org can connect to at redis://default:password@fly-amex-map-redis.upstash.io
    If you have redis-cli installed, use fly redis connect to connect to your database.
    ```

1. ```$ flyctl redis list ```
    > to look your redis

1. ```$ flyctl apps list```
    > to look your app

1. ```$ flyctl status```
    > to watch your app status
    ```
    App
    Name     = app_name
    Owner    = personal
    Version  = 0
    Status   = pending
    Hostname = app_name.fly.dev
    Platform =
    ```

1. add environments setting in system environments (named 'Secrets' in fly.io)

    ```$ flyctl secrets set DEBUG='1'```

    ```$ flyctl secrets set DATABASE_URL='postgres://postgres:password@amex-map-db.internal:5432/postgres'```

    ```$ flyctl secrets set CELERY_BROKER_URL='redis://default:5babad3ee7f44ec8953dc84889ea1b02@fly-amex-map-redis.upstash.io'```

    ```$ fly secrets set SECRET_KEY='django-insecure-qmq4l#2)h9_!us=2^kw6n&rs$=-wbckvn=$k-2(asbcsf!mey2'```

    or set in onetime

    ```$ flyctl secrets set DEBUG='1 DATABASE_URL='postgres://postgres:password@amex-map-db.internal:5432/postgres' CELERY_BROKER_URL='redis://default:5babad3ee7f44ec8953dc84889ea1b02@fly-amex-map-redis.upstash.io' SECRET_KEY='django-insecure-qmq4l#2)h9_!us=2^kw6n&rs$=-wbckvn=$k-2(asbcsf!mey2'```

1. ```$ flyctl secrets list```
    > Check environments setting(Secrets in fly.io)

1. ```$ fly deploy ```
    > depoly

1. ```$ fly status```
    > to watch your app status

1. ```$ fly logs```
    > watch logs








### problem

1. non interactive (in Windows)
    ```
    $fly redis create
    automatically selected personal organization: xxxxx@gmail.com
    Error prompt: non interactive
    ```
    use 
    [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=en-us&gl=us) to ```$ fly redis create``` again
