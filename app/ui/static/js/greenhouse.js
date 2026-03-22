/* ============================================================
   KLARA GREENHOUSE — Frontend Controller
   Phase 5: Event logging, interactive sun map, SVG diagrams,
   veracity rendering, 6-step intake, feedback prompt
   ============================================================ */

// ── State ────────────────────────────────────────────────────
const state = {
    currentStep: 1,
    totalSteps: 6,
    sessionId: null,
    plan: null,
    pendingAction: null,
    intake: {
        location: null,
        goal: null,
        budget: null,
        property_type: null,
        greenhouse_type: null,
        solar_existing: null,
    },
};

// ── Region Data (Phase 5E) ──────────────────────────────────
const REGION_DATA = {
    halifax: {
        name: 'Halifax / HRM', sunlight: 'High', wind: 'Moderate (coastal)',
        winter: 'Moderate — coastal buffering', fit: 'Excellent for all greenhouse types'
    },
    annapolis_valley: {
        name: 'Annapolis Valley', sunlight: 'High', wind: 'Low (sheltered)',
        winter: 'Moderate — sheltered valley', fit: 'Ideal for passive solar — max sun exposure'
    },
    south_shore: {
        name: 'South Shore', sunlight: 'Moderate', wind: 'High (coastal exposure)',
        winter: 'Mild — ocean proximity', fit: 'Polycarbonate recommended — wind resilience'
    },
    eastern_shore: {
        name: 'Eastern Shore', sunlight: 'Moderate', wind: 'Moderate (coastal)',
        winter: 'Moderate — fog factor', fit: 'Good for polycarbonate with wind bracing'
    },
    cape_breton: {
        name: 'Cape Breton', sunlight: 'Lower', wind: 'High',
        winter: 'Severe — heavy snow, long', fit: 'Insulated design critical — passive solar preferred'
    },
    central_ns: {
        name: 'Central NS', sunlight: 'Lower', wind: 'Low (inland)',
        winter: 'Severe — cold inland temps', fit: 'Insulation priority — double-wall glazing'
    },
    north_shore: {
        name: 'North Shore', sunlight: 'Moderate', wind: 'Moderate',
        winter: 'Moderate-Severe', fit: 'Polycarbonate or passive solar with thermal mass'
    },
};

