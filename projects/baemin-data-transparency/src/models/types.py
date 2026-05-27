from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class Platform(str, Enum):
    BAEMIN = "baemin"
    COUPANGEATS = "coupangeats"
    YOGIYO = "yogiyo"


class DataCategory(str, Enum):
    SETTLEMENT = "settlement"
    SALES = "sales"
    AD = "ad"
    MENU = "menu"


class ImportMethod(str, Enum):
    UPLOAD = "upload"
    API = "api"
    BROWSER_EXPORT = "browser_export"


class JobStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"


class FeeType(str, Enum):
    MEDIATION_FEE_DELIVERY = "mediation_fee_delivery"
    MEDIATION_FEE_PICKUP = "mediation_fee_pickup"
    MEDIATION_FEE_VAT = "mediation_fee_vat"
    PAYMENT_FEE = "payment_fee"
    PAYMENT_FEE_VAT = "payment_fee_vat"
    DELIVERY_FEE_OWNER = "delivery_fee_owner"
    DELIVERY_FEE_CUSTOMER = "delivery_fee_customer"
    AD_ULTRA_CALL = "ad_ultra_call"
    AD_OPEN_LIST = "ad_open_list"
    AD_SMART = "ad_smart"
    AD_OTHER = "ad_other"
    DISCOUNT_OWNER = "discount_owner"
    DISCOUNT_PLATFORM = "discount_platform"
    COUPON_COST = "coupon_cost"
    POINT_SETTLEMENT = "point_settlement"
    ADJUSTMENT_PLUS = "adjustment_plus"
    ADJUSTMENT_MINUS = "adjustment_minus"
    OTHER_DEDUCTION = "other_deduction"


class OrderStatus(str, Enum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class AuditAction(str, Enum):
    UPLOAD = "upload"
    VIEW_REPORT = "view_report"
    DOWNLOAD = "download"
    DELETE = "delete"
    CONSENT = "consent"
    REVOKE = "revoke"


@dataclass
class FeeItem:
    fee_type: FeeType
    amount: Decimal
    fee_label: Optional[str] = None
    rate: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None


@dataclass
class SettlementRecord:
    settlement_date: date
    period_start: date
    period_end: date
    gross_sales: Decimal
    total_deductions: Decimal
    net_deposit: Decimal
    fee_items: list[FeeItem] = field(default_factory=list)
    platform: Platform = Platform.BAEMIN


@dataclass
class OrderRecord:
    order_date: date
    order_amount: Decimal
    order_status: OrderStatus = OrderStatus.COMPLETED
    order_time: Optional[str] = None
    delivery_fee: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    order_type: Optional[str] = None
    menu_items: list[MenuSaleRecord] = field(default_factory=list)


@dataclass
class AdRecord:
    ad_type: str
    period_start: date
    period_end: date
    spend: Decimal
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    attributed_orders: Optional[int] = None
    attributed_sales: Optional[Decimal] = None


@dataclass
class MenuSaleRecord:
    menu_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


@dataclass
class MenuRecord:
    menu_name: str
    price: Decimal
    category: Optional[str] = None
    cost: Optional[Decimal] = None
    total_sold: Optional[int] = None
    total_revenue: Optional[Decimal] = None


@dataclass
class ParseResult:
    job_id: UUID = field(default_factory=uuid4)
    status: JobStatus = JobStatus.PENDING
    data_category: DataCategory = DataCategory.SETTLEMENT
    records_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    settlements: list[SettlementRecord] = field(default_factory=list)
    orders: list[OrderRecord] = field(default_factory=list)
    ads: list[AdRecord] = field(default_factory=list)
    menus: list[MenuRecord] = field(default_factory=list)


@dataclass
class SettlementReport:
    store_id: UUID
    period_start: date
    period_end: date
    gross_sales: Decimal
    total_deductions: Decimal
    net_deposit: Decimal
    effective_fee_rate: Decimal
    fee_breakdown: dict[str, Decimal] = field(default_factory=dict)
    fee_rate_breakdown: dict[str, Decimal] = field(default_factory=dict)
    month_over_month: Optional[dict] = None
    warnings: list[str] = field(default_factory=list)


@dataclass
class AdReport:
    store_id: UUID
    period_start: date
    period_end: date
    total_spend: Decimal
    total_attributed_orders: int
    total_attributed_sales: Decimal
    roas: Optional[Decimal] = None
    spend_per_order: Optional[Decimal] = None
    spend_ratio: Optional[Decimal] = None
    by_ad_type: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class MenuProfitabilityReport:
    store_id: UUID
    period_start: date
    period_end: date
    menus: list[dict] = field(default_factory=list)
    top_revenue_menus: list[dict] = field(default_factory=list)
    low_margin_menus: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class AuditLogEntry:
    actor_id: UUID
    actor_type: str
    action: AuditAction
    store_id: Optional[UUID] = None
    data_scope: Optional[str] = None
    detail: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
