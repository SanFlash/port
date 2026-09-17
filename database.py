"""SQLAlchemy schema compatible with the supplied Prisma PostgreSQL tables."""
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import (MetaData, Table, Column, String, Integer, Boolean, DateTime,
                        JSON, Enum, Index, select, insert)
from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()
json_type = JSON().with_variant(JSONB(), 'postgresql')
def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)
def identity():
    return uuid.uuid4().hex
def key():
    return Column('id', String, primary_key=True, default=identity)
def created():
    return Column('createdAt', DateTime, nullable=False, default=now)
def updated():
    return Column('updatedAt', DateTime, nullable=False, default=now, onupdate=now)

profile = Table('Profile', metadata, key(), Column('name', String, nullable=False),
    Column('headline', String, nullable=False), *[Column(n, String) for n in
    ['location', 'email', 'phone', 'intro', 'summary']], updated())
items = Table('CollectionItem', metadata, key(), Column('collection', String, nullable=False),
    Column('title', String, nullable=False), Column('slug', String, unique=True),
    Column('status', Enum('DRAFT', 'PUBLISHED', 'PRIVATE', 'ARCHIVED', name='Visibility'), nullable=False, default='DRAFT'),
    Column('featured', Boolean, nullable=False, default=False),
    Column('position', Integer, nullable=False, default=0), Column('data', json_type, nullable=False, default=dict),
    Column('source', String, nullable=False, default='manual'), created(), updated())
Index('CollectionItem_collection_status_position_idx', items.c.collection, items.c.status, items.c.position)
media = Table('Media', metadata, key(), Column('name', String, nullable=False),
    Column('url', String, nullable=False), Column('mimeType', String, nullable=False),
    Column('size', Integer), Column('alt', String), created())
contacts = Table('ContactSubmission', metadata, key(), Column('name', String, nullable=False),
    Column('email', String, nullable=False), Column('company', String), Column('message', String, nullable=False),
    Column('projectType', String), Column('budget', String), Column('timeline', String),
    Column('status', String, nullable=False, default='new'), created())
events = Table('AnalyticsEvent', metadata, key(), Column('name', String, nullable=False),
    Column('path', String, nullable=False), Column('metadata', json_type), created())
Index('AnalyticsEvent_createdAt_path_idx', events.c.createdAt, events.c.path)

def initialize(engine):
    # Creates missing tables only; it never drops or replaces existing data.
    metadata.create_all(engine)

def seed(engine):
    data = json.loads((Path(__file__).parent / 'data/database_seed.json').read_text())
    with engine.begin() as conn:
        if not conn.execute(select(profile.c.id).where(profile.c.id == 'profile')).first():
            conn.execute(insert(profile).values(**data['profile']))
        for collection, title, content in data['items']:
            slug = re.sub(r'[^a-z0-9]+', '-', f'{collection}-{title}'.lower())
            if not conn.execute(select(items.c.id).where(items.c.slug == slug)).first():
                conn.execute(insert(items).values(collection=collection, title=title,
                    slug=slug, data=content, status='PUBLISHED'))