// ── SVG Greenhouse Diagrams (Phase 5B) ──────────────────────
const GH_DIAGRAMS = {
    polytunnel: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        <text x="100" y="12" fill="#FFD60A" font-size="8" text-anchor="middle" font-family="Inter">YOUR LAYOUT</text>
        <!-- Hoop structure outline -->
        <rect x="30" y="20" width="140" height="110" rx="50" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" fill="rgba(255,214,10,0.03)"/>
        <!-- Central walkway -->
        <rect x="90" y="25" width="20" height="100" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.15)" stroke-width="0.5"/>
        <!-- Raised beds L -->
        <rect x="40" y="30" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="40" y="80" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <!-- Raised beds R -->
        <rect x="115" y="30" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="115" y="80" width="45" height="40" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <!-- Sun arrow -->
        <line x1="100" y1="145" x2="100" y2="135" stroke="#FFD60A" stroke-width="1.5" marker-end="url(#arrowY)"/>
        <text x="100" y="150" fill="#FFD60A" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH</text>
        <defs><marker id="arrowY" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,6 L3,0 L6,6" fill="#FFD60A"/></marker></defs>
    </svg>`,
    polycarbonate: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        <text x="100" y="12" fill="#FFD60A" font-size="8" text-anchor="middle" font-family="Inter">YOUR LAYOUT</text>
        <!-- Rigid structure outline -->
        <rect x="25" y="20" width="150" height="110" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" fill="rgba(255,214,10,0.03)" rx="3"/>
        <!-- Ridge line -->
        <line x1="100" y1="20" x2="100" y2="130" stroke="rgba(255,255,255,0.1)" stroke-width="0.8" stroke-dasharray="4,3"/>
        <!-- Central walkway -->
        <rect x="90" y="22" width="20" height="106" fill="rgba(255,255,255,0.06)" stroke="rgba(255,255,255,0.12)" stroke-width="0.5"/>
        <!-- 6 beds -->
        <rect x="32" y="28" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="32" y="64" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="32" y="96" width="52" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="28" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="64" width="52" height="30" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="116" y="96" width="52" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <!-- Door -->
        <rect x="92" y="125" width="16" height="7" fill="rgba(255,214,10,0.15)" stroke="#FFD60A" stroke-width="0.8" rx="1"/>
        <!-- Sun -->
        <text x="100" y="150" fill="#FFD60A" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH</text>
    </svg>`,
    passive_solar: `<svg viewBox="0 0 200 150" fill="none" xmlns="http://www.w3.org/2000/svg">
        <text x="100" y="12" fill="#FFD60A" font-size="8" text-anchor="middle" font-family="Inter">YOUR LAYOUT</text>
        <!-- Structure outline -->
        <rect x="25" y="20" width="150" height="110" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" fill="rgba(255,214,10,0.03)" rx="3"/>
        <!-- North wall (insulated - thick) -->
        <rect x="25" y="20" width="150" height="12" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
        <text x="100" y="29" fill="rgba(255,255,255,0.4)" font-size="6" text-anchor="middle" font-family="Inter">INSULATED NORTH WALL</text>
        <!-- Glazing south wall -->
        <rect x="25" y="125" width="150" height="5" fill="rgba(255,214,10,0.2)" stroke="#FFD60A" stroke-width="0.8"/>
        <!-- Thermal mass -->
        <circle cx="40" cy="45" r="6" fill="rgba(244,163,0,0.2)" stroke="rgba(244,163,0,0.4)" stroke-width="0.8"/>
        <circle cx="160" cy="45" r="6" fill="rgba(244,163,0,0.2)" stroke="rgba(244,163,0,0.4)" stroke-width="0.8"/>
        <text x="100" y="47" fill="rgba(244,163,0,0.5)" font-size="5" text-anchor="middle" font-family="Inter">THERMAL MASS</text>
        <!-- Beds -->
        <rect x="35" y="55" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="35" y="90" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="110" y="55" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <rect x="110" y="90" width="55" height="28" fill="rgba(45,106,79,0.15)" stroke="rgba(45,106,79,0.4)" stroke-width="0.8" rx="2"/>
        <!-- Walkway -->
        <rect x="93" y="38" width="14" height="84" fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>
        <!-- Sun -->
        <text x="100" y="150" fill="#FFD60A" font-size="7" text-anchor="middle" font-family="Inter">☀ SOUTH-FACING GLAZING</text>
    </svg>`,
};

// ── Event Logging ───────────────────────────────────────────
function logEvent(event, data = {}) {
    const entry = { event, timestamp: new Date().toISOString(), session_id: state.sessionId, ...data };
    console.log('[KLARA]', event, data);
    try { navigator.sendBeacon('/api/log-event', JSON.stringify(entry)); } catch (e) {}
}

