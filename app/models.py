from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class CreamVault(Base):
    __tablename__ = "cream_vaults"
    vault_id = Column(Integer, primary_key=True, index=True)
    user_address = Column(String, index=True)
    asset_symbol = Column(String)
    asset_address = Column(String)
    balance = Column(Numeric, default=0)
    collateral_ratio = Column(Numeric, default=1.5)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    events = relationship("VaultEvent", back_populates="vault")

class VaultEvent(Base):
    __tablename__ = "vault_events"
    event_id = Column(Integer, primary_key=True, index=True)
    vault_id = Column(Integer, ForeignKey("cream_vaults.vault_id"))
    event_type = Column(String)
    amount = Column(Numeric)
    event_ts = Column(TIMESTAMP, default=datetime.utcnow)

    vault = relationship("CreamVault", back_populates="events")
