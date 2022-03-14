import typing
import datetime
import ipaddress
import fastapi
import pydantic
import shutil
import os
import framework.elasticmodel
import framework.queryparams
import framework.types
import SocialSwag_enum



class UserCreate(framework.elasticmodel.BaseElasticModel):
    phone: str
    email: typing.Optional[str] = pydantic.Field("", **{})
    name: typing.Optional[str] = pydantic.Field("", **{})
    headline: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    dateOfBirth: typing.Optional[datetime.date]
    countryCode: typing.Optional[str] = pydantic.Field("", **{})
    profileCompletedAt: datetime.datetime
    state: typing.Optional[str] = pydantic.Field("", **{})
    kind: SocialSwag_enum.UserKind
    languages: typing.List[str]
    gstin: typing.Optional[str] = pydantic.Field("", **{})
    avatar: typing.Optional[str] = pydantic.Field("", **{})
    previewImage: typing.Optional[str] = pydantic.Field("", **{})
    previewImageThumbnail: typing.Optional[str] = pydantic.Field("", **{})
    categoryId: typing.Optional[str] = pydantic.Field("", **{})
    category: typing.Optional[str] = pydantic.Field("", **{})
    contactName: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutEnabled: typing.Optional[bool] = pydantic.Field(False, )
    shoutoutPersonalEnabled: bool
    shoutoutBrandEnabled: bool
    shoutoutForCharityEnabled: bool
    shoutoutForCharityName: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutForCharityURL: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutForCharityLogo: typing.Optional[str] = pydantic.Field("", **{})
    liveChatEnabled: bool

    class Config:
        collection_name = 'socialswag_user'
        db_collection = 'user'
        
        
    
    

class User(framework.elasticmodel.ElasticModel):
    phone: typing.Optional[str]
    email: typing.Optional[str] = pydantic.Field("", **{})
    name: typing.Optional[str] = pydantic.Field("", **{})
    headline: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    dateOfBirth: typing.Optional[datetime.date]
    countryCode: typing.Optional[str] = pydantic.Field("", **{})
    profileCompletedAt: typing.Optional[datetime.datetime]
    state: typing.Optional[str] = pydantic.Field("", **{})
    kind: typing.Optional[SocialSwag_enum.UserKind]
    languages: typing.Optional[typing.List[str]]
    gstin: typing.Optional[str] = pydantic.Field("", **{})
    avatar: typing.Optional[str] = pydantic.Field("", **{})
    previewImage: typing.Optional[str] = pydantic.Field("", **{})
    previewImageThumbnail: typing.Optional[str] = pydantic.Field("", **{})
    categoryId: typing.Optional[str] = pydantic.Field("", **{})
    category: typing.Optional[str] = pydantic.Field("", **{})
    contactName: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutEnabled: typing.Optional[bool] = pydantic.Field(False, )
    shoutoutPersonalEnabled: typing.Optional[bool]
    shoutoutBrandEnabled: typing.Optional[bool]
    shoutoutForCharityEnabled: typing.Optional[bool]
    shoutoutForCharityName: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutForCharityURL: typing.Optional[str] = pydantic.Field("", **{})
    shoutoutForCharityLogo: typing.Optional[str] = pydantic.Field("", **{})
    liveChatEnabled: typing.Optional[bool]
    
    class Config:
        collection_name = 'socialswag_user'
        db_collection = 'user'
        
        
    

    

    


class UserGetResp(pydantic.BaseModel):
    data: typing.List[User]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class UserBulkDelete(pydantic.BaseModel):
    ids: typing.List[str]
class registerUserParams(pydantic.BaseModel):
    email: str
    name: str
    countryCode: str
    state: typing.Optional[str] = pydantic.Field("", **{})
    gstin: typing.Optional[str] = pydantic.Field("", **{})
    
    
class updateUserParams(pydantic.BaseModel):
    email: str
    name: str
    state: typing.Optional[str] = pydantic.Field("", **{})
    gstin: typing.Optional[str] = pydantic.Field("", **{})
    
    
class loginWithPasswordParams(pydantic.BaseModel):
    email: str
    password: str
    
    





class EmployeeCreate(framework.elasticmodel.BaseElasticModel):
    name: str
    employeeId: int
    mobile: int

    class Config:
        collection_name = 'employee'
        db_collection = 'employee'
        
        
    
    

class Employee(framework.elasticmodel.ElasticModel):
    name: typing.Optional[str]
    employeeId: typing.Optional[int]
    mobile: typing.Optional[int]
    
    class Config:
        collection_name = 'employee'
        db_collection = 'employee'
        
        
    

    

    


class EmployeeGetResp(pydantic.BaseModel):
    data: typing.List[Employee]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class EmployeeBulkDelete(pydantic.BaseModel):
    ids: typing.List[str]
class registerEmpParams(pydantic.BaseModel):
    name: str
    employeeId: int
    mobile: int
    
    
class updateEmpParams(pydantic.BaseModel):
    name: typing.Optional[str] = pydantic.Field("", **{})
    employeeId: typing.Optional[int] = pydantic.Field(0, **{})
    mobile: typing.Optional[int] = pydantic.Field(0, **{})
    
    





