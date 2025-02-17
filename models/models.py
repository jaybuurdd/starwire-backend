'''
 NOTE: Used script to generate orm mapping of our current database structure.
 Need to check that everything was mapped correctly before distributing models 
 to their own files.
 '''
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import CHAR, Column, Integer, DateTime, Float, ForeignKey,\
      Index, LargeBinary, String, Table, Text, text


Base = declarative_base()
metadata = Base.metadata


class AddressType(Base):
    __tablename__ = 'address_types'

    address_type = Column(String(45), primary_key=True, comment='PHYSICAL, SHIPPING, BILLING')


class Person(Base):
    __tablename__ = 'people'

    id = Column(INTEGER(11), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    nick_name = Column(String(50))
    email = Column(String(50), nullable=False)
    phone = Column(String(20))
    role = Column(String(20))
    pfp = Column(LargeBinary)
    premium_commission = Column(TINYINT(2), nullable=False, server_default=text("0"), comment='0 = no premium, 1 = premium (input affiliate_commisions record)')
    notes = Column(Text)
    site_env = Column(String(100))

    roles = relationship('Role', secondary='people_roles')


class Product(Base):
    __tablename__ = 'products'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(45), nullable=False)
    description = Column(String(45), nullable=False)
    price = Column(String(45), nullable=False, comment='the current retail price')
    qty_limit = Column(Float, nullable=False, server_default=text("0"), comment='the quantity we are authorized to distribute')
    qty_sales = Column(Float, nullable=False, server_default=text("0"), comment='the quantity currently distributed (needs trigger from affiliate_sales)')
    creator = Column(INTEGER(11), nullable=False, comment='the people_id who owns the right to sell this item and receives the profit - fk on people_id')
    source = Column(INTEGER(11), comment='the organization that provides the product, whether physical or digital - fk on organizations')
    expiration_date = Column(DateTime)
    default_commision = Column(Float, nullable=False)
    notes = Column(Text)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(INTEGER(11), primary_key=True)
    role = Column(String(45), nullable=False)
    description = Column(String(255), nullable=False)


class Session(Base):
    __tablename__ = 'sessions'

    sid = Column(String(36), primary_key=True)
    expires = Column(DateTime)
    data = Column(Text)
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)


class TalentCategory(Base):
    __tablename__ = 'talent_categories'

    category = Column(String(45), primary_key=True)


class WalletType(Base):
    __tablename__ = 'wallet_types'

    type = Column(String(45), primary_key=True)


class AffiliateCommision(Base):
    __tablename__ = 'affiliate_commisions'

    people_id = Column(ForeignKey('people.id'), primary_key=True, nullable=False, index=True)
    product_id = Column(ForeignKey('products.id'), primary_key=True, nullable=False, index=True)
    commision = Column(Float, nullable=False, server_default=text("0"), comment='premium commision that only applies to this person for this product - overrides products.default_commision')

    people = relationship('Person')
    product = relationship('Product')


class AffiliateSale(Base):
    __tablename__ = 'affiliate_sales'

    id = Column(INTEGER(11), primary_key=True)
    people_id = Column(ForeignKey('people.id'), nullable=False, index=True)
    product_id = Column(ForeignKey('products.id'), nullable=False, index=True)
    commision = Column(Float, nullable=False, comment='percent commision for that person/product at the time of sale')
    date = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))
    price = Column(Float, nullable=False)

    people = relationship('Person')
    product = relationship('Product')


class Organization(Base):
    __tablename__ = 'organizations'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(45), nullable=False)
    description = Column(String(45), nullable=False)
    phone = Column(String(45))
    email = Column(String(45))
    POC_id = Column(ForeignKey('people.id'), nullable=False, index=True)
    payment_method = Column(Text)
    notes = Column(Text)

    POC = relationship('Person')


t_people_roles = Table(
    'people_roles', metadata,
    Column('people_id', ForeignKey('people.id'), primary_key=True, nullable=False),
    Column('roles_id', ForeignKey('roles.id'), primary_key=True, nullable=False, index=True)
)


class SocialMedia(Base):
    __tablename__ = 'social_media'

    id = Column(INTEGER(11), primary_key=True)
    URL = Column(String(45), nullable=False)
    app_name = Column(String(45), nullable=False)
    user_name = Column(String(45), nullable=False)
    user_handle = Column(String(45))
    followers = Column(INTEGER(11))
    people_id = Column(ForeignKey('people.id'), nullable=False, index=True)

    people = relationship('Person')


class Talent(Base):
    __tablename__ = 'talents'

    id = Column(INTEGER(11), primary_key=True)
    talent = Column(String(45), nullable=False)
    description = Column(String(45), nullable=False)
    talent_category = Column(ForeignKey('talent_categories.category'), nullable=False, index=True)

    talent_category1 = relationship('TalentCategory')


