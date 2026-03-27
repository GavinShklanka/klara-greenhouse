/* ============================================================
   KLARA GREENHOUSE — Frontend Controller
   Updated for 9-step intake + archetype-based recommendation
   ============================================================ */

// ── State ────────────────────────────────────────────────────
const state = {
    currentStep: 1,
    totalSteps: 9,
    sessionId: null,
    plan: null,
    pendingAction: null,
    intake: {
        location: null,
        goal: null,
        budget: null,
        property_type: null,
        greenhouse_type: null,
        wind_exposure: null,
        has_south_wall: null,
        experience_level: null,
        solar_existing: null,
    },
};

// ── Region Data ─────────────────────────────────────────────
const REGION_DATA = {
    halifax: { name: 'Halifax / HRM', sunlight: 'High', wind: 'Moderate (coastal)', winter: 'Moderate — coastal buffering', fit: 'Excellent for all greenhouse types' },
    annapolis_valley: { name: 'Annapolis Valley', sunlight: 'High', wind: 'Low (sheltered)', winter: 'Moderate — sheltered valley', fit: 'Ideal for passive solar — max sun exposure' },
    south_shore: { name: 'South Shore', sunlight: 'Moderate', wind: 'High (coastal exposure)', winter: 'Mild — ocean proximity', fit: 'Steel-frame recommended — wind resilience critical' },
    eastern_shore: { name: 'Eastern Shore', sunlight: 'Moderate', wind: 'Moderate (coastal)', winter: 'Moderate — fog factor', fit: 'Good for polycarbonate with wind bracing' },
    cape_breton: { name: 'Cape Breton', sunlight: 'Lower', wind: 'High', winter: 'Severe — heavy snow, long', fit: 'Insulated design critical — Maritime Standard minimum' },
    central_ns: { name: 'Central NS', sunlight: 'Lower', wind: 'Low (inland)', winter: 'Severe — cold inland temps', fit: 'Insulation priority — double-wall glazing' },
    north_shore: { name: 'North Shore', sunlight: 'Moderate', wind: 'Moderate', winter: 'Moderate-Severe', fit: 'Polycarbonate or passive solar with thermal mass' },
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

// ── Interactive Sun Map ─────────────────────────────────────
function showRegionDetail(regionKey) {
    const data = REGION_DATA[regionKey];
    if (!data) return;
    document.querySelectorAll('.ns-map-region').forEach((r) => r.classList.remove('active-region'));
    const region = document.querySelector('[data-region="' + regionKey + '"]');
    if (region) region.classList.add('active-region');
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
            logEvent('recommendation_shown', { archetype: data.plan.design.id, name: data.plan.design.name });
            renderPlan(data.plan);
        } else { console.error('Plan error:', data.error); }
    } catch (err) { console.error('Plan fetch error:', err); }
}

