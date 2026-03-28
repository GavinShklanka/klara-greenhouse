"""
Scraper runner — orchestrates all scrapers, produces reports.
Run with: python -m app.scrapers.runner
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Import all scraper classes
from app.scrapers.structures.planta import PlantaScraper
from app.scrapers.lighting.mars_hydro import MarsHydroScraper

META_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "_meta"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "greenhouse_components"

# All registered scrapers
SCRAPERS = [
    PlantaScraper,
    MarsHydroScraper,
]

# Manual collection queue — vendors that cannot be scraped
MANUAL_VENDORS = [
    {
        "vendor_name": "Atlantic Greenhouse Supplies",
        "vendor_url": "https://www.atlanticgreenhouses.ca",
        "category": "structures",
        "contact": "Jackie MacDonald, 902-968-1082, jackie@atlanticgreenhouses.ca",
        "data_needed": "Harnois structure models, pricing, snow/wind specs, delivery to NS/PEI",
        "collection_method": "phone_call",
        "status": "pending",
    },
    {
        "vendor_name": "BC Greenhouse Builders",
        "vendor_url": "https://www.bcgreenhouses.com",
        "category": "structures",
        "contact": "Website contact form",
        "data_needed": "Model specs, pricing range, shipping to NS",
        "collection_method": "email",
        "status": "pending",
    },
    {
        "vendor_name": "Grandio Greenhouses",
        "vendor_url": "https://www.grandiogreenhouses.com",
        "category": "structures",
        "contact": "Website contact form",
        "data_needed": "Snow/wind ratings per model, Canadian pricing",
        "collection_method": "email",
        "status": "pending",
    },
    {
        "vendor_name": "Rimol Greenhouse Systems",
        "vendor_url": "https://www.rimol.com",
        "category": "structures",
        "contact": "Contact form on rimol.com",
        "data_needed": "Nor'Easter residential pricing, Atlantic-specific specs",
        "collection_method": "email",
        "status": "pending",
    },
    {
        "vendor_name": "T&C Hydroponics (Digby)",
        "vendor_url": "https://www.hydrotekhydroponics.com",
        "category": "hydroponic",
        "contact": "Conway Place, 3-305 NS-303, Digby NS B0V 1A0",
        "data_needed": "In-store inventory, Kratky supplies, nutrients, pH kits, pricing",
        "collection_method": "phone_or_visit",
        "status": "pending",
    },
    {
        "vendor_name": "The Grow-Op Shop (Dartmouth)",
        "vendor_url": "https://www.hydrotekhydroponics.com",
        "category": "hydroponic",
        "contact": "10 Akerley Blvd, Unit 58, Dartmouth NS B3B 1J3",
        "data_needed": "In-store inventory, pricing for Kratky supplies, nutrients",
        "collection_method": "phone_or_visit",
        "status": "pending",
    },
    {
        "vendor_name": "Mile High Hydroponics (Sackville)",
        "vendor_url": "https://www.hydrotekhydroponics.com",
        "category": "hydroponic",
        "contact": "225 Cobequid Rd, Unit 3, Lower Sackville NS B4C 3J7",
        "data_needed": "In-store inventory, pricing",
        "collection_method": "phone_or_visit",
        "status": "pending",
    },
    {
        "vendor_name": "SucSeed",
        "vendor_url": "https://www.sucseed.ca",
        "category": "hydroponic",
        "contact": "Website / St. John's NL",
        "data_needed": "Kit pricing, nutrient supplies, component availability",
        "collection_method": "website_review",
        "status": "pending",
    },
    {
        "vendor_name": "Hope Seeds",
        "vendor_url": "https://www.hopeseed.com",
        "category": "biological",
        "contact": "NS-based organic seed company",
        "data_needed": "NS-adapted variety list, pricing, companion species availability",
        "collection_method": "website_review",
        "status": "pending",
    },
    {
        "vendor_name": "Canadian Solar (via dealers)",
        "vendor_url": "https://www.canadiansolar.com",
        "category": "renewable",
        "contact": "Dealer locator on website",
        "data_needed": "NS/PEI dealer identification, panel pricing, residential availability",
        "collection_method": "dealer_lookup",
        "status": "pending",
    },
    {
        "vendor_name": "Greenhouse Nova Scotia",
        "vendor_url": "https://www.greenhousenovascotia.com",
        "category": "support",
        "contact": "Member directory",
        "data_needed": "Installer referrals, builder contacts by region",
        "collection_method": "directory_review",
        "status": "pending",
    },
]


def ensure_directories():
    """Create data directory structure."""
    for category in ["structures", "hydroponic", "lighting", "sensors", "renewable", "biological"]:
        (DATA_DIR / category).mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)
    (META_DIR / "manual_templates").mkdir(parents=True, exist_ok=True)


def run_all_scrapers() -> dict:
    """Run all registered scrapers and produce a consolidated report."""
    ensure_directories()

    scrape_log = {
        "run_started_at": datetime.now(timezone.utc).isoformat(),
        "scrapers_registered": len(SCRAPERS),
        "results": [],
        "total_products": 0,
        "total_valid": 0,
        "total_warnings": 0,
        "total_errors": 0,
    }

    for scraper_cls in SCRAPERS:
        scraper = scraper_cls()
        logger.info(f"Running scraper: {scraper.vendor_name} ({scraper.category})")

        result = scraper.run()
        scrape_log["results"].append(result)
        scrape_log["total_products"] += result.get("products_found", 0)
        scrape_log["total_valid"] += result.get("products_valid", 0)
        scrape_log["total_warnings"] += result.get("warnings", 0)
        scrape_log["total_errors"] += result.get("errors", 0)

    scrape_log["run_completed_at"] = datetime.now(timezone.utc).isoformat()

    # Save scrape log
    log_file = META_DIR / "scrape_log.json"
    log_file.write_text(json.dumps(scrape_log, indent=2, default=str), encoding="utf-8")
    logger.info(f"Scrape log saved to {log_file}")

    # Save manual collection queue
    queue_file = META_DIR / "manual_collection_queue.json"
    queue_file.write_text(json.dumps(MANUAL_VENDORS, indent=2), encoding="utf-8")
    logger.info(f"Manual collection queue saved to {queue_file}")

    # Generate manual templates
    _generate_manual_templates()

    return scrape_log


def _generate_manual_templates():
    """Generate empty JSON templates for manual data collection."""
    template_dir = META_DIR / "manual_templates"

    for vendor in MANUAL_VENDORS:
        slug = vendor["vendor_name"].lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")
        template = {
            "product_id": f"{slug}_FILL_MODEL_NAME",
            "product_name": "FILL: product name",
            "vendor_name": vendor["vendor_name"],
            "vendor_url": vendor["vendor_url"],
            "product_url": "FILL: specific product page URL",
            "price_cad": None,
            "price_source": "unknown",
            "ships_to_ns": None,
            "ships_to_pei": None,
            "delivery_cost_estimate_cad": None,
            "delivery_source": "unknown",
            "klara_system_fit": "standard",
            "meets_minimum_spec": True,
            "spec_gap_notes": None,
            "evidence": {
                "source_url": vendor["vendor_url"],
                "fetch_date": None,
                "extraction_method": "manual",
                "data_confidence": "unknown",
                "verified_by": "FILL: operator name",
                "notes": f"Data collected from {vendor['collection_method']}",
            },
            "spec_completeness_score": 0,
            "last_verified": None,
            "stale": False,
            "_operator_notes": f"Contact: {vendor['contact']}. Data needed: {vendor['data_needed']}",
        }

        # Add category-specific fields
        if vendor["category"] == "structures":
            template.update({
                "dimensions_ft": {"width": None, "length": None, "peak_height": None},
                "area_sqft": None,
                "frame_material": None,
                "frame_gauge": None,
                "glazing_type": None,
                "glazing_thickness_mm": None,
                "snow_load_psf": None,
                "snow_load_source": "unknown",
                "wind_load_kmh": None,
                "wind_load_source": "unknown",
                "warranty_months": None,
                "ventilation_type": None,
                "assembly_complexity": None,
                "foundation_requirements": None,
                "extendable": None,
            })
        elif vendor["category"] == "hydroponic":
            template.update({
                "system_type": None,
                "capacity_plants": None,
                "reservoir_litres": None,
                "pump_required": None,
                "power_draw_watts": None,
                "maintenance_interval_days": None,
                "organic_compatible": None,
            })

        out_file = template_dir / f"{slug}.json"
        out_file.write_text(json.dumps([template], indent=2), encoding="utf-8")

    logger.info(f"Generated {len(MANUAL_VENDORS)} manual collection templates")


def print_report(log: dict):
    """Print human-readable summary."""
    print("\n" + "=" * 60)
    print("KLARA SCRAPE REPORT")
    print("=" * 60)
    print(f"Run: {log['run_started_at']}")
    print(f"Scrapers: {log['scrapers_registered']}")
    print(f"Products found: {log['total_products']}")
    print(f"Products valid: {log['total_valid']}")
    print(f"Warnings: {log['total_warnings']}")
    print(f"Errors: {log['total_errors']}")
    print("-" * 60)

    for r in log["results"]:
        status = "✓" if r.get("products_found", 0) > 0 else "✗"
        manual = " [MANUAL]" if r.get("requires_manual") else ""
        print(f"  {status} {r['vendor']} ({r['category']}){manual}: "
              f"{r.get('products_found', 0)} products, "
              f"{r.get('warnings', 0)} warnings, "
              f"{r.get('errors', 0)} errors")

    print("=" * 60)


if __name__ == "__main__":
    log = run_all_scrapers()
    print_report(log)