// ── Scroll & Animation ──────────────────────────────────────
function scrollToSection(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

const observer = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('.fade-in').forEach((el) => observer.observe(el));

// ── Progress Bar ────────────────────────────────────────────
function updateProgress(step) {
    document.getElementById('progressBar').style.width = ((step / state.totalSteps) * 100) + '%';
}

// ── Interactive Sun Map (Phase 5E) ──────────────────────────
function showRegionDetail(regionKey) {
    const data = REGION_DATA[regionKey];
    if (!data) return;

    // Highlight active region
    document.querySelectorAll('.ns-map-region').forEach((r) => r.classList.remove('active-region'));
    const region = document.querySelector('[data-region="' + regionKey + '"]');
    if (region) region.classList.add('active-region');

    // Show detail panel
    document.getElementById('regionDetailName').textContent = data.name;
    document.getElementById('regionSunlight').textContent = data.sunlight;
    document.getElementById('regionWind').textContent = data.wind;
    document.getElementById('regionWinter').textContent = data.winter;
    document.getElementById('regionFit').textContent = data.fit;
    document.getElementById('sunMapDetail').classList.add('active');
}

// ── Intake Step Navigation ──────────────────────────────────
document.querySelectorAll('.btn-select').forEach((btn) => {
    btn.addEventListener('click', () => {
        const field = btn.dataset.field;
        const value = btn.dataset.value;
        state.intake[field] = value;
        logEvent('intake_selection', { field, value, step: state.currentStep });

        // Highlight selected location on sun map
        if (field === 'location') {
            const rd = REGION_DATA[value];
            const zoneName = rd ? rd.sunlight + ' Solar Zone' : value;
            document.getElementById('sunMapDetected').innerHTML = 'You\'re in a ' + zoneName + '<div class="sun-map-detected-sub">' + (rd ? rd.fit : '') + '</div>';
            showRegionDetail(value);
        }

        const parent = btn.closest('.intake-options');
        parent.querySelectorAll('.btn-select').forEach((b) => b.classList.remove('selected'));
        btn.classList.add('selected');
        setTimeout(() => advanceIntake(), 350);
    });
});

function advanceIntake() {
    const current = state.currentStep;
    const currentEl = document.getElementById('intake-step-' + current);
    if (currentEl) currentEl.classList.remove('active');

    if (current < state.totalSteps) {
        state.currentStep = current + 1;
        const nextEl = document.getElementById('intake-step-' + state.currentStep);
        if (nextEl) nextEl.classList.add('active');
        updateProgress(state.currentStep);
    } else {
        updateProgress(state.totalSteps);
        submitIntake();
    }
}

// ── API: Submit Intake ──────────────────────────────────────
async function submitIntake() {
    try {
        const resp = await fetch('/api/intake', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state.intake),
        });
        const data = await resp.json();
        if (data.success) {
            state.sessionId = data.session_id;
            logEvent('intake_completed', state.intake);
            showStorySequence();
        } else { console.error('Intake error:', data.error); }
    } catch (err) { console.error('Intake fetch error:', err); }
}

// ── Story Sequence Animation ────────────────────────────────
function showStorySequence() {
    const storySection = document.getElementById('screen-story');
    storySection.classList.add('revealed');
    scrollToSection('screen-story');

    const elements = ['word-sun','conn-1','word-energy','conn-2','word-growth','conn-3','word-food','conn-4','word-indep'];
    elements.forEach((id, i) => {
        setTimeout(() => {
            const el = document.getElementById(id);
            if (el) el.classList.add('visible');
        }, 400 + i * 500);
    });

    setTimeout(() => fetchPlan(), elements.length * 500 + 800);
}

// ── API: Fetch Full Plan ────────────────────────────────────
async function fetchPlan() {
    try {
        const resp = await fetch('/api/plan/' + state.sessionId);
        const data = await resp.json();
        if (data.success) {
            state.plan = data.plan;
            logEvent('recommendation_shown', {
                type: data.plan.design.greenhouse.type_name,
                size: data.plan.design.size.dimensions,
            });
            renderPlan(data.plan);
        } else { console.error('Plan error:', data.error); }
    } catch (err) { console.error('Plan fetch error:', err); }
}

