"""
lead.py
-------
Defines the Lead model for database representation.
"""

from sqlalchemy import Column, Integer, String, Float
try:
    from sqlalchemy import JSON
    has_json = True
except ImportError:
    from sqlalchemy import Text
    has_json = False

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Lead(Base):
    """
    Skeleton SQLAlchemy model for a lead.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    # Add more fields as needed

    risk_score = Column(Float, nullable=True, comment="Represents the lead’s risk level (0.0 = no risk, 1.0 = max risk)")
    projected_ltv = Column(Float, nullable=True, comment="Predicted lifetime value of the lead in USD")
    relationship_map = Column(
        JSON if 'has_json' in globals() and has_json else Text,
        nullable=True,
        comment="JSON structure: {\"connections\": [\"lead_id1\", ...]}"
    )

    def __repr__(self):
        return (
            f"<Lead(name={self.name}, email={self.email}, "
            f"risk_score={self.risk_score}, projected_ltv={self.projected_ltv})>"
        )
