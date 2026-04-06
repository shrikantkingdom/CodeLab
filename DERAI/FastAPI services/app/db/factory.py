"""Factory for selecting database connector by document type."""

from app.db.base import DBConnector
from app.db.snowflake_connector import SnowflakeConnector
from app.db.db2_connector import DB2Connector
from app.models.enums import DocumentType


class DBFactory:
    """Returns the appropriate DBConnector based on document type.

    - Statements → Snowflake
    - Letters & Confirms → DB2
    """

    _connectors: dict[DocumentType, type[DBConnector]] = {
        DocumentType.STATEMENT: SnowflakeConnector,
        DocumentType.LETTER: DB2Connector,
        DocumentType.CONFIRM: DB2Connector,
    }

    @classmethod
    def get_connector(cls, document_type: DocumentType) -> DBConnector:
        connector_cls = cls._connectors.get(document_type)
        if connector_cls is None:
            raise ValueError(f"No DB connector for document type: {document_type}")
        return connector_cls()
