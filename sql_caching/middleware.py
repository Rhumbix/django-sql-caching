'''
Hack to cache SELECT statements inside a single Django request. The patch() method replaces
the Django internal execute_sql method with a stand-in called execute_sql_cache. That method
looks at the sql to be run, and if it's a select statement, it checks a thread-local cache first.
Only if it's not found in the cache does it proceed to execute the SQL. On any other type of
sql statement, it blows away the cache. There is some logic to not cache large result sets,
meaning anything over 100 records. This is to preserve Django's lazy query set evaluation.
'''
from threading import local
import itertools
from django.db.models.sql.constants import MULTI
from django.db.models.sql.compiler import SQLCompiler
from django.db.models.sql.datastructures import EmptyResultSet
from django.db.models.sql.constants import GET_ITERATOR_CHUNK_SIZE


_thread_locals = local()


def get_sql(compiler):
    ''' get a tuple of the SQL query and the arguments '''
    try:
        return compiler.as_sql()
    except EmptyResultSet:
        pass
    return ('', [])


def execute_sql_cache(self, result_type=MULTI):

    if hasattr(_thread_locals, 'query_cache'):

        sql = get_sql(self)  # ('SELECT * FROM ...', (50)) <= sql string, args tuple
        if sql[0][:6].upper() == 'SELECT':

            # uses the tuple of sql + args as the cache key
            if sql in _thread_locals.query_cache:
                return _thread_locals.query_cache[sql]

            result = self._execute_sql(result_type)
            if hasattr(result, 'next'):

                # only cache if this is not a full first page of a chunked set
                peek = result.next()
                result = list(itertools.chain([peek], result))

                if len(peek) == GET_ITERATOR_CHUNK_SIZE:
                    return result

            _thread_locals.query_cache[sql] = result

            return result

        else:
            # the database has been updated; throw away the cache
            _thread_locals.query_cache = {}

    return self._execute_sql(result_type)


class QueryCacheMiddleware:
    def process_request(self, request):
        _thread_locals.query_cache = {}

    def process_response(self, request, response):
         _thread_locals.query_cache = {}
         return response

''' patch the django query runner to use our own method to execute sql '''
if not hasattr(SQLCompiler, '_execute_sql'):
    SQLCompiler._execute_sql = SQLCompiler.execute_sql
    SQLCompiler.execute_sql = execute_sql_cache


