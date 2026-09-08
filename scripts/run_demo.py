#!/usr/bin/env python3
"""
Runs one full operating cycle of the C-Suite AI Agent System against a
realistic (but entirely synthetic) demo dataset, entirely in dry-run mode,
and writes the result to dashboard/dashboard_data.json so the executive
command-center HTML page has something real to render.

Usage:
    python3 scripts/run_demo.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from csuite.orchestrator import RevenueOperatingSystem  # noqa: E402
from csuite.revenue.financial_model import FinancialModel  # noqa: E402


def build_demo_context() -> dict:
    return {
        "target_90_day_value": FinancialModel().scenario("target")["combined_modeled_90_day_value"],
        "cco_high_risk_threshold": 2,
        "cro": {
            "market_opportunity_analyst": {
                "vertical_scores": {
                    "insurance_agency": {
                        "pain_urgency": 9, "financial_impact": 8, "ability_to_pay": 7,
                        "ease_of_reaching_decision_makers": 6, "sales_cycle_length": 6,
                        "repeatability": 8, "ghl_compatibility": 9, "ai_automation_potential": 9,
                        "compliance_complexity": 5, "retention_potential": 8,
                        "expansion_revenue": 7, "referral_potential": 7,
                    },
                    "real_estate": {
                        "pain_urgency": 8, "financial_impact": 7, "ability_to_pay": 7,
                        "ease_of_reaching_decision_makers": 8, "sales_cycle_length": 7,
                        "repeatability": 8, "ghl_compatibility": 9, "ai_automation_potential": 8,
                        "compliance_complexity": 7, "retention_potential": 7,
                        "expansion_revenue": 6, "referral_potential": 8,
                    },
                    "home_services": {
                        "pain_urgency": 9, "financial_impact": 8, "ability_to_pay": 7,
                        "ease_of_reaching_decision_makers": 8, "sales_cycle_length": 8,
                        "repeatability": 9, "ghl_compatibility": 9, "ai_automation_potential": 8,
                        "compliance_complexity": 9, "retention_potential": 7,
                        "expansion_revenue": 6, "referral_potential": 7,
                    },
                    "mortgage": {
                        "pain_urgency": 6, "financial_impact": 6, "ability_to_pay": 6,
                        "ease_of_reaching_decision_makers": 5, "sales_cycle_length": 5,
                        "repeatability": 5, "ghl_compatibility": 7, "ai_automation_potential": 6,
                        "compliance_complexity": 3, "retention_potential": 5,
                        "expansion_revenue": 4, "referral_potential": 5,
                    },
                }
            },
            "productization_director": {
                "implementation_hours_by_industry": {"insurance_agency": 14, "real_estate": 11, "home_services": 9}
            },
            "sales_director": {
                "location_id": "demo_agency_master",
                "new_opportunities": [
                    {"account_name": "Summit Insurance Group", "industry": "insurance_agency", "source": "referral", "value": 30500},
                    {"account_name": "Coastal Realty Partners", "industry": "real_estate", "source": "webinar", "value": 30500},
                    {"account_name": "Ironclad HVAC", "industry": "home_services", "source": "outbound", "value": 5491},
                ],
                "stage_updates": [],
            },
            "client_onboarding_director": {
                "new_clients": [
                    {
                        "tenant_id": "tenant_summit_insurance",
                        "client_name": "Summit Insurance Group",
                        "industry": "insurance_agency",
                        "plan_id": "ai_revenue_operating_system",
                        "client_config": {
                            "branding": {"logo_url": "placeholder"}, "domain": "summitinsurance.example.com",
                            "phone_numbers": ["+15555550100"], "email": "hello@summitinsurance.example.com",
                            "calendars": ["interview_calendar"], "users": ["admin@summitinsurance.example.com"],
                            "services": ["life", "auto", "home"], "service_areas": ["TX"],
                            "pricing": {"setup": 20000, "monthly": 3500}, "disclosures": ["licensing_disclaimer"],
                            "integrations": ["quickbooks"], "escalation_contacts": ["owner@summitinsurance.example.com"],
                        },
                        "users": [{"email": "admin@summitinsurance.example.com", "role": "client_admin"}],
                    },
                    {
                        "tenant_id": "tenant_ironclad_hvac",
                        "client_name": "Ironclad HVAC",
                        "industry": "home_services",
                        "plan_id": "ai_growth_system",
                        "client_config": {
                            "branding": {}, "domain": "",  # intentionally incomplete to demonstrate the BLOCKED path
                            "phone_numbers": [], "email": "", "calendars": [], "users": [],
                            "services": [], "service_areas": [], "pricing": {}, "disclosures": [],
                            "integrations": [], "escalation_contacts": [],
                        },
                        "users": [],
                    },
                ]
            },
            "client_success_retention_director": {
                "client_health": [
                    {"tenant_id": "tenant_summit_insurance", "location_id": "loc_demo_1", "adoption_pct": 0.85,
                     "appointments_last_30d": 22, "engagement_score": 0.9, "failed_automations": 0},
                    {"tenant_id": "tenant_legacy_realty", "location_id": "loc_demo_2", "adoption_pct": 0.12,
                     "appointments_last_30d": 1, "engagement_score": 0.2, "failed_automations": 2,
                     "testimonial_requested": True, "testimonial_permission_granted": False},
                ]
            },
            "revenue_operations_analyst": {
                "funnel": {
                    "leads_generated": 480, "qualified_appointments": 120, "shows": 90,
                    "proposals_sent": 60, "closed_won": 22, "closed_total": 40,
                },
                "scenario": "target",
            },
        },
        "cmo": {
            "location_id": "demo_agency_master",
            "campaigns": [
                {"name": "Insurance Recruiting - LinkedIn Outbound", "channel": "outbound"},
                {"name": "Home Services Database Reactivation", "channel": "database_reactivation"},
            ],
            "leads_by_channel": {"outbound": 180, "referral": 90, "webinar": 60, "database_reactivation": 150},
        },
        "coo": {
            "active_implementations": 7,
            "max_capacity": 10,
            "time_to_launch_days_by_client": [9, 12, 7, 14, 10],
            "qa_results": [
                {"tenant_id": "tenant_summit_insurance", "passed": True},
                {"tenant_id": "tenant_ironclad_hvac", "passed": False},
            ],
        },
        "cfo": {
            "accounts": [
                {
                    "tenant_id": "tenant_summit_insurance", "setup_revenue": 20000, "monthly_revenue": 3500,
                    "software_cost": 250, "ai_usage_cost": 180, "phone_cost": 60, "email_cost": 20, "sms_cost": 40,
                    "integration_cost": 300, "labor_hours": 40, "hourly_labor_rate": 65,
                    "onboarding_cost": 500, "support_cost": 150,
                },
                {
                    "tenant_id": "tenant_thin_margin_client", "setup_revenue": 2500, "monthly_revenue": 997,
                    "software_cost": 300, "ai_usage_cost": 400, "phone_cost": 80, "email_cost": 30, "sms_cost": 60,
                    "integration_cost": 200, "labor_hours": 30, "hourly_labor_rate": 65,
                    "onboarding_cost": 400, "support_cost": 200,
                },
            ],
            "billing_events": [
                {"tenant_id": "tenant_summit_insurance", "event_type": "contract_signed", "amount": 30500},
                {"tenant_id": "tenant_summit_insurance", "event_type": "invoice_sent", "amount": 20000},
                {"tenant_id": "tenant_summit_insurance", "event_type": "payment_collected", "amount": 20000},
                {"tenant_id": "tenant_summit_insurance", "event_type": "payment_collected", "amount": 3500, "is_recurring": True},
            ],
        },
        "cto": {
            "pending_client_configs": [
                {"tenant_id": "tenant_ironclad_hvac", "industry": "home_services", "client_config": {}},
            ],
            "usage_events": [
                {"tenant_id": "tenant_summit_insurance", "tier": "ai_revenue_operating_system", "metric": "ai_conversations", "amount": 4200},
            ],
            "isolation_checks": [
                {"requesting_tenant_id": "tenant_ironclad_hvac", "owner_tenant_id": "tenant_summit_insurance", "key": "notes"},
            ],
        },
    }


def main() -> None:
    ros = RevenueOperatingSystem()
    context = build_demo_context()
    result = ros.run_cycle(context)

    output = {
        "generated_by": "scripts/run_demo.py",
        "mode": "DRY_RUN",
        "agent_roster": ros.agent_roster(),
        "cycle_result": result,
    }

    out_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "dashboard_data.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, default=str)

    print(f"Wrote demo cycle output to {os.path.abspath(out_path)}")
    print(f"Agents wired: {len(output['agent_roster'])}")
    print(f"CEO escalations this cycle: {result['ceo']['kpis'].get('open_executive_escalations')}")


if __name__ == "__main__":
    main()