// ── Render Full Plan (Archetype-based) ──────────────────────
function renderPlan(plan) {
    document.querySelectorAll('.hidden-section').forEach((s) => s.classList.add('revealed'));

    const d = plan.design;
    const c = plan.costs;
    const s = plan.solar;
    const cr = plan.crops;
    const lr = plan.local_resources;
    const sd = s.solar_data;

    // --- Archetype Header ---
    document.getElementById('archetypeName').textContent = d.name || 'Your Greenhouse';
    document.getElementById('archetypeTagline').textContent = d.tagline || '';
    document.getElementById('archetypeWhyThis').textContent = d.why_this || '';

    // --- Specs Grid ---
    document.getElementById('specSize').textContent = d.size_range || '—';
    document.getElementById('specFrame').textContent = d.frame_material || '—';
    document.getElementById('specWind').textContent = d.wind_rating || '—';
    document.getElementById('specSnow').textContent = d.snow_load || '—';
    document.getElementById('specFoundation').textContent = d.foundation_type || '—';
    document.getElementById('specCost').textContent = d.true_installed_cost || c.true_installed_cost_range || '—';

    // --- Cost Reality Block ---
    document.getElementById('costKit').textContent = c.kit_price_range || d.kit_price_only || '—';
    document.getElementById('costInstalled').textContent = c.true_installed_cost_range || d.true_installed_cost || '—';

    // Cost line items
    const lineItemsEl = document.getElementById('costLineItems');
    if (c.line_items && c.line_items.length) {
        lineItemsEl.innerHTML = c.line_items.map(function(item) {
            return '<div class="cost-line-item">' +
                '<div class="cost-line-category">' + item.category + '</div>' +
                '<div class="cost-line-range">' + item.range + '</div>' +
                '<div class="cost-line-note">' + item.note + '</div>' +
                '</div>';
        }).join('');
    }
    document.getElementById('costDisclaimer').textContent = c.estimate_disclaimer || '';

    // --- Disqualification Block ---
    document.getElementById('disqualificationText').textContent = d.why_not_others || '';

    // --- Confidence Indicators ---
    setConfidence('badgeClimate', 'confClimate', d.climate_confidence);
    setConfidence('badgeBudget', 'confBudget', d.budget_confidence);
    setConfidence('badgeSite', 'confSite', d.site_fit_confidence);

    // --- Assumptions ---
    const assumptionsList = document.getElementById('assumptionsList');
    if (d.assumptions && d.assumptions.length) {
        assumptionsList.innerHTML = d.assumptions.map(function(a) { return '<li>' + a + '</li>'; }).join('');
    }

    // --- Materials ---
    const materialsList = document.getElementById('materialsList');
    if (d.materials_list_summary && d.materials_list_summary.length) {
        materialsList.innerHTML = d.materials_list_summary.map(function(m) { return '<li>' + m + '</li>'; }).join('');
    }

    // --- Solar ---
    const viability = sd.viability.charAt(0).toUpperCase() + sd.viability.slice(1);
    document.getElementById('solarSummer').textContent = sd.peak_sun_hours_summer + ' hrs/day';
    document.getElementById('solarWinter').textContent = sd.peak_sun_hours_winter + ' hrs/day';
    document.getElementById('solarViability').textContent = viability;
    document.getElementById('solarOrientation').textContent = 'Orientation: ' + s.orientation.ideal + ', long axis ' + s.orientation.long_axis + '. ' + s.why;
    document.getElementById('solarHeat').textContent = 'Heat retention: ' + s.heat_retention.recommendation + '. ' + s.heat_retention.why;

    // Solar existing note
    const solarNote = document.getElementById('solarExistingNote');
    const se = state.intake.solar_existing;
    if (se === 'rooftop') solarNote.textContent = 'You have rooftop solar — excess generation can power ventilation fans, grow lights, or heated propagation mats.';
    else if (se === 'ground') solarNote.textContent = 'Ground-mounted solar pairs well — consider positioning panels and greenhouse to share south-facing exposure.';
    else if (se === 'not_sure') solarNote.textContent = 'Solar panels are optional — passive greenhouse design captures heat without panels. Add them later.';
    else solarNote.textContent = 'No solar panels needed — passive greenhouse design captures and stores solar heat naturally.';

    // --- Crops ---
    document.getElementById('cropWhy').textContent = cr.why;
    document.getElementById('cropList').innerHTML = cr.crops.map(function(crop) {
        var extra = '';
        if (crop.archetype_fit) extra = '<div style="font-size: 0.8rem; color: rgba(255,214,10,0.5); margin-top: 0.3rem;">' + crop.archetype_fit + '</div>';
        if (crop.experience_note) extra += '<div style="font-size: 0.8rem; color: rgba(244,163,0,0.7); margin-top: 0.2rem;">⚠ ' + crop.experience_note + '</div>';
        return '<div style="padding: 1.25rem 0; border-bottom: 1px solid rgba(255,255,255,0.06);">' +
            '<div style="display: flex; justify-content: space-between; align-items: flex-start;">' +
            '<div><div style="font-size: 1.125rem; font-weight: 500; color: #fff;">' + crop.name + '</div>' +
            '<div style="font-size: 0.85rem; color: rgba(255,255,255,0.5); margin-top: 0.25rem;">' + crop.reason + '</div>' +
            extra + '</div>' +
            '<div style="text-align: right; flex-shrink: 0; margin-left: 2rem;">' +
            '<div style="font-size: 0.8rem; color: #FFD60A; text-transform: uppercase; letter-spacing: 0.1em;">' + crop.season + '</div>' +
            '<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4); margin-top: 0.2rem;">' + crop.difficulty + ' · ' + crop.first_harvest_weeks + ' weeks to first harvest</div></div></div></div>';
    }).join('');

    // --- Local Resources ---
    const localExplainer = document.getElementById('localExplainer');
    localExplainer.textContent = lr.service_routing_explainer || '';

    const localList = document.getElementById('localResourcesList');
    if (lr.resources && lr.resources.length) {
        localList.innerHTML = lr.resources.map(function(r) {
            return '<div class="local-resource-card">' +
                '<div class="local-resource-type">' + r.type + '</div>' +
                '<div class="local-resource-name">' + r.name + '</div>' +
                '<div class="local-resource-what">' + r.what_they_do + '</div>' +
                '<div class="local-resource-who">' + r.who_its_for + '</div>' +
                '<div class="local-resource-disclosure">' + (r.disclosure || '') + '</div>' +
                (r.url && r.url !== '#consultation' ? '<a href="' + r.url + '" target="_blank" class="local-resource-link">Visit →</a>' : '') +
                '</div>';
        }).join('');
    }

    // --- Update action section with archetype name ---
    var actionName1 = document.getElementById('actionArchetypeName1');
    if (actionName1) actionName1.textContent = d.name || 'Greenhouse';

    // Scroll to recommendation
    setTimeout(function() { scrollToSection('screen-recommendation'); }, 600);

    // Show sticky CTA
    setTimeout(function() {
        var sticky = document.getElementById('stickyCTA');
        if (sticky) sticky.classList.add('visible');
    }, 1200);

    // Hide sticky when action section visible
    var actionObs = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            var sticky = document.getElementById('stickyCTA');
            if (sticky) sticky.classList.toggle('visible', !entry.isIntersecting);
        });
    }, { threshold: 0.3 });
    var actionSection = document.getElementById('screen-action');
    if (actionSection) actionObs.observe(actionSection);
}

