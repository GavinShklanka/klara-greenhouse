"""
Cross-category validation rules for scraped greenhouse components.
Implements rules from Prompt 2 Section 3.3.
"""
from .base import ValidationReport


def validate_structure(product: dict, report: ValidationReport):
    """Validate a greenhouse structure product."""
    pid = product.get("product_id", "unknown")

    price = product.get("price_cad")
    if price is not None:
        if price < 500:
            report.add_warning(pid, "price_cad", f"Suspicious low price: ${price} — likely accessory, not full greenhouse")
        if price > 15000:
            report.add_warning(pid, "price_cad", f"Price ${price} exceeds $15k — likely commercial-grade, may exceed budget")

    snow = product.get("snow_load_psf")
    if snow is None:
        report.add_error(pid, "snow_load_psf",
                         "Snow load not published. Cannot validate against NS/PEI requirements. meets_minimum_spec set to false.")
        product["meets_minimum_spec"] = False
    elif snow < 45:
        report.add_warning(pid, "snow_load_psf",
                           f"Snow load {snow} PSF below minimum 45 PSF for Zone 6a NS.")
        product["meets_minimum_spec"] = False

    wind = product.get("wind_load_kmh") or product.get("wind_load_mph")
    if wind is None:
        report.add_warning(pid, "wind_load", "Wind load not published.")

    frame = product.get("frame_material")
    if frame == "aluminum":
        product["spec_gap_notes"] = (product.get("spec_gap_notes") or "") + \
            " Aluminum frame — verify wind load adequacy for coastal NS."

    if product.get("glazing_type") == "single_wall_polycarb":
        report.add_warning(pid, "glazing_type", "Single-wall glazing — inadequate insulation for NS winters.")

    if product.get("glazing_type") == "polyfilm":
        report.add_warning(pid, "glazing_type", "Polyfilm glazing — short lifespan, poor insulation.")

    if not report.errors or all(e["product_id"] != pid for e in report.errors):
        report.add_valid(pid, "Structure passes validation")


def validate_lighting(product: dict, report: ValidationReport):
    """Validate a LED grow light product."""
    pid = product.get("product_id", "unknown")

    ppf = product.get("ppf_umol_s")
    if ppf is None:
        report.add_warning(pid, "ppf_umol_s", "PAR output not published. Cannot validate adequacy.")

    spectrum = product.get("spectrum")
    if spectrum == "red_blue":
        report.add_warning(pid, "spectrum", "Red/blue (blurple) spectrum — incomplete for full plant growth.")

    wattage = product.get("wattage")
    if wattage and wattage < 50:
        report.add_warning(pid, "wattage", f"Wattage {wattage}W may be too low for supplemental greenhouse lighting.")

    report.add_valid(pid, "Lighting passes validation")


def validate_renewable(product: dict, report: ValidationReport):
    """Validate a solar/battery/charge controller/inverter product."""
    pid = product.get("product_id", "unknown")

    comp_type = product.get("component_type")

    if comp_type == "battery":
        chemistry = product.get("battery_chemistry")
        if chemistry and chemistry != "lifepo4":
            report.add_warning(pid, "battery_chemistry",
                               f"Chemistry '{chemistry}' — LiFePO4 recommended for cold climate safety and cycle life.")

        self_heating = product.get("self_heating_bms")
        if self_heating is False or self_heating is None:
            product["spec_gap_notes"] = (product.get("spec_gap_notes") or "") + \
                " No self-heating BMS — requires insulated enclosure in greenhouse."

    if comp_type == "charge_controller":
        cc_type = product.get("charge_controller_type")
        if cc_type == "pwm":
            report.add_warning(pid, "charge_controller_type",
                               "PWM controller — MPPT recommended for 15-20% better efficiency in NS winter low-light.")

    if comp_type == "inverter":
        wave = product.get("inverter_wave")
        if wave == "modified_sine":
            report.add_warning(pid, "inverter_wave",
                               "Modified sine wave — pure sine recommended for LED driver compatibility.")

    report.add_valid(pid, "Renewable component passes validation")


def validate_sensor(product: dict, report: ValidationReport):
    """Validate a sensor product."""
    pid = product.get("product_id", "unknown")

    if product.get("connectivity") == "none":
        report.add_warning(pid, "connectivity",
                           "No connectivity — cannot support future Klara Care integration.")

    report.add_valid(pid, "Sensor passes validation")


def validate_hydroponic(product: dict, report: ValidationReport):
    """Validate a hydroponic supply product."""
    pid = product.get("product_id", "unknown")
    report.add_valid(pid, "Hydroponic supply passes validation")


def validate_biological(product: dict, report: ValidationReport):
    """Validate a biological supply product."""
    pid = product.get("product_id", "unknown")
    report.add_valid(pid, "Biological supply passes validation")


VALIDATORS = {
    "structures": validate_structure,
    "lighting": validate_lighting,
    "renewable": validate_renewable,
    "sensors": validate_sensor,
    "hydroponic": validate_hydroponic,
    "biological": validate_biological,
}


def validate_product(product: dict, category: str, report: ValidationReport):
    """Route to the correct category validator."""
    validator = VALIDATORS.get(category, validate_hydroponic)
    validator(product, report)