// ── Render Full Plan ────────────────────────────────────────
function renderPlan(plan) {
    document.querySelectorAll('.hidden-section').forEach((s) => s.classList.add('revealed'));

    const d = plan.design;
    const c = plan.costs;
    const s = plan.solar;
    const cr = plan.crops;
    const lr = plan.local_resources;
    const sd = s.solar_data;
    const climate = d.climate_context;

    // --- Recommendation ---
    document.getElementById('recTypeLabel').textContent = d.greenhouse.type_short;
    document.getElementById('recDims').textContent = d.size.dimensions;
    document.getElementById('recTypeName').textContent = d.greenhouse.type_name;
    document.getElementById('recType').textContent = d.greenhouse.type_name;
    document.getElementById('recSize').textContent = d.size.dimensions + ' (' + d.size.sq_ft + ' sq ft)';
    document.getElementById('recMaterials').textContent = d.greenhouse.frame + ' + ' + d.greenhouse.glazing;
    document.getElementById('recCost').textContent = c.recommendation;
    document.getElementById('recTimeline').textContent = c.timeline.diy_weeks + ' weeks (DIY) · ' + c.timeline.contractor_weeks + ' weeks (contractor)';

    // --- SVG Diagram (Phase 5B) ---
    const ghKey = d.greenhouse.type_short.toLowerCase().replace(/[^a-z_]/g, '').replace('hoop_house', 'polytunnel');
    const typeKey = d.greenhouse.type_name.toLowerCase().includes('polytunnel') ? 'polytunnel' :
                    d.greenhouse.type_name.toLowerCase().includes('passive') ? 'passive_solar' : 'polycarbonate';
    document.getElementById('ghDiagram').innerHTML = GH_DIAGRAMS[typeKey] || GH_DIAGRAMS.polycarbonate;

    // --- Solar Badge ---
    const viability = sd.viability.charAt(0).toUpperCase() + sd.viability.slice(1);
    document.getElementById('badgeOrientation').textContent = s.orientation.ideal;
    document.getElementById('badgeViability').textContent = viability;
    const ghType = d.greenhouse.type_name.toLowerCase();
    document.getElementById('badgeSolar').textContent = ghType.includes('passive solar') ? 'Built-In' : 'Optional';

    // --- Solar Detail ---
    document.getElementById('solarSummer').textContent = sd.peak_sun_hours_summer + ' hrs/day';
    document.getElementById('solarWinter').textContent = sd.peak_sun_hours_winter + ' hrs/day';
    document.getElementById('solarViability').textContent = viability;
    document.getElementById('solarOrientation').textContent = 'Orientation: ' + s.orientation.ideal + ', long axis ' + s.orientation.long_axis + '. ' + s.why;
    document.getElementById('solarHeat').textContent = 'Heat retention: ' + s.heat_retention.recommendation + '. ' + s.heat_retention.why;

    // --- Solar Existing Note (Phase 5C) ---
    const solarNote = document.getElementById('solarExistingNote');
    const se = state.intake.solar_existing;
    if (se === 'rooftop') {
        solarNote.textContent = 'You have rooftop solar — excess generation can power ventilation fans, grow lights, or heated propagation mats to extend your season further.';
    } else if (se === 'ground') {
        solarNote.textContent = 'Ground-mounted solar pairs well with a greenhouse setup — consider positioning panels and greenhouse to share south-facing exposure.';
    } else if (se === 'not_sure') {
        solarNote.textContent = 'Solar panels are optional — passive solar greenhouse design captures heat without any panels. Add them later if you want.';
    } else {
        solarNote.textContent = 'No solar panels needed — passive greenhouse design captures and stores solar heat naturally. Panels can be added later as an upgrade.';
    }

    // --- Crops ---
    document.getElementById('cropWhy').textContent = cr.why;
    document.getElementById('cropList').innerHTML = cr.crops.map((crop) =>
        '<div style="padding: 1.25rem 0; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center;">' +
        '<div><div style="font-size: 1.125rem; font-weight: 500; color: #fff;">' + crop.name + '</div>' +
        '<div style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin-top: 0.25rem;">' + crop.note + '</div></div>' +
        '<div style="text-align: right; flex-shrink: 0; margin-left: 2rem;">' +
        '<div style="font-size: 0.8rem; color: #FFD60A; text-transform: uppercase; letter-spacing: 0.1em;">' + crop.harvest_months + '</div>' +
        '<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">' + crop.difficulty + '</div></div></div>'
    ).join('');

    // --- Impact Snapshot ---
    const sqft = d.size.sq_ft || 120;
    document.getElementById('impactProduce').textContent = sqft >= 200 ? '30–50%' : sqft >= 120 ? '20–40%' : '10–25%';
    document.getElementById('impactSavings').textContent = (sqft >= 200 ? '$800–$1,500' : sqft >= 120 ? '$500–$1,200' : '$300–$700') + '/yr';

    // --- Why This Works ---
    document.getElementById('whyList').innerHTML = [
        'Optimized for ' + climate.region + ' — Zone ' + climate.zone + ', ' + climate.growing_season + '-day outdoor season',
        'Snow load rated for ' + climate.snow_load + ' PSF — structure handles NS winters',
        'Foundation depth ' + climate.frost_depth + '" reaches below frost line',
        d.greenhouse.type_name + ' balances cost, durability, and performance for your budget',
        d.size.beds + ' fits your space and growing goals',
        'South-facing orientation maximizes winter solar gain',
    ].map((item) => '<li>' + item + '</li>').join('');

    // --- Veracity Section (Phase 5A) ---
    document.getElementById('vZone').textContent = 'Zone ' + climate.zone + ' (Nova Scotia)';
    document.getElementById('vSeason').textContent = climate.growing_season + ' days (outdoor) · extended with greenhouse';
    document.getElementById('vSunSummer').textContent = sd.peak_sun_hours_summer + ' hrs/day peak';
    document.getElementById('vSunWinter').textContent = sd.peak_sun_hours_winter + ' hrs/day peak';
    document.getElementById('vSnow').textContent = climate.snow_load + ' PSF — frame rated accordingly';
    document.getElementById('vFrost').textContent = climate.frost_depth + '" — foundation depth set to match';
    document.getElementById('vDaylight').textContent = sd.peak_sun_hours_summer + 'h summer → ' + sd.peak_sun_hours_winter + 'h winter';

    // Rule applied
    const budgetLabel = state.intake.budget === 'under_5k' ? 'Budget < $5k' : state.intake.budget === '5k_10k' ? 'Budget $5–10k' : 'Budget $10k+';
    document.getElementById('veracityRuleApplied').textContent = '▸ Your input: ' + budgetLabel + ' → ' + d.greenhouse.type_name;

    // --- Local Resources (Phase 5D — 3 paths) ---
    const buildItems = document.getElementById('localBuildItems');
    const quoteItems = document.getElementById('localQuoteItems');
    const communityItems = document.getElementById('localCommunityItems');

    // Build path: seeds + materials
    let buildHTML = '';
    if (lr.seeds) lr.seeds.forEach((s) => { buildHTML += '<div class="local-path-item">' + s.name + '</div>'; });
    if (lr.materials) lr.materials.forEach((m) => { buildHTML += '<div class="local-path-item">' + m.name + '</div>'; });
    buildItems.innerHTML = buildHTML;

    // Quote path
    quoteItems.innerHTML = '<div class="local-path-item">Local greenhouse builders</div><div class="local-path-item">Custom quotes based on your plan</div>';

    // Community path
    let commHTML = '';
    if (lr.agricultural_support) lr.agricultural_support.forEach((a) => { commHTML += '<div class="local-path-item">' + a.name + '</div>'; });
    commHTML += '<div class="local-path-item">Community gardens</div><div class="local-path-item">Food bank programs</div>';
    communityItems.innerHTML = commHTML;

    // Scroll to recommendation
    setTimeout(() => scrollToSection('screen-recommendation'), 600);

    // Show sticky CTA after plan renders (Phase 6D)
    setTimeout(() => {
        const sticky = document.getElementById('stickyCTA');
        if (sticky) sticky.classList.add('visible');
    }, 1200);

    // Hide sticky CTA when action section is in view
    const actionObs = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            const sticky = document.getElementById('stickyCTA');
            if (sticky) sticky.classList.toggle('visible', !entry.isIntersecting);
        });
    }, { threshold: 0.3 });
    const actionSection = document.getElementById('screen-action');
    if (actionSection) actionObs.observe(actionSection);
}