class Wallet(Base):
    __tablename__ = 'wallets'

    wallet = Column(CHAR(42), primary_key=True)
    people_id = Column(ForeignKey('people.id'), index=True)
    type = Column(ForeignKey('wallet_types.type'), index=True)

    people = relationship('Person')
    wallet_type = relationship('WalletType')


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(INTEGER(11), primary_key=True)
    people_id = Column(String(45), nullable=False)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False, index=True)
    address_type = Column(ForeignKey('address_types.address_type'), nullable=False, index=True, comment='types:')
    address1 = Column(String(45), nullable=False)
    address2 = Column(String(45), nullable=False, server_default=text("''"), comment='default: empty string')
    city = Column(String(45), nullable=False)
    state = Column(String(45), nullable=False)
    country = Column(String(45), nullable=False)
    postal_code = Column(String(45), nullable=False)
    notes = Column(String(45))

    address_type1 = relationship('AddressType')
    organization = relationship('Organization')


class OrganizationPerson(Base):
    __tablename__ = 'organization_people'

    people_id = Column(ForeignKey('people.id'), primary_key=True, nullable=False, index=True)
    organization_id = Column(ForeignKey('organizations.id'), primary_key=True, nullable=False, index=True)
    title = Column(String(45), nullable=False, server_default=text("'Member'"))
    notes = Column(Text)

    organization = relationship('Organization')
    people = relationship('Person')


class PeopleTalent(Base):
    __tablename__ = 'people_talents'

    people_id = Column(ForeignKey('people.id'), primary_key=True, nullable=False, index=True)
    talents_id = Column(ForeignKey('talents.id'), primary_key=True, nullable=False, index=True)
    notes = Column(Text)

    people = relationship('Person')
    talents = relationship('Talent')


class Token(Base):
    __tablename__ = 'tokens'
    __table_args__ = (
        Index('idx_unique_wallet-address', 'wallet', 'address', unique=True),
    )

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(45), nullable=False)
    address = Column(CHAR(42), nullable=False)
    symbol = Column(String(45), nullable=False)
    type = Column(String(45), nullable=False)
    blockchain = Column(String(45), nullable=False)
    quantity = Column(Float, nullable=False)
    wallet = Column(ForeignKey('wallets.wallet', ondelete='CASCADE'), nullable=False, index=True)

    wallet1 = relationship('Wallet')


class Ledger(Base):
    __tablename__ = 'ledger'

    people_id = Column(ForeignKey('people.id'), primary_key=True, nullable=False)
    wallet = Column(ForeignKey('wallets.wallet'), primary_key=True, nullable=False, index=True)
    tokens_id = Column(ForeignKey('tokens.id'), primary_key=True, nullable=False, index=True)
    sub_quantity = Column(Float, nullable=False)
    token_ids_list = Column(Text)

    people = relationship('Person')
    tokens = relationship('Token')
    wallet1 = relationship('Wallet')


class TokenId(Base):
    __tablename__ = 'token_ids'
    __table_args__ = (
        Index('idx_unique_tokens-token_ids', 'token_id', 'token_name', unique=True),
    )

    id = Column(INTEGER(11), primary_key=True)
    tokens_id = Column(ForeignKey('tokens.id', ondelete='CASCADE'), nullable=False, index=True)
    token_id = Column(INTEGER(11), nullable=False)
    token_name = Column(String(45), nullable=False)

    tokens = relationship('Token')


class TxHistory(Base):
    __tablename__ = 'tx_history'

    id = Column(INTEGER(11), primary_key=True)
    people_id = Column(ForeignKey('ledger.people_id'), nullable=False, index=True)
    wallet = Column(ForeignKey('ledger.wallet'), nullable=False, index=True)
    tokens_id = Column(ForeignKey('ledger.tokens_id'), nullable=False, index=True)
    token_ids_list_from = Column(Text)
    token_ids_list_to = Column(Text)
    sub_quantity_from = Column(Float, nullable=False)
    sub_quantity_to = Column(Float, nullable=False)
    authorized_by = Column(String(45), nullable=False)
    date = Column(DateTime, nullable=False, server_default=text("current_timestamp()"))

    people = relationship('Ledger', primaryjoin='TxHistory.people_id == Ledger.people_id')
    tokens = relationship('Ledger', primaryjoin='TxHistory.tokens_id == Ledger.tokens_id')
    ledger = relationship('Ledger', primaryjoin='TxHistory.wallet == Ledger.wallet')


class GoatsByWallet(Base):
    __tablename__ = 'GOATS_by_wallet'

    wallet = Column(String, primary_key=True)
    GOAT_ids = Column(String)
    quantity = Column(Integer)