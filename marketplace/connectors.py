"""Metadata-only preflight. No token handling, SDK, MCP transport or live reads."""
from dataclasses import dataclass
import math
from .core import Denied

@dataclass(frozen=True)
class Grant:
    org: str
    member: str
    purpose: str
    channels: tuple[str,...]
    expires: float
    admin_reference: str
    revoked: bool=False

def preflight(grant, *, org, member, purpose, channel, visibility, shared, action, now):
    if action!='read': raise Denied('External writes disabled')
    if not math.isfinite(now) or not math.isfinite(grant.expires) or now>=grant.expires or grant.revoked: raise Denied('Inactive consent')
    if (org,member,purpose)!=(grant.org,grant.member,grant.purpose): raise Denied('Consent scope mismatch')
    if not grant.admin_reference.strip(): raise Denied('Administrator authorization required')
    if visibility!='public' or shared is not False or channel not in grant.channels: raise Denied('Channel not allowed')
    return True