// ── Confidence Badge Helper ─────────────────────────────────
function setConfidence(badgeId, valueId, level) {
    var badge = document.getElementById(badgeId);
    var value = document.getElementById(valueId);
    if (!badge || !value) return;
    var label = (level || 'medium').charAt(0).toUpperCase() + (level || 'medium').slice(1);
    value.textContent = label;
    badge.className = 'confidence-badge confidence-' + (level || 'medium');
}

// ── Action Handlers ─────────────────────────────────────────
function handleAction(type) {
    state.pendingAction = type;
    logEvent('action_clicked', { action: type });

    if (type === 'checkout') {
        document.getElementById('modalTitle').textContent = 'Get Your Build Plan';
        document.getElementById('modalDesc').textContent = 'Enter your email. Your build plan — structural specs, materials cut list, foundation guide, and crop calendar — will be delivered within 24 hours.';
        document.getElementById('modalNameRow').style.display = 'none';
        document.getElementById('modalPhoneRow').style.display = 'none';
        document.getElementById('modalSubmitLabel').textContent = 'Continue to Payment — $49';
    } else if (type === 'quote') {
        document.getElementById('modalTitle').textContent = 'Request a Builder Quote';
        document.getElementById('modalDesc').textContent = 'We\'ll send your archetype specs and True Installed Cost to matched NS builders. They contact you — not the other way around.';
        document.getElementById('modalNameRow').style.display = 'block';
        document.getElementById('modalPhoneRow').style.display = 'block';
        document.getElementById('modalSubmitLabel').textContent = 'Submit Quote Request';
    } else if (type === 'consultation') {
        document.getElementById('modalTitle').textContent = 'Book a Consultation';
        document.getElementById('modalDesc').textContent = '45-minute video consultation for complex yards, unusual zoning, or specific crop goals beyond the standard intake.';
        document.getElementById('modalNameRow').style.display = 'block';
        document.getElementById('modalPhoneRow').style.display = 'block';
        document.getElementById('modalSubmitLabel').textContent = 'Request Consultation — $79';
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
    var email = document.getElementById('modalEmail').value.trim();
    if (!email) { document.getElementById('modalEmail').style.borderColor = '#ff4444'; return; }
    var name = document.getElementById('modalName').value.trim();
    var phone = document.getElementById('modalPhone').value.trim();
    var action = state.pendingAction;

    // Build archetype context
    var archetypeContext = {};
    if (state.plan && state.plan.design) {
        archetypeContext = {
            archetype_id: state.plan.design.id,
            archetype_name: state.plan.design.name,
            true_installed_cost_range: state.plan.design.true_installed_cost,
        };
    }

    var endpoint, body;
    if (action === 'checkout') {
        endpoint = '/api/action/checkout';
        body = { session_id: state.sessionId, email: email, plan_tier: 'full', ...archetypeContext };
    } else if (action === 'quote') {
        endpoint = '/api/action/quote';
        body = { session_id: state.sessionId, name: name, email: email, phone: phone, ...archetypeContext };
    } else {
        endpoint = '/api/action/consultation';
        body = { session_id: state.sessionId, name: name, email: email, phone: phone, ...archetypeContext };
    }

    try {
        var resp = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        var data = await resp.json();
        closeModal();
        logEvent('action_submitted', { action: action, success: data.success });
        if (data.success) {
            if (data.checkout_url) { window.location.href = data.checkout_url; return; }
            showConfirmation(action, data);
        }
    } catch (err) { console.error('Action error:', err); }
}

// ── Structured Confirmations (Prompt 8) ─────────────────────
function showConfirmation(action, data) {
    var archName = (state.plan && state.plan.design) ? state.plan.design.name : 'your greenhouse';
    var refId = data.reference_id || data.session_id || '—';

    var title = '';
    var body = '';

    if (action === 'checkout') {
        title = 'Plan Purchase Confirmed';
        body = '<div class="confirm-card">' +
            '<div class="confirm-ref">Reference: ' + refId + '</div>' +
            '<div class="confirm-archetype">Archetype: ' + archName + '</div>' +
            '<div class="confirm-detail">Your ' + archName + ' Plan includes:</div>' +
            '<ul class="confirm-list">' +
            '<li>Structural specifications matched to your archetype</li>' +
            '<li>Materials cut list formatted for NS suppliers</li>' +
            '<li>Foundation prep guide</li>' +
            '<li>Crop starter plan with planting calendar</li>' +
            '</ul>' +
            '<div class="confirm-next">Your plan will be delivered to your email within 24 hours.</div>' +
            '</div>';
    } else if (action === 'quote') {
        title = 'Quote Request Submitted';
        body = '<div class="confirm-card">' +
            '<div class="confirm-ref">Reference: ' + refId + '</div>' +
            '<div class="confirm-detail">What happens next:</div>' +
            '<ul class="confirm-list">' +
            '<li>We review your specs and route them to builders who work with ' + archName + ' structures in your area.</li>' +
            '<li>Expect contact within 3–5 business days.</li>' +
            '<li>You\'ll enter the conversation knowing your archetype, your True Installed Cost range, and your site requirements. The builder receives the same specs.</li>' +
            '</ul>' +
            '</div>';
    } else {
        title = 'Consultation Request Submitted';
        body = '<div class="confirm-card">' +
            '<div class="confirm-ref">Reference: ' + refId + '</div>' +
            '<div class="confirm-detail">A 45-minute video consultation covers complex yards, unusual zoning, or specific crop goals that go beyond the standard intake.</div>' +
            '<div class="confirm-next" style="margin-top: 1rem;">We\'ll contact you to schedule within 2 business days.</div>' +
            '</div>';
    }

    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmBody').innerHTML = body;
    document.getElementById('screen-confirmation').classList.add('active');
    scrollToSection('screen-confirmation');
}

// ── Feedback ────────────────────────────────────────────────
function submitFeedback(value) {
    logEvent('feedback', { response: value });
    document.querySelectorAll('.feedback-btn').forEach(function(b) { b.classList.remove('selected'); b.style.pointerEvents = 'none'; });
    event.target.classList.add('selected');
    document.getElementById('feedbackThanks').style.display = 'block';
}

// ── Keyboard ────────────────────────────────────────────────
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'Enter' && document.getElementById('contactModal').classList.contains('active')) submitContact();
});

// ── Init ────────────────────────────────────────────────────
window.addEventListener('load', function() {
    document.querySelectorAll('.hero .fade-in').forEach(function(el) { el.classList.add('visible'); });
    logEvent('page_loaded');
    var params = new URLSearchParams(window.location.search);
    if (params.get('checkout') === 'success') {
        showConfirmation('checkout', { reference_id: params.get('ref') || '—' });
    }
});