class CreateUserCreate(framework.elasticmodel.BaseElasticModel):
    name: str
    email: str
    country: str

    class Config:
        collection_name = 'createuser'
        db_collection = 'createuser'
        
        
    
    

class CreateUser(framework.elasticmodel.ElasticModel):
    name: typing.Optional[str]
    email: typing.Optional[str]
    country: typing.Optional[str]
    
    class Config:
        collection_name = 'createuser'
        db_collection = 'createuser'
        
        
    

    

    


class CreateUserGetResp(pydantic.BaseModel):
    data: typing.List[CreateUser]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class CreateUserBulkDelete(pydantic.BaseModel):
    ids: typing.List[str]
class registerUserParams(pydantic.BaseModel):
    name: str
    email: str
    country: str
    
    
class verifyUserParams(pydantic.BaseModel):
    name: str
    email: str
    id: str
    
    





class mobileImageCreate(framework.elasticmodel.BaseElasticModel):
    url: str

    
    





class desktopImageCreate(framework.elasticmodel.BaseElasticModel):
    linkUrl: str

    
    





class ctaButtonIconmobileCreate(framework.elasticmodel.BaseElasticModel):
    url: str

    
    





class ctaButtonIconCreate(framework.elasticmodel.BaseElasticModel):
    url: str

    
    





class IconCreate(framework.elasticmodel.BaseElasticModel):
    url: str

    
    





class summaryItemsCreate(framework.elasticmodel.BaseElasticModel):
    contentType: str
    icon: IconCreate
    text: str
    textMobile: str

    
    





class BlocksCreate(framework.elasticmodel.BaseElasticModel):
    contentType: str
    id: typing.Optional[str] = pydantic.Field("", **{})
    label: typing.Optional[str] = pydantic.Field("", **{})
    cardType: typing.Optional[str] = pydantic.Field("", **{})
    url: typing.Optional[str] = pydantic.Field("", **{})
    altText: typing.Optional[str] = pydantic.Field("", **{})
    desktopimage: typing.Optional[desktopImageCreate]
    mobileimage: typing.Optional[mobileImageCreate]
    ctabuttonicon: typing.Optional[ctaButtonIconCreate]
    ctabuttoniconmobile: typing.Optional[ctaButtonIconmobileCreate]
    ctaButtonLable: typing.Optional[str] = pydantic.Field("", **{})
    description: typing.Optional[str] = pydantic.Field("", **{})
    descriptionMobile: typing.Optional[str] = pydantic.Field("", **{})
    scrollTo: typing.Optional[str] = pydantic.Field("", **{})
    subtitle: str
    summaryitems: typing.Optional[typing.List[summaryItemsCreate]]
    summaryText1: typing.Optional[str] = pydantic.Field("", **{})
    summaryText1Mobile: typing.Optional[str] = pydantic.Field("", **{})
    summaryText2: typing.Optional[str] = pydantic.Field("", **{})
    summaryText2Mobile: typing.Optional[str] = pydantic.Field("", **{})
    summaryText3: typing.Optional[str] = pydantic.Field("", **{})
    summaryText3Mobile: typing.Optional[str] = pydantic.Field("", **{})
    title: str
    video: typing.Optional[str] = pydantic.Field("", **{})

    
    





class PageCreate(framework.elasticmodel.BaseElasticModel):
    identifier: str
    position: int
    blocks: typing.List[BlocksCreate]
    route: str

    
    





class NavItemsCreate(framework.elasticmodel.BaseElasticModel):
    contentType: str
    itemIcon: str
    itemLable: str
    itemLink: str

    
    





class LogoCreate(framework.elasticmodel.BaseElasticModel):
    url: str

    
    





class footerItemsCreate(framework.elasticmodel.BaseElasticModel):
    contentType: str
    text: str
    url: str

    
    





class footerColumnsCreate(framework.elasticmodel.BaseElasticModel):
    contentType: str
    footeritems: typing.List[footerItemsCreate]
    order: typing.List[int]

    
    





class LayoutCreate(framework.elasticmodel.BaseElasticModel):
    identifier: str
    position: int
    footercolums: typing.List[footerColumnsCreate]
    loginModalIdentifier: str
    logo: LogoCreate
    navitems: typing.List[NavItemsCreate]
    title: str

    
    





class ENCreate(framework.elasticmodel.BaseElasticModel):
    layout: LayoutCreate
    page: PageCreate

    class Config:
        collection_name = 'en'
        db_collection = 'en'
        
        
    
    

class EN(framework.elasticmodel.ElasticModel):
    layout: typing.Optional[LayoutCreate]
    page: typing.Optional[PageCreate]
    
    class Config:
        collection_name = 'en'
        db_collection = 'en'
        
        
    

    

    


class ENGetResp(pydantic.BaseModel):
    data: typing.List[EN]
    total: int = pydantic.Field(0)
    count: int = pydantic.Field(0)


class ENBulkDelete(pydantic.BaseModel):
    ids: typing.List[str]
class AuthenticateParams(pydantic.BaseModel):
    layout: LayoutCreate
    page: PageCreate
    
    

