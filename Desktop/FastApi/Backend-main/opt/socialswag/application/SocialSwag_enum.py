
import enum



class PricingKind(enum.IntEnum):
    REGULAR = 1
    IN_APP = 2







class LiveCourseStatus(enum.IntEnum):
    DRAFT = 1
    COMING_SOON = 2
    PUBLISHED = 3







class InteractionKind(enum.IntEnum):
    SHOUTOUT_PERSONAL = 1
    SHOUTOUT_BRAND = 2
    LIVE_CHAT = 3







class RecipientKind(enum.IntEnum):
    SELF = 1
    SOMEONE_ELSE = 2







class InteractionStatus(enum.IntEnum):
    UNPAID = 1
    PAID = 2
    WAITING_FOR_APPROVAL = 3
    WAITING_FOR_CELEBRITY = 4
    COMPLETED = 5
    CANCELLED = 6







class QuestionStatus(enum.IntEnum):
    PENDING = 1
    WAITING_FOR_APPROVAL = 2
    WAITING_FOR_ANSWER = 3
    COMPLETED = 4
    CANCELLED = 5







class MasterclassStatus(enum.IntEnum):
    DRAFT = 1
    COMING_SOON = 2
    PUBLISHED = 3







class SubscriptionKind(enum.IntEnum):
    MASTERCLASS = 1
    OTT = 2







class UserKind(enum.IntEnum):
    FAN = 1
    CELEBRITY = 2
    TRAINER = 3
    ENTITY = 4







class OttChannelStatus(enum.IntEnum):
    DISABLED = 1
    COMING_SOON = 2
    ENABLED = 3







class NftStatus(enum.IntEnum):
    DRAFT = 1
    COMING_SOON = 2
    PUBLISHED = 3







class NftMode(enum.IntEnum):
    SALE = 1
    AUCTION = 2







class NftTokenType(enum.IntEnum):
    ERC721 = 1
    ERC1155 = 2







class NftAuctionStatus(enum.IntEnum):
    DRAFT = 1
    ONGOING = 2
    COMPLETED = 3







class ShoutoutKind(enum.IntEnum):
    PERSONAL = 1
    BRAND = 2







class Gateway(enum.IntEnum):
    RAZORPAY = 1
    RAZORPAY_NFT = 2
    GOOGLE = 3
    APPLE = 4







class LeadSource(enum.IntEnum):
    MOBILE = 1
    WEBSITE = 2




