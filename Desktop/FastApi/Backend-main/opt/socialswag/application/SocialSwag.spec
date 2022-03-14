Model User {
     phone str
     email optional str
     name optional str
     headline optional str
     description optional str
     dateOfBirth optional date
     countryCode optional str
     profileCompletedAt datetime
     state optional str
     kind UserKind
     languages list str
     gstin optional str
     avatar optional str
     previewImage optional str
     previewImageThumbnail optional str
     categoryId optional str
     category optional str
     contactName optional str
     shoutoutEnabled optional bool
     shoutoutPersonalEnabled bool
     shoutoutBrandEnabled bool
     shoutoutForCharityEnabled bool
     shoutoutForCharityName optional str
     shoutoutForCharityURL optional str
     shoutoutForCharityLogo optional str
     liveChatEnabled bool




  
  Action=>registerUser{
    email str
    name str
    countryCode str
    state optional str
    gstin optional str
  }
  Action=>updateUser{
    email str
    name str
    state optional str
    gstin  optional str
  }
  Action=>loginWithPassword{
    email str
    password str
  }
  Config=> {
         collection_name=socialswag_user
         allowedapis="NotAllowed"
     }

}




Enum PricingKind {
  REGULAR=1
  IN_APP
}

Enum LiveCourseStatus {
  DRAFT=1
  COMING_SOON
  PUBLISHED
}

Enum InteractionKind {
  SHOUTOUT_PERSONAL=1
  SHOUTOUT_BRAND
  LIVE_CHAT
}

Enum RecipientKind {
  SELF=1
  SOMEONE_ELSE
}

Enum InteractionStatus {
  UNPAID=1
  PAID
  WAITING_FOR_APPROVAL
  WAITING_FOR_CELEBRITY
  COMPLETED
  CANCELLED
}

Enum QuestionStatus {
  PENDING=1
  WAITING_FOR_APPROVAL
  WAITING_FOR_ANSWER
  COMPLETED
  CANCELLED
}

Enum MasterclassStatus {
  DRAFT=1
  COMING_SOON
  PUBLISHED
}

Enum SubscriptionKind {
  MASTERCLASS=1
  OTT
}

Enum UserKind {
  FAN=1
  CELEBRITY
  TRAINER
  ENTITY
}

Enum OttChannelStatus {
  DISABLED=1
  COMING_SOON
  ENABLED
}

Enum NftStatus {
  DRAFT=1
  COMING_SOON
  PUBLISHED
}

Enum NftMode {
  SALE=1
  AUCTION
}

Enum NftTokenType {
  ERC721=1
  ERC1155
}

Enum NftAuctionStatus {
  DRAFT=1
  ONGOING
  COMPLETED
}

Enum ShoutoutKind {
  PERSONAL=1
  BRAND
}

Enum Gateway {
  RAZORPAY=1
  RAZORPAY_NFT
  GOOGLE
  APPLE
}


Enum LeadSource {
  MOBILE=1
  WEBSITE
}

Model Employee{
  name str
  employeeId int
  mobile int

  Action=>registerEmp{
    name str
    employeeId int
    mobile int
  }

  Action=>updateEmp{
    name optional str
    employeeId optional int
    mobile optional int
  }
  
}
Model CreateUser
  {
    name str
    email str
    country str

    Action=>registerUser{
      name str
      email str
      country str
    }
    Action=>verifyUser{
      name str
      email str
      id str
    }
  }





Model mobileImage internal
{
  url str
}
Model desktopImage internal
{
  linkUrl str
}
Model ctaButtonIconmobile internal
{
  url str
}
Model ctaButtonIcon internal
{
  url str
}
Model Icon internal
{
  url str
}
Model summaryItems internal
{
  contentType str
  icon Icon
  text str
  textMobile str
}
Model Blocks internal
{
  contentType str
  id optional str
  label optional str
  cardType optional str
  url optional str
  altText optional str
  desktopimage optional desktopImage
  mobileimage optional mobileImage
  ctabuttonicon optional ctaButtonIcon
  ctabuttoniconmobile optional ctaButtonIconmobile
  ctaButtonLable optional str
  description optional str
  descriptionMobile optional str
  scrollTo optional str
  subtitle str
  summaryitems list optional summaryItems
  summaryText1 optional str
  summaryText1Mobile optional  str
  summaryText2 optional str
  summaryText2Mobile optional str
  summaryText3 optional str
  summaryText3Mobile optional str
  title str
  video optional str
}
Model Page internal
{
  identifier str
  position int
  blocks list Blocks
  route str
}

Model NavItems internal
{
  contentType str
  itemIcon str
  itemLable str
  itemLink str
}
Model Logo internal
{
  url str
}

Model footerItems internal
{
  contentType str
  text str
  url str
}
Model footerColumns internal
{
  contentType str
  footeritems list footerItems
  order list int
}
Model Layout internal
{
  identifier str
  position int
  footercolums list footerColumns
  loginModalIdentifier str
  logo Logo
  navitems list NavItems
  title str
}

Model EN
{
  layout Layout
  page Page

  Action=>Authenticate
  {
    layout Layout
    page Page
  }
}





