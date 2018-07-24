

import us
import pkgutil
import yaml

import numpy as np

from tqdm import tqdm

from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred, relationship

from sqlalchemy import (
    Column, ForeignKey,
    Integer, String, Float, Text, Boolean,
)

from . import logger
from .utils import safe_property
from .db import session, engine


class BaseModel:

    @classmethod
    def column_names(cls):
        """Get a list of column names.
        """
        return cls.__table__.columns.keys()

    def __iter__(self):
        """Generate column / value tuples.

        Yields: (key, val)
        """
        for key in self.column_names():
            if key in self.__dict__:
                yield (key, getattr(self, key))


BaseModel = declarative_base(cls=BaseModel)

BaseModel.query = session.query_property()


# TODO: Country


class Region(BaseModel):

    __tablename__ = 'region'

    wof_id = Column(Integer, primary_key=True)

    wof_country_id = Column(Integer)

    fips_code = Column(String, index=True)

    geonames_id = Column(Integer, index=True)

    geoplanet_id = Column(Integer, index=True)

    iso_id = Column(String, index=True)

    wikidata_id = Column(String, index=True)

    name = Column(String)

    name_abbr = Column(String)

    country_iso = Column(String, index=True)

    name_a0 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    area_m2 = Column(Float)

    def __repr__(self):
        return '%s<%s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.name, self.name_a0, self.wof_id,
        )


# TODO: Make pluggable.
CITY_ALT_NAMES = yaml.load(pkgutil.get_data(
    'litecoder', 'data/city-alt-names.yml'
))


class Locality(BaseModel):

    __tablename__ = 'locality'

    wof_id = Column(Integer, primary_key=True)

    wof_region_id = Column(Integer, ForeignKey(Region.wof_id), nullable=True)

    region = relationship(Region, primaryjoin=(wof_region_id==Region.wof_id))

    dbpedia_id = Column(String, index=True)

    freebase_id = Column(String, index=True)

    factual_id = Column(String, index=True)

    fips_code = Column(String, index=True)

    geonames_id = Column(Integer, index=True)

    geoplanet_id = Column(Integer, index=True)

    library_of_congress_id = Column(String, index=True)

    new_york_times_id = Column(String, index=True)

    quattroshapes_id = Column(Integer, index=True)

    wikidata_id = Column(String, index=True)

    wikipedia_page = Column(String)

    name = Column(String)

    country_iso = Column(String, index=True)

    name_a0 = Column(String)

    name_a1 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    wikipedia_wordcount = Column(Integer)

    elevation = Column(Integer)

    area_m2 = Column(Float)

    @classmethod
    def median_population(cls):
        """Get median population.
        """
        pops = [c.population for c in cls.query if c.population]
        return np.median(pops)

    def __repr__(self):
        return '%s<%s, %s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.name, self.name_a1, self.name_a0, self.wof_id,
        )

    @property
    def completeness(self):
        """Count non-null fields.
        """
        return len([k for k, v in dict(self).items() if v is not None])

    # TODO: Make name list pluggable.
    @property
    def alt_names(self):
        """Map alt names via Wikidata id.
        """
        return CITY_ALT_NAMES.get(self.wikidata_id, [])

    @property
    def names(self):
        """Name + alt names.
        """
        return set((self.name, *self.alt_names))

    # TODO: Get from region?
    @safe_property
    def us_state_abbr(self):
        """A1 name -> US state abbreviation.
        """
        return us.states.lookup(self.name_a1).abbr


# TODO: What to include?
LOCALITY_DUP_COLS = (
    'dbpedia_id',
    'freebase_id',
    'factual_id',
    'fips_code',
    'geonames_id',
    'wikipedia_page',
    'wikidata_id',
)


class LocalityDup(BaseModel):

    __tablename__ = 'locality_dup'

    wof_id = Column(Integer, ForeignKey(Locality.wof_id), primary_key=True)

    @classmethod
    def set_dupe(cls, wof_id):
        """Register duplicate locality.
        """
        try:
            session.add(cls(wof_id=wof_id))
            session.commit()

        except:
            session.rollback()

    @classmethod
    def dedupe_shared_id_col(cls, col_name):
        """Dedupe localities via shared external identifier.
        """
        dup_col = getattr(Locality, col_name)

        # Select ids with 2+ records.
        query = (session
            .query(dup_col)
            .filter(dup_col != None)
            .group_by(dup_col)
            .having(func.count(Locality.wof_id) > 1)
            .all())

        dupes = set()
        for r in tqdm(query):

            # Load rows, sort by completeness.
            rows = Locality.query.filter(dup_col==r[0])
            rows = sorted(rows, key=lambda r: r.completeness, reverse=True)

            # Add all but most complete to dupes.
            for row in rows[1:]:
                cls.set_dupe(row.wof_id)

    @classmethod
    def dedupe_shared_id_cols(cls):
        """Dedupe all external identifiers.
        """
        for col in LOCALITY_DUP_COLS:
            logger.info('Deduping on `%s`' % col)
            cls.dedupe_shared_id_col(col)
