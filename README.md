django-sql-caching
==========================

[Rails SQL Caching](http://guides.rubyonrails.org/caching_with_rails.html#sql-caching) implemented in Django. SQL query result returned by the same query will be cached for *current request only*. The cache will be cleared at the end of the request.

## Installing

```bash
$ pip install django-sql-caching
```

Then add ```sql_caching.middleware.QueryCacheMiddleware``` to your ```MIDDLEWARE_CLASSES```.

Finally watch your query counts/request goes down by 20-80%!

#Caveat

django-sql-caching will break for this rare situation:
- in a request an object is retrieved from DB, cached in memory by django-sql-caching;
- later in the same request, this object is modified and saved back to the DB;
- again in the same request, you try to retrieve the same object with the same query;
- the cached, now outdated, object will be returned.

If you did run into this rare situation, the workaround is to add the following right before you try to retrieve the same object the 2nd time:
``` import threading; threading.local().query_cache = {}```

## Enjoy!

Email me with any questions: [kenneth.jiang@gmail.com](kenneth.jiang@gmail.com).

#Acknowledgement
This package is based on [this article](http://chase-seibert.github.io/blog/2013/01/17/caching-selects-per-request-django.html) published by [Chase Seibert](http://chase-seibert.github.io/blog/index.html) 
