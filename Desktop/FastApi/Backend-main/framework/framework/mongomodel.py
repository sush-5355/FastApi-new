import typing
import bson
import framework.utilities
import framework.queryparams
import motor.motor_asyncio
from pydantic.fields import Field
import json
import pymongo
import pydantic
from datetime import datetime

class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    # @classmethod
    # def validate(cls, v):
    #     try:
    #         bson.ObjectId(str(v))
    #     except bson.errors.InvalidId:
    #         raise ValueError("Not a valid ObjectId")
    #     return str(v)
    @classmethod
    def validate(cls, v):
        if not bson.ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return bson.ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# There should be only one MongoClient instance per cluster per application instance 
# for connection pooling.
# For now to start with there will be only one mongo cluster that will be used, so this
# should be fine. When scaling if there are multiple clusters then we need to have a
# cache lookup based on say partnerId or something and a default one for generic data
# like Country,etc. Don't think twice when the time comes for change!!!
@framework.utilities.run_once
def get_mongo_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    if hasattr(framework.settings, 'db_urls') and framework.settings.db_urls.get("mongo"):
        return motor.motor_asyncio.AsyncIOMotorClient(framework.settings.db_urls["mongo"][0])
    return motor.motor_asyncio.AsyncIOMotorClient()

class BaseMongoModel(pydantic.BaseModel):
    # NOTE: Handling of _id was based on https://github.com/tiangolo/fastapi/issues/1515
    

    @classmethod
    def client(cls) -> motor.motor_asyncio.AsyncIOMotorClient:
        return get_mongo_client()

    @classmethod
    def db(cls) -> motor.motor_asyncio.AsyncIOMotorDatabase:
        return cls.client()[cls.database_name()]

    @classmethod
    def collection(cls) -> motor.motor_asyncio.AsyncIOMotorCollection:
        return cls.db()[cls.collection_name()]

    @classmethod
    def collection_name(cls) -> str:
        return cls.__config__.db_collection if cls.__config__.db_collection else cls.__name__.lower()

    @classmethod
    def database_name(cls) -> str:
        return cls.__config__.collection_name if cls.__config__.collection_name else cls.__name__.lower()

    @classmethod
    def from_mongo(cls, data: dict):
        """We must convert _id into "id". """
        if not data:
            return data
        # id = data.pop('_id', None)
        return cls(**dict(data))

    def to_mongo(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        by_alias = kwargs.pop('by_alias', True)
        exclude = kwargs.pop('exclude', set())
        exclude.union({'created', 'updated', 'tenantId'})

        parsed = self.dict(
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            exclude=exclude,
            **kwargs,
        )

        # Mongo uses `_id` as default key. We should stick to that as well.
        # if '_id' not in parsed and 'id' in parsed:
        #     parsed['_id'] = parsed.pop('id')

        return parsed

    async def create(self):
        try:
            data = self.to_mongo(exclude_unset=False, exclude_none=True)
            data['c'] = data['u'] = datetime.utcnow()
            data['tid'] = bson.ObjectId()

            inserted_doc = await self.collection().insert_one(data)
            collection = self.collection().with_options(read_preference=pymongo.ReadPreference.PRIMARY)
            resp = await collection.find_one(inserted_doc.inserted_id)
            return self.from_mongo(resp)
        except pymongo.errors.DuplicateKeyError as e:
            print("Duplicate")

    async def update(self):
        try:
            data = self.to_mongo()
            data['u'] = datetime.utcnow()
            updated_doc = await self.collection().update_one({'_id':bson.ObjectId(self.id)}, {'$set': data})
            collection = self.collection().with_options()
            resp = await collection.find_one(self.id)
            return self.from_mongo(resp)
        except pymongo.errors.DuplicateKeyError as e:
            print("Duplicate")
    
    @classmethod
    async def get(cls, id):
        resp = await cls.collection().find_one(bson.ObjectId(id))
        return cls.from_mongo(resp)

    @classmethod
    async def get_all(cls, params: framework.queryparams.QueryParams):
        mongoquery = {"collation": {"locale": "en"}}
        mongoquery["filter"] = json.loads(params.q)
        if params.fields:
            mongoquery['projection'] = list(set(json.loads(params.fields) + ["tid"]))
        cursor = cls.collection().find(**mongoquery, sort=None)
        resp = {}
        cursor.skip(params.skip)
        cursor.limit(params.limit)
        data = await cursor.to_list(length=None)
        resp["total"] = await cursor.collection.count_documents(**mongoquery)
        resp["current"] = len(data)
        for index, rec in enumerate(data):
            data[index]['tid'] = str(data[index]['tid'])
            data[index]['_id'] = str(data[index]['_id'])
        resp['data'] = data
        return resp

    @classmethod
    async def delete(cls, id):
        resp = await cls.collection().delete_one({'_id': bson.ObjectId(id)})
        return True

    @classmethod
    async def createIndex(cls, fieldSpec, unique=False):
        return await cls.collection().create_index(fieldSpec, background=True, unique=unique)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            bson.ObjectId: str
        }
        collection_name: None

class MongoModel(BaseMongoModel):
    id: typing.Optional[str] = Field(alias='_id')
    created: typing.Optional[datetime] = Field(alias='c')
    updated: typing.Optional[datetime] = Field(alias='u')
    tenantId: typing.Optional[str] = Field(alias='tid')