// ── Action Handlers ─────────────────────────────────────────
function handleAction(type) {
    state.pendingAction = type;
    logEvent('action_clicked', { action: type });

    if (type === 'checkout') {
        document.getElementById('modalTitle').textContent = 'Get Your Starter Plan';
        document.getElementById('modalDesc').textContent = 'Enter your email to receive your starter greenhouse plan — directional guidance, materials list, and crop calendar.';
        document.getElementById('modalNameRow').style.display = 'none';
        document.getElementById('modalPhoneRow').style.display = 'none';
        document.getElementById('modalSubmitLabel').textContent = 'Continue to Payment — $29';
    } else if (type === 'blueprint') {
        document.getElementById('modalTitle').textContent = 'Get Your Tailored Blueprint';
        document.getElementById('modalDesc').textContent = 'Enter your email and we\'ll create a custom greenhouse plan based on your property, sunlight, and build goals.';
        document.getElementById('modalNameRow').style.display = 'block';
        document.getElementById('modalPhoneRow').style.display = 'none';
        document.getElementById('modalSubmitLabel').textContent = 'Continue to Payment — $79';
    } else if (type === 'quote') {
        document.getElementById('modalTitle').textContent = 'Request a Builder Quote';
        document.getElementById('modalDesc').textContent = 'A local NS greenhouse builder will contact you within 48 hours.';
        document.getElementById('modalNameRow').style.display = 'block';
        document.getElementById('modalPhoneRow').style.display = 'block';
        document.getElementById('modalSubmitLabel').textContent = 'Submit Quote Request';
    } else if (type === 'consultation') {
        document.getElementById('modalTitle').textContent = 'Book a Local Consultation';
        document.getElementById('modalDesc').textContent = 'Connect with a greenhouse specialist to discuss your site and next steps.';
        document.getElementById('modalNameRow').style.display = 'block';
        document.getElementById('modalPhoneRow').style.display = 'block';
        document.getElementById('modalSubmitLabel').textContent = 'Request Consultation';
    }
    openModal();
}

