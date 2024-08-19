import os

from peewee import SqliteDatabase

from metrics.common.util import get_cache_dir

db = SqliteDatabase(os.path.join(get_cache_dir(), "campaign.db"))
db.connect(reuse_if_open=True)
