# Base declarative class for all models

import datetime
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.orm_models.crud import CRUD

__all__ = [
    "User",
    "RefreshToken",
    "OAuthIdentity",
    "DeviceGroup",
    "DeviceType",
    "Device",
    "DeviceEvent",
    "SyncLog",
    "Collection",
    "Field",
    "Relation",
    "Revision",
    "Navigation",
    "Taxonomy",
    "Translation",
    "Content",
]

class Base(DeclarativeBase, CRUD):
    """Root base class using SQLAlchemy 2.0 DeclarativeBase.

    All models inherit from this to share metadata and conventions.
    Provides a common 'id' primary key column (UUID) for all tables.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Universal primary key UUID",
    )

# Main User table
class User(Base):
    __tablename__ = "mitre_users"
    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False, index=True,
        comment="Unique email address for login and notifications",
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True, index=True,
        comment="Optional unique username for login",
    )
    hashed_password: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
        comment="Hashed password for username/password login (null for OAuth-only users)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
        comment="Whether the user account is active",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether the user has admin privileges",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now,
        comment="Account creation timestamp",
    )
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="Timestamp of last successful login",
    )
    __table_args__ = (
        Index("idx_mitre_users_email", "email"),
        Index("idx_mitre_users_username", "username"),
    )

# OAuth Identity table for external providers
class OAuthIdentity(Base):
    __tablename__ = "mitre_oauth_identities"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_users.id"), nullable=False, index=True,
        comment="FK to the associated user",
    )
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False,
        comment="OAuth provider (e.g., google, github)",
    )
    provider_user_id: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Unique user ID from the OAuth provider",
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="OAuth access token (if stored)",
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="OAuth refresh token (if stored)",
    )
    token_expiry: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, comment="Expiry timestamp for access token",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now,
        comment="Identity creation timestamp",
    )
    __table_args__ = (
        Index(
            "idx_mitre_oauth_identities_provider_user_id",
            "provider", "provider_user_id",
        ),
    )

# Refresh Token table for JWT authentication
class RefreshToken(Base):
    __tablename__ = "mitre_refresh_tokens"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_users.id"), nullable=False, index=True,
        comment="FK to the associated user",
    )
    token: Mapped[str] = mapped_column(
        Text, nullable=False, unique=True, index=True,
        comment="Refresh token string",
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, comment="Token expiry timestamp",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now,
        comment="Token creation timestamp",
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether the token is revoked",
    )
    __table_args__ = (
        Index("idx_mitre_refresh_tokens_token", "token"),
    )

# Device Management Tables
class DeviceGroup(Base):
    __tablename__ = "mitre_device_groups"
    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Logical group of devices",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Description of the device group",
    )

class DeviceType(Base):
    __tablename__ = "mitre_device_types"
    name: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, comment="Type identifier for devices",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Description of device type capabilities",
    )
    schema: Mapped[Optional[JSON]] = mapped_column(
        JSON, nullable=True, comment="Optional telemetry data schema",
    )

class Device(Base):
    __tablename__ = "mitre_devices"
    name: Mapped[str] = mapped_column(
        String, nullable=False, index=True, comment="Human-readable device name",
    )
    device_type: Mapped[str] = mapped_column(
        String, ForeignKey("mitre_device_types.name"), nullable=False, index=True,
        comment="Type of this device",
    )
    group: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("mitre_device_groups.name"), nullable=True, index=True,
        comment="Group this device belongs to",
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="offline", index=True,
        comment="Current device status: online/offline/error",
    )
    last_seen: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, nullable=True, comment="Last heartbeat timestamp",
    )
    provisioned: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether provisioning is complete",
    )
    credentials: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Provisioning credentials or cert thumbprints",
    )
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Additional device-specific properties",
    )

class DeviceEvent(Base):
    __tablename__ = "mitre_device_events"
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_devices.id"), nullable=False, index=True,
        comment="FK to the device generating the event",
    )
    event_type: Mapped[str] = mapped_column(
        String, nullable=False, comment="Type of event (telemetry, alert, status)",
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, comment="Event data payload",
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now,
        comment="Event generation timestamp",
    )
    processed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
        comment="Whether the event has been processed by workflows",
    )
    __table_args__ = (
        Index("idx_mitre_device_events_device_id", "device_id"),
        Index("idx_mitre_device_events_timestamp", "timestamp"),
    )

class SyncLog(Base):
    __tablename__ = "mitre_sync_logs"
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mitre_devices.id"), nullable=False, index=True,
        comment="FK to the device performing sync",
    )
    collection: Mapped[str] = mapped_column(
        String, nullable=False, comment="Collection being synced",
    )
    last_synced_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now,
        comment="Last successful sync timestamp",
    )
    conflict_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Number of conflicts detected",
    )
    __table_args__ = (
        Index("idx_mitre_sync_logs_device_id_collection", "device_id", "collection"),
    )

# Existing content and system tables with enhancements
class Collection(Base):
    __tablename__ = "mitre_collections"
    collection: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    singleton: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    icon: Mapped[JSON] = mapped_column(JSON, nullable=True)
    note: Mapped[JSON] = mapped_column(JSON, nullable=True)
    translations: Mapped[JSON] = mapped_column(JSON, nullable=True)
    __table_args__ = (Index("idx_mitre_collections_hidden", "hidden"),)

class Field(Base):
    __tablename__ = "mitre_fields"
    collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False, index=True)
    field: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    schema: Mapped[JSON] = mapped_column(JSON, nullable=True)
    interface: Mapped[JSON] = mapped_column(JSON, nullable=True)
    options: Mapped[JSON] = mapped_column(JSON, nullable=True)
    __table_args__ = (Index("idx_mitre_fields_collection_field", "collection", "field"),)

class Relation(Base):
    __tablename__ = "mitre_relations"
    many_collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False, index=True)
    one_collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False, index=True)
    field_many: Mapped[str] = mapped_column(ForeignKey("mitre_fields.field"), nullable=False, index=True)
    field_one: Mapped[str] = mapped_column(ForeignKey("mitre_fields.field"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String, nullable=False)
    junction: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    __table_args__ = (Index("idx_mitre_relations_many_one", "many_collection", "one_collection"),)

class Revision(Base):
    __tablename__ = "mitre_revisions"
    collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False, index=True)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    data: Mapped[JSON] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft", index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("mitre_users.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.now)

class Navigation(Base):
    __tablename__ = "mitre_navigation"
    label: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mitre_navigation.id"), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class Taxonomy(Base):
    __tablename__ = "mitre_taxonomy"
    vocabulary: Mapped[str] = mapped_column(String, nullable=False, index=True)
    term: Mapped[str] = mapped_column(String, nullable=False, index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mitre_taxonomy.id"), nullable=True)

class Translation(Base):
    __tablename__ = "mitre_translations"
    collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    field: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class Content(Base):
    __tablename__ = "mitre_content"
    collection: Mapped[str] = mapped_column(ForeignKey("mitre_collections.collection"), nullable=False, index=True)
    data: Mapped[JSON] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft", index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("mitre_users.id"), nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.datetime.now)
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    is_draft: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    last_modified: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow,
        comment="Timestamp of last content change"
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
        comment="Incrementing version for optimistic locking"
    )
    __table_args__ = (
        Index("idx_mitre_content_collection_status", "collection", "status"),
        Index("idx_mitre_content_created_by", "created_by"),
        Index("idx_content_collection_status_lastmod", "collection", "status", "last_modified"),
    )