function openModal() {
    document.getElementById('contactModal').classList.add('active');
    document.getElementById('modalEmail').value = '';
    document.getElementById('modalName').value = '';
    document.getElementById('modalPhone').value = '';
    document.getElementById('modalEmail').focus();
}

function closeModal() {
    document.getElementById('contactModal').classList.remove('active');
    state.pendingAction = null;
}

async function submitContact() {
    const email = document.getElementById('modalEmail').value.trim();
    if (!email) { document.getElementById('modalEmail').style.borderColor = '#ff4444'; return; }
    const name = document.getElementById('modalName').value.trim();
    const phone = document.getElementById('modalPhone').value.trim();
    const action = state.pendingAction;

    let endpoint, body;
    if (action === 'checkout') { endpoint = '/api/action/checkout'; body = { session_id: state.sessionId, email, plan_tier: 'basic' }; }
    else if (action === 'blueprint') { endpoint = '/api/action/checkout'; body = { session_id: state.sessionId, email, plan_tier: 'premium' }; }
    else if (action === 'quote') { endpoint = '/api/action/quote'; body = { session_id: state.sessionId, name, email, phone }; }
    else { endpoint = '/api/action/consultation'; body = { session_id: state.sessionId, name, email, phone }; }

    try {
        const resp = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const data = await resp.json();
        closeModal();
        logEvent('action_submitted', { action, success: data.success });
        if (data.success) {
            if (data.checkout_url) { window.location.href = data.checkout_url; return; }
            showConfirmation(data);
        }
    } catch (err) { console.error('Action error:', err); }
}

function showConfirmation(data) {
    const titles = { checkout: "Your Plan Is On Its Way", quote: "Quote Request Submitted", consultation: "Consultation Requested" };
    const messages = {
        checkout: "Check your email for your complete greenhouse build plan with materials list, build instructions, and crop calendar.",
        quote: "A local Nova Scotia builder will contact you within 48 hours with a detailed quote based on your plan.",
        consultation: "A greenhouse specialist in your area will reach out to schedule your consultation.",
    };
    document.getElementById('confirmTitle').textContent = titles[data.action] || "You're All Set";
    document.getElementById('confirmMessage').textContent = messages[data.action] || data.message;
    document.getElementById('screen-confirmation').classList.add('active');
    scrollToSection('screen-confirmation');
}

// ── Feedback ────────────────────────────────────────────────
function submitFeedback(value) {
    logEvent('feedback', { response: value });
    document.querySelectorAll('.feedback-btn').forEach((b) => { b.classList.remove('selected'); b.style.pointerEvents = 'none'; });
    event.target.classList.add('selected');
    document.getElementById('feedbackThanks').style.display = 'block';
}

// ── Keyboard ────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'Enter' && document.getElementById('contactModal').classList.contains('active')) submitContact();
});

// ── Init ────────────────────────────────────────────────────
window.addEventListener('load', () => {
    document.querySelectorAll('.hero .fade-in').forEach((el) => el.classList.add('visible'));
    logEvent('page_loaded');
    const params = new URLSearchParams(window.location.search);
    if (params.get('checkout') === 'success') {
        document.getElementById('confirmTitle').textContent = "Payment Confirmed";
        document.getElementById('confirmMessage').textContent = "Your full greenhouse build plan has been sent to your email.";
        document.getElementById('screen-confirmation').classList.add('active');
        scrollToSection('screen-confirmation');
    }
});
