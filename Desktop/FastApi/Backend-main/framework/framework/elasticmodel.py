import typing
import os
import uuid
import json
import warnings
import framework.settings
import framework.utilities
import framework.redispool
import framework.queryparams
import elasticsearch
from pydantic.fields import Field
import pydantic
from datetime import datetime, date
from elasticsearch import AsyncElasticsearch
from elasticsearch.connection import create_ssl_context
import ssl
import aioredis
def jsondefault(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()
es_logger = elasticsearch.logger
es_logger.setLevel(elasticsearch.logging.ERROR)

# Ignoring python warnings
warnings.filterwarnings("ignore")
# There should be only one ElasticClient instance per cluster per application instance
# for connection pooling.
# For now to start with there will be only one mongo cluster that will be used, so this
# should be fine. When scaling if there are multiple clusters then we need to have a
# cache lookup based on say partnerId or something and a default one for generic data
# like Country,etc. Don't think twice when the time comes for change!!!

@framework.utilities.run_once
async def get_elasticsearch_client() -> AsyncElasticsearch:
    ssl_context = create_ssl_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    urls = []
    if hasattr(framework.settings, 'db_urls') and framework.settings.db_urls.get("elastic"):
        for url in framework.settings.db_urls["elastic"]:
            urls.append(f"{url.scheme}://{url.host}:{url.port}")
        dburl = framework.settings.db_urls["elastic"][0]
        username = dburl.user
        password = dburl.password
    else:
        urls = ["https://localhost:9200"]
        username = "admin"
        password = "password"
    return AsyncElasticsearch(urls, http_auth=(username, password), verify_certs=False, ssl_context=ssl_context, maxsize=1)

@framework.utilities.run_once
async def get_elasticsearch_sql_client() -> AsyncElasticsearch:
    ssl_context = create_ssl_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    urls = []
    if hasattr(framework.settings, 'db_urls') and framework.settings.db_urls.get("elastic"):
        for url in framework.settings.db_urls["elastic"]:
            urls.append(f"{url.scheme}://{url.host}:{url.port}/_opendistro")
        dburl = framework.settings.db_urls["elastic"][0]
        username = dburl.user
        password = dburl.password
    else:
        urls = ["https://localhost:9200/_opendistro"]
        username = "afmin"
        password = "password"
    return AsyncElasticsearch(urls, http_auth=(username, password), verify_certs=False, ssl_context=ssl_context, maxsize=1)


async def get_redis_client() ->aioredis.Redis:
    dburl = framework.settings.redis_url
    redis = await aioredis.create_redis(f"{dburl.scheme}://{dburl.host}:{dburl.port}")
    return redis


class BaseElasticModel(pydantic.BaseModel):
    # NOTE: Handling of _id was based on https://github.com/tiangolo/fastapi/issues/1515

    @classmethod
    async def client(cls, isSql=False) -> AsyncElasticsearch:
        if isSql:
            return await get_elasticsearch_sql_client()
        return await get_elasticsearch_client()

    @classmethod
    async def collection_name(cls, domain=None) -> str:
        # Converting collection name to session domain index
        if not domain:
            if not framework.ctx.exists() and framework.settings.default_tenant:
                domain = framework.settings.default_tenant
        if not domain:
            domain = framework.ctx["tenant"]
        if cls.__config__.collection_name:
            if cls.__config__.collection_name == framework.settings.product_name:
                domain = f"{framework.settings.product_name}_{domain}"
            else:
                temp = cls.__config__.collection_name.split(framework.settings.product_name)
                domain = f"{framework.settings.product_name}_{domain}_{temp[-1]}"
        else:
            domain = f"{framework.settings.product_name}_{domain}_{cls.__name__.lower()}"
        return domain
        # return cls.__config__.collection_name if cls.__config__.collection_name else cls.__name__.lower()

    @classmethod
    def from_elastic(cls, data: dict):
        """We must convert _id into "id". """
        if not data:
            return data
        return cls(**dict(data))

    @classmethod
    def getTenantId(cls):
        if framework.ctx.exists():
            rpt = framework.context.context.get('rpt', {})
            return rpt.get("tenantId", None)
        return None

    def to_elastic(self, **kwargs):
        exclude_unset = kwargs.pop('exclude_unset', True)
        exclude_defaults = kwargs.pop('exclude_defaults', False)
        by_alias = kwargs.pop('by_alias', True)
        exclude = kwargs.pop('exclude', set())
        # exclude.union({'created', 'updated', 'tenantId'})
        exclude.union({'created', 'updated'})

        parsed = json.loads(self.json(
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            by_alias=by_alias,
            exclude=exclude,
            **kwargs,
        ))
        return parsed

    @classmethod
    def getclassname(cls) -> str:
        return cls.__config__.db_collection if hasattr(cls.__config__, "db_collection") and \
                                                 cls.__config__.db_collection else cls.__name__.lower()

    @classmethod
    def getdefaultquery(cls) -> str:
        if hasattr(cls.__config__, 'def_query') and cls.__config__.def_query:
            try:
                return cls.__config__.def_query
            except:
                pass
        return json.dumps({})

    @classmethod
    def getdefaultquery_condition(cls, isSql=False) -> typing.Any:
        defterms = [{"match": {"_type_.keyword": cls.getclassname()}}]
        if not framework.ctx.exists():
            return defterms
        rpt = framework.context.context.get('rpt', {})
        filterKey = cls.isFilterEnabled().strip().split(",")
        state = [state.strip() for state in rpt.get("state", "").strip().split(",") if state.strip()]
        region = [region.strip() for region in rpt.get("region", "").strip().split(",") if region.strip()]
        filterKeyMap = {"tenantId": "tid", "entityId": "tid", "state": "state", "region": "region"}
        # getting entity of the user
        # tenants = rpt.get(filterKey, '')
        entityid = rpt["entityId"]
        if isSql:
            # f"{key}='{value}'"
            return [f"_type_.keyword='{cls.getclassname()}'", f"_type_.keyword='{cls.getclassname()}create'"] + [f"tid='{entityid}'"] if entityid else []
        for key in filterKey:
            if key not in filterKeyMap:
                continue
            if key == "state" and state:
                if "*" not in state:
                    defterms.append({"terms": {"state.keyword": ["*"] + state}})
            if key == "region" and region:
                if "*" not in region:
                    defterms.append({"terms": {"region.keyword": ["*"] + region}})
            elif key == "tenantId" and rpt.get('tenantId'):
                defterms.append({"terms": {"tid.keyword": rpt.get('tenantId', '').strip().split(",")}})
            elif key == "entityId" and rpt.get('entityId'):
                defterms.append({"match": {"tid.keyword": rpt.get('entityId', '')}})
        return defterms

    @classmethod
    def getClassFields(cls) -> list:
        rename_fields = {"id": "_id", "created": "c", "updated": "u"}
        fields_remove = ["tenantId"]
        return [key for key in list(cls.__dict__['__fields__'].keys()) if key not in rename_fields and key not  in fields_remove] + list(rename_fields.values())

    @classmethod
    def isFilterEnabled(cls) -> str:
        if hasattr(cls.__config__, 'filterkey'):
            return cls.__config__.filterkey
        return "entityId"

    @classmethod
    def accesscheck(self, data):
        if not framework.ctx.exists():
            return True
        filterkey = self.isFilterEnabled()
        rpt = framework.context.context.get('rpt', {})
        entityid = rpt.get('entityId', '')
        includes = rpt.get('includes', '')
        excludes = rpt.get('excludes', '')
        inc = []
        exc = []
        if includes:
            inc = [x.strip() for x in includes.split(',') if x.strip()]
        if excludes:
            exc = [x.strip() for x in excludes.split(',') if x.strip()]

        if (not inc) and (not exc):
            return True
        if not filterkey:
            return True
        elif '_id' in filterkey:
            _id = data['_id']
            if inc and _id not in inc:
                return False
            if exc and _id in exc:
                return False
        # elif "entity_ref.id.keyword" not in filterkey:
        #     companyrefid = data.get(filterkey.replace(".keyword", ""), '')
        #     if companyrefid:
        #         if inc and companyrefid not in inc:
        #             return False
        #         if exc and companyrefid in exc:
        #             return False
        else:
            entity_ref = data.get('entity_ref', {})
            if isinstance(entity_ref, list):
                entityref = []
                for x in entity_ref:
                    if inc and x['id'] in inc:
                        entityref.append(x)
                    if exc and x['id'] not in exc:
                        entityref.append(x)
                if not entityref:
                    print("No ids available data:%s" % data)
                    return False
            elif isinstance(entity_ref, dict):
                entityrefid = entity_ref.get('id', '')
                if entityrefid:
                    if inc and entityrefid not in inc:
                        return False
                    if exc and entityrefid in exc:
                        return False
        return True

    async def create(self, cyberTenant=None):
        try:
            if not cyberTenant and framework.ctx.exists():
                filterkey = self.isFilterEnabled()
                rpt = framework.context.context.get('rpt', {})
                includes = rpt.get('includes', '')
                excludes = rpt.get('excludes', '')
                if filterkey == '_id' and (includes or excludes):
                    return {'_id': "Not allowed"}

            indexName = await self.collection_name(cyberTenant)
            data = self.to_elastic(exclude_unset=False, exclude_none=True)
            data['c'] = data['u'] = datetime.utcnow()
            data['_type_'] = self.getclassname()
            tenantData = self.getTenantId()
            if tenantData:
                data["tid"] = tenantData.strip().split(",")
            #data['tid'] = bson.ObjectId()
            datauuid=str(uuid.uuid4())
            if "_id" in data:
                datauuid = data["_id"]
                del data["_id"]
            client = await self.client()
            inserted_doc = await client.create(indexName, str(datauuid), body=data, refresh=False if cyberTenant else True)
            id = inserted_doc['_id']
            resp = await client.get(index=indexName, id=id)
            inserted_doc = {**resp["_source"], **{"_id": resp['_id']}}
            return inserted_doc
        except elasticsearch.ElasticsearchException as e:
            print(e)

    async def update(self, cyberTenant=None):
        indexName = await self.collection_name(cyberTenant)
        try:
            data = self.to_elastic()
            data['u'] = datetime.utcnow()
            data['_type_'] = self.getclassname()
            id = data['_id']
            del data['_id']
            # tenantData = self.getTenantId()
            # if tenantData:
            #     data["tid"] = tenantData.strip().split(",")
            client = await self.client()
            olddata = await client.get(index=indexName, id=id)
            olddata = {**olddata["_source"], **{"_id": olddata['_id']}}

            if not cyberTenant:
                if not self.accesscheck(olddata):
                    return self.from_elastic({'_id': "Not Allowed"})
            updated_doc = await client.update(index=indexName, id=id, body={"doc": data}, refresh=False if cyberTenant else True)
            resp = await client.get(index=indexName, id=id, request_timeout=90)
            return self.from_elastic({**resp["_source"], **{"_id": resp['_id']}})
        except elasticsearch.ElasticsearchException as e:
            print(e)

    @classmethod
    async def get(cls, id, cyberTenant=None):
        indexName = await cls.collection_name(cyberTenant)
        client = await cls.client()
        olddata = await client.get(index=indexName, id=id)
        olddata = {**olddata["_source"], **{"_id": olddata['_id']}}
        if not cyberTenant:
            if not cls.accesscheck(olddata):
                return cls.from_elastic({'_id': "Not Allowed"})

        # client = await cls.client()
        # resp = await client.get(index=indexName, id=id)
        # return cls.from_elastic({**resp["_source"], **{"_id": resp['_id']}})
        return cls.from_elastic(olddata)

    @classmethod
    async def get_all(cls, params: framework.queryparams.QueryParams, cyberTenant=None):
        indexName = await cls.collection_name(cyberTenant)
        if not params.q:
            params.q = cls.getdefaultquery()
        sqlQuery = ""
        fields = []
        if params.fields:
            if isinstance(params.fields, list):
                fields = params.fields
            elif isinstance(params.fields, str):
                try:
                    fields = json.loads(params.fields)
                except:
                    pass
        try:
            query = json.loads(params.q)
        except:
            query = {}
            if params.q.startswith("SELECT"):
                sqlQuery = params.q
        if sqlQuery:
            cls_fields = cls.getClassFields()
            if len(fields) == 0:
                fields = cls_fields
            defConditions = cls.getdefaultquery_condition(True)
            query_str = " OR ".join(defConditions)
            if "WHERE" in sqlQuery:
                sqlQuery = sqlQuery.replace("WHERE", f"WHERE ({query_str}) AND ")
            else:
                sqlQuery += f"WHERE {query_str}"
            if "FROM datatable" not in sqlQuery:
                return {"count": 0, "total": 0, "data": []}
            fields_query = sqlQuery.split("FROM datatable")[0].replace("SELECT", "").strip().split(",")
            if "*" in fields_query:
                fields_intrested = cls_fields
            else:
                fields_intrested = [field for field in fields_query if field in cls_fields]
                if not fields_intrested:
                    fields_intrested = [field for field in fields if field in cls_fields]
                if not fields_intrested:
                    fields_intrested = cls_fields
            offset = f"LIMIT {params.limit} OFFSET {params.skip * params.limit}"
            sqlQuery = f"SELECT {','.join(fields_intrested)} FROM {indexName} {sqlQuery.split('FROM datatable')[-1]}".strip().strip(";")
            # print(sqlQuery)
            client = await cls.client(isSql=True)
            response = await client.sql.query(body=json.dumps({"query": sqlQuery + " " + offset}), format="json")
            total = response.get('hits', {}).get("total", {}).get('value', 0)
            count = len(response.get('hits', {}).get("hits", []))
            return {"data": [{**record['_source'], **{"_id": record["_id"]}} for record in response.get('hits', {}).get("hits", [])], "total": total, "count": count}
        else:
            query['size'] = params.limit
            query['from'] = params.limit * params.skip
            if not cyberTenant:
                if "query" not in query:
                    query["query"] = {}
                if "bool" not in query["query"]:
                    query["query"]["bool"] = {}
                if "must" not in query["query"]["bool"]:
                    query["query"]["bool"]["must"] = []
                query["query"]["bool"]["must"].extend(cls.getdefaultquery_condition())
            if fields:
                query["_source"] = fields
            if not params.sort:
                params.sort = json.dumps([{"u": {"order": "desc"}}])
            if params.sort:
                order_by = []
                for record in json.loads(params.sort):
                    record_ = {}
                    for key, value in record.items():
                        if value.get('order'):
                            record_[key] = {**value, **{"unmapped_type": "string"}}
                    if record_:
                        order_by.append(record_)
                if order_by:
                    query['sort'] = order_by
                # query['sort'] = params.sort

            query['track_total_hits'] = True
            # if not cyberTenant:
            #     filterkey = cls.isFilterEnabled()
            #     if filterkey:
            #         rpt = framework.context.context.get('rpt', {})
            #         entityid = rpt.get('entityId', '')
            #         # For Global Rules Where companyref.id mustnot exists
            #         should = []
            #         for filter in filterkey:
            #             should.append({"match": {filter: [entityid]}})
            #         if should:
            #             query["query"]["bool"]["should"].extend(should)
            client = await cls.client()
            if query["from"] + query["size"] <= 10000:
                response = await client.search(index=indexName, body=query, request_timeout=90)
                total = response.get('hits', {}).get('total', {}).get('value', 0)
                if response.get('hits', {}).get('total', {}).get('relation', '') == 'gte':
                    q = json.loads(params.q)
                    if "_source" in q:
                        del q['_source']
                    if "size" in q:
                        del q["size"]
                    total_count = await client.count(index=indexName, body=q)
                    if isinstance(total_count, dict) and total_count.get('count', 0) > total:
                        total = total_count['count']
                count = len(response.get('hits', {}).get("hits", []))
            else:
                from_range = query["from"]
                del query["from"]
                st, getFullData = await cls._scrollApi(client, indexName, query, from_range+query["size"])
                getIds = getFullData[from_range:from_range+query["size"]]
                query_new = {"query": {"ids": {"values": getIds}}}
                query_new["size"] = len(getIds)
                response = await client.search(index=indexName, body=query_new, request_timeout=90)
                total = response.get('hits', {}).get('total', {}).get('value', 0)
                q = json.loads(params.q)
                if "_source" in q:
                    del q['_source']
                if "size" in q:
                    del q["size"]
                total_count = await client.count(index=indexName, body=q)
                if isinstance(total_count, dict) and total_count.get('count', 0) > total:
                    total = total_count['count']
                count = len(response.get('hits', {}).get("hits", []))
            return {"data": [{**record['_source'], **{"_id": record["_id"]}} for record in response.get('hits', {}).get("hits", [])], "total": total, "count": count}

    @classmethod
    async def _scrollApi(cls, client, indexName, query, maxSize):
        try:
            query_ = query.copy()
            query_["_source"] = ["_id"]
            query_["size"] = 10000
            res = await client.search(index=indexName, body=query_, scroll='2m')
            sid = res['_scroll_id']
            scroll_size = len(res['hits']['hits'])
            tmpData = []
            for q in res['hits']['hits']:
                tmpData.append(q["_id"])
            while (scroll_size > 0):
                res = await client.scroll(scroll_id=sid, scroll='2m')
                sid = res['_scroll_id']
                scroll_size = len(res['hits']['hits'])
                for p in res['hits']['hits']:
                    tmpData.append(p["_id"])
                if len(tmpData) >= maxSize:
                    break
            return True, tmpData
        except Exception as e:
            print("the exception which fetching the data is ", str(e))
            return False, "the exception which fetching the data is " + str(e)

    @classmethod
    async def delete(cls, id, cyberTenant=None):
        indexName = await cls.collection_name(cyberTenant)
        client = await cls.client()
        olddata = await client.get(index=indexName, id=id)
        olddata = {**olddata["_source"], **{"_id": olddata['_id']}}
        # checking if this id is accessible
        if not cyberTenant:
            if not cls.accesscheck(olddata):
                return False

        if hasattr(cls.__config__, 'changeLogEnabled') and cls.__config__.changeLogEnabled:
            redis_client = await framework.redispool.get_redis_connection()
            if not olddata.get('_type_'):
                olddata['_type_'] = cls.__name__.lower()
            await redis_client.xadd("ChangeStream.BaseElasticModel", {"type": "delete",
                                                                "data": json.dumps({"old": olddata, "new": {}}, default=jsondefault),
                                                                '__class__': olddata["_type_"],
                                                                "domain": framework.ctx["tenant"] if not cyberTenant else cyberTenant})
            # redis_client.close()
        resp = await client.delete(index=indexName, id=id, refresh=False if cyberTenant else True)
        return True

    @classmethod
    async def bulkdelete(cls, ids, cyberTenant=None):
        indexName = await cls.collection_name(cyberTenant)
        client = await cls.client()
        query = {"query": {"terms": {"_id": ids}}}
        await client.delete_by_query(index=indexName, body=query, refresh=False if cyberTenant else True)
        return True

    @classmethod
    async def delete_bulk(cls, condition, cyberTenant=None):
        indexName = await cls.collection_name(cyberTenant)
        query = {"query": {"bool": {"must": [{"match": condition}, {"match": {"_type_.keyword": cls.__name__.lower()}}]}}}
        client = await cls.client()
        await client.delete_by_query(index=indexName, body=query)
        return True


    class Config:
        allow_population_by_field_name = True
        json_encoders = {
        }
        collection_name: None


class ElasticModel(BaseElasticModel):
    id: typing.Optional[str] = Field(alias='_id')
    created: typing.Optional[datetime] = Field(alias='c')
    updated: typing.Optional[datetime] = Field(alias='u')
    tenantId: typing.Optional[typing.List[str]] = Field(alias='tid')
