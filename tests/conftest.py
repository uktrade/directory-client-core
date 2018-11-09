def pytest_configure():
    from django.conf import settings
    settings.configure(
        DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS=10,
        CACHES={
            'fallback': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake',
            }
        }
    )
