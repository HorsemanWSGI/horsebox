from typing import Callable, Mapping, Iterable


WSGICallable = Callable[[Mapping, Callable], Iterable[bytes]]
WSGIServer = Callable[[WSGICallable], None]
WSGIMiddleware = Callable[[WSGICallable], WSGICallable]
