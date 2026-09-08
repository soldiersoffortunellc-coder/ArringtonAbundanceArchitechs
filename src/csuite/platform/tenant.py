"""
Tenant registry: duplicate-account prevention + tenant isolation.

Every client is a tenant. Each tenant gets exactly one GHL location, and
every piece of data a tenant creates (contacts, opportunities, usage,
billing events) must be namespaced under that tenant's id so that no
cross-tenant read/write is possible.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class DuplicateTenantError(Exception):
    pass


class TenantIsolationError(Exception):
    pass


@dataclass
class Tenant:
    tenant_id: str
    client_name: str
    industry: str
    location_id: str | None = None
    data: dict = field(default_factory=dict)  # namespaced storage for this tenant only


class TenantRegistry:
    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._client_name_index: dict[str, str] = {}  # normalized client_name -> tenant_id
        self._location_index: dict[str, str] = {}  # location_id -> tenant_id

    @staticmethod
    def _normalize(client_name: str) -> str:
        return client_name.strip().lower()

    def register(self, tenant_id: str, client_name: str, industry: str) -> Tenant:
        if tenant_id in self._tenants:
            raise DuplicateTenantError(f"Tenant id '{tenant_id}' already exists.")

        normalized = self._normalize(client_name)
        if normalized in self._client_name_index:
            raise DuplicateTenantError(
                f"A tenant already exists for client name '{client_name}' "
                f"(tenant_id={self._client_name_index[normalized]}). "
                "Refusing to create a duplicate account."
            )

        tenant = Tenant(tenant_id=tenant_id, client_name=client_name, industry=industry)
        self._tenants[tenant_id] = tenant
        self._client_name_index[normalized] = tenant_id
        return tenant

    def attach_location(self, tenant_id: str, location_id: str) -> None:
        if location_id in self._location_index:
            raise DuplicateTenantError(
                f"GHL location '{location_id}' is already attached to tenant "
                f"'{self._location_index[location_id]}'. One location per tenant."
            )
        tenant = self.get(tenant_id)
        tenant.location_id = location_id
        self._location_index[location_id] = tenant_id

    def get(self, tenant_id: str) -> Tenant:
        if tenant_id not in self._tenants:
            raise KeyError(f"Unknown tenant_id '{tenant_id}'.")
        return self._tenants[tenant_id]

    # ---- isolation-enforced data access -----------------------------------

    def put_data(self, tenant_id: str, key: str, value) -> None:
        self.get(tenant_id).data[key] = value

    def get_data(self, requesting_tenant_id: str, owner_tenant_id: str, key: str):
        """
        Reads `key` from `owner_tenant_id`'s namespace, but only if the
        requester IS the owner. This is the isolation boundary: nothing in
        the system may read another tenant's namespaced data.
        """
        if requesting_tenant_id != owner_tenant_id:
            raise TenantIsolationError(
                f"Tenant '{requesting_tenant_id}' is not permitted to read data belonging to "
                f"tenant '{owner_tenant_id}'."
            )
        return self.get(owner_tenant_id).data.get(key)

    def all_tenant_ids(self) -> list[str]:
        return list(self._tenants.keys())
