import monitor

try:
    import bottle as _bottle
    import sqlalchemy as _sqlalchemy
except ImportError:
    server = False
else:
    server = True
    import orm
    import webapi
    