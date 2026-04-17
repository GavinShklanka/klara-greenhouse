/* ============================================================
   KLARA GREENHOUSE — Frontend Controller
   Phase 5: Event logging, interactive sun map, SVG diagrams,
   veracity rendering, 6-step intake, feedback prompt
   ============================================================ */

console.log('[DEBUG] greenhouse.js loaded');

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
        name: 'Cape Breton', sunlight: 'Moderate-High', wind: 'High',
        winter: 'Severe — heavy snow, long', fit: 'Insulated design critical — passive solar preferred'
    },
    central_ns: {
        name: 'Central NS', sunlight: 'Moderate', wind: 'Low (inland)',
        winter: 'Severe — cold inland temps', fit: 'Insulation priority — double-wall glazing'
    },
    north_shore: {
        name: 'North Shore', sunlight: 'Moderate', wind: 'Moderate',
        winter: 'Moderate-Severe', fit: 'Polycarbonate or passive solar with thermal mass'
    },
};

// ── SVG Greenhouse Diagrams (Phase 5B) ──────────────────────
// Sourced from SVGDic.js in index.html

// ── Event Logging & Debug ──────────────────────────────────
function logDebug(message, data = null) {
    const urlParams = new URLSearchParams(window.location.search);
    const debugOutput = document.getElementById('debug-content');
    const debugContainer = document.getElementById('debug-output');
    
    const timestamp = new Date().toLocaleTimeString();
    const logMsg = `[${timestamp}] ${message}`;
    console.log(logMsg, data || '');

    if (urlParams.get('debug') === 'true' && debugContainer && debugOutput) {
        debugContainer.style.display = 'block';
        const entry = document.createElement('div');
        entry.style.marginBottom = '0.5rem';
        entry.style.borderBottom = '1px solid #333';
        entry.style.paddingBottom = '0.5rem';
        entry.innerHTML = `<strong>${logMsg}</strong>${data ? '<pre style="margin-top:0.5rem; color:rgba(27,48,34,0.65)">' + JSON.stringify(data, null, 2) + '</pre>' : ''}`;
        debugOutput.appendChild(entry);
    }
}

function logEvent(event, data = {}) {
    const entry = { event, timestamp: new Date().toISOString(), session_id: state.sessionId, ...data };
    logDebug(`Event: ${event}`, data);
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
        // Prevent double-click if already transitioning
        if (btn.classList.contains('selected') || btn.closest('.intake-step').dataset.locked === 'true') return;

        const field = btn.dataset.field;
        const value = btn.dataset.value;
        state.intake[field] = value;
        logEvent('intake_selection', { field, value, step: state.currentStep });

        // Highlight selected location on sun map
        if (field === 'location') {
            const rd = REGION_DATA[value];
            const zoneName = rd ? rd.sunlight + ' Solar Zone' : value;
            const mapDetected = document.getElementById('sunMapDetected');
            if (mapDetected) {
                mapDetected.innerHTML = 'You\'re in a ' + zoneName + '<div class="sun-map-detected-sub">' + (rd ? rd.fit : '') + '</div>';
            }
            showRegionDetail(value);
        }

        const parent = btn.closest('.intake-options');
        parent.querySelectorAll('.btn-select').forEach((b) => b.classList.remove('selected'));
        btn.classList.add('selected');

        // Save progress to sessionStorage
        sessionStorage.setItem('klara_intake_state', JSON.stringify(state.intake));
        
        setTimeout(() => advanceIntake(), 350);
    });
});

function renderStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > state.totalSteps) {
        logDebug(`renderStep aborted: invalid step ${stepNumber}`);
        return;
    }

    logDebug(`Rendering step ${stepNumber}. Current state step was ${state.currentStep}`);
    state.currentStep = stepNumber;
    
    // Hide all steps, show current
    document.querySelectorAll('.intake-step').forEach(step => {
        step.classList.remove('active');
        step.dataset.locked = 'false';
    });
    
    const targetStep = document.getElementById('intake-step-' + stepNumber);
    if (targetStep) {
        targetStep.classList.add('active');
        
        // Restore visual selections for this step
        const options = targetStep.querySelectorAll('.btn-select');
        options.forEach(btn => {
            const field = btn.dataset.field;
            const value = btn.dataset.value;
            if (state.intake[field] === value) {
                btn.classList.add('selected');
            } else {
                btn.classList.remove('selected');
            }
        });
    } else {
        logDebug(`renderStep error: DOM element #intake-step-${stepNumber} not found.`);
    }

    updateProgress(stepNumber);
    sessionStorage.setItem('klara_current_step', stepNumber);
}

function advanceIntake() {
    if (state.currentStep < state.totalSteps) {
        const nextStep = state.currentStep + 1;
        
        // Prevent duplicate pushState for the same step
        if (window.history.state && window.history.state.step === nextStep) {
            logDebug(`advanceIntake: Prevented duplicate pushState for step ${nextStep}`);
            renderStep(nextStep);
            return;
        }

        const stateObj = { view: 'intake', step: nextStep };
        history.pushState(stateObj, "", "?step=" + nextStep);
        logDebug(`advanceIntake: Pushed history state:`, stateObj);
        renderStep(nextStep);
    } else {
        updateProgress(state.totalSteps);
        submitIntake();
    }
}

function retreatIntake() {
    logDebug(`retreatIntake called from step ${state.currentStep}`);
    if (state.currentStep === 1) {
        scrollToSection('screen-hero');
        return;
    }

    // Try to rely on the browser history if we pushed states properly
    if (window.history.state && window.history.state.view === 'intake' && window.history.state.step > 1) {
        logDebug(`retreatIntake: calling history.back() because valid state exists`, window.history.state);
        history.back();
    } else {
        logDebug(`retreatIntake: NO valid history state found. Falling back to manual render.`);
        const prevStep = state.currentStep - 1;
        const stateObj = { view: 'intake', step: prevStep };
        history.replaceState(stateObj, "", "?step=" + prevStep);
        renderStep(prevStep);
    }
}

// ── API: Submit Intake ──────────────────────────────────────
async function submitIntake() {
    // 1. Lock UI & Prevent Double Submission
    const finalStep = document.getElementById('intake-step-' + state.totalSteps);
    if (finalStep) finalStep.dataset.locked = 'true';
    
    // Disable all select buttons in the final step
    const finalOptions = finalStep ? finalStep.querySelectorAll('.btn-select') : [];
    finalOptions.forEach(btn => btn.style.pointerEvents = 'none');

    logDebug('Submitting intake payload', state.intake);

    try {
        // 2. Validate Full State
        const required = ['location', 'goal', 'budget', 'property_type', 'greenhouse_type', 'solar_existing'];
        const missing = required.filter(f => !state.intake[f]);
        if (missing.length > 0) {
            throw new Error('Missing fields: ' + missing.join(', '));
        }

        // 3. Await POST /api/intake
        const resp = await fetch('/api/intake', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state.intake),
        });
        
        const data = await resp.json();
        logDebug('/api/intake response', data);

        // 4. Verify Valid Session ID
        if (data.success && data.session_id) {
            state.sessionId = data.session_id;
            sessionStorage.setItem('klara_last_session_id', state.sessionId);
            logEvent('intake_completed', state.intake);
            
            // 5. Run Transition/Story Animation
            logDebug('Starting story sequence animation');
            await showStorySequence();
            
            // 6. Redirect to /plan/{session_id}
            sessionStorage.setItem('klara_intake_submitted', 'true');
            const targetUrl = '/plan/' + state.sessionId;
            logDebug(`[DEBUG] Redirect Executed: window.location.href = '${targetUrl}'`);
            window.location.href = targetUrl;
        } else {
            throw new Error(data.error || 'Submission failed');
        }
    } catch (err) {
        logDebug('Intake submission error', err.message);
        showToast(err.message || 'An error occurred during submission', "error");
        
        // Unlock on error
        if (finalStep) finalStep.dataset.locked = 'false';
        finalOptions.forEach(btn => btn.style.pointerEvents = 'auto');
    }
}

// ── Story Sequence Animation ────────────────────────────────
function showStorySequence() {
    return new Promise((resolve) => {
        const storySection = document.getElementById('screen-story');
        if (!storySection) { resolve(); return; }

        storySection.classList.add('revealed');
        scrollToSection('screen-story');

        const elements = ['word-sun','conn-1','word-energy','conn-2','word-growth','conn-3','word-food','conn-4','word-indep'];
        elements.forEach((id, i) => {
            setTimeout(() => {
                const el = document.getElementById(id);
                if (el) el.classList.add('visible');
            }, 200 + i * 300); // Sped up to ensure it finishes within ~3 seconds
        });

        setTimeout(() => {
            resolve();
        }, elements.length * 300 + 800);
    });
}

// ── Reset Intake (allows user to try different scenarios) ───
function resetIntake() {
    logDebug('resetIntake triggered: Hard cleaning intake state.');
    
    // Clear persistence
    sessionStorage.removeItem('klara_intake_state');
    sessionStorage.removeItem('klara_current_step');
    sessionStorage.removeItem('klara_intake_submitted');

    // Reset state
    state.currentStep = 1;
    state.sessionId = null;
    state.plan = null;
    state.intake = {
        location: null,
        goal: null,
        budget: null,
        property_type: null,
        greenhouse_type: null,
        solar_existing: null,
    };

    // Hide story section completely
    const storySection = document.getElementById('screen-story');
    if (storySection) {
        storySection.classList.remove('revealed');
        storySection.classList.remove('visible');
        storySection.querySelectorAll('.visible').forEach(el => el.classList.remove('visible'));
    }

    // Unlock all steps and re-enable pointer events
    document.querySelectorAll('.intake-step').forEach(step => {
        step.dataset.locked = 'false';
        step.classList.remove('active');
        step.querySelectorAll('.btn-select').forEach(btn => {
            btn.style.pointerEvents = 'auto';
            btn.classList.remove('selected');
        });
    });

    // Reset history state and normalize URL (stripping ?restart=1)
    history.replaceState({ view: 'intake', step: 1 }, "", "/");
    renderStep(1);

    // Scroll back to top
    scrollToSection('screen-hero');
}

// ── API: Fetch Full Plan ────────────────────────────────────
async function fetchPlan() {
    if (!state.sessionId) {
        logDebug('No session ID available for plan fetch');
        showToast("Session missing. Redirecting to home...", "error");
        setTimeout(() => window.location.href = "/", 2000);
        return;
    }

    logDebug(`Fetching plan for session: ${state.sessionId}`);
    try {
        const resp = await fetch('/api/plan/' + state.sessionId);
        const data = await resp.json();
        logDebug('Plan API response:', data);

        if (data.success) {
            state.plan = data.plan;
            logEvent('recommendation_shown', {
                type: data.plan.design.greenhouse.type_name,
                size: data.plan.design.size.dimensions,
            });
            renderPlan(data.plan);
        } else {
            console.error('Plan error:', data.error);
            showToast(data.error || "Could not find your plan", "error");
            document.body.innerHTML = `<div style="padding: 4rem; text-align: center;"><h1>Plan Not Found</h1><p>${data.error || 'The requested plan could not be retrieved.'}</p><a href="/" class="btn-primary">Start New Plan</a></div>`;
        }
    } catch (err) {
        logDebug('Plan fetch fetch error:', err);
        showToast("Connection error. Please try again.", "error");
    }
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
        '<div style="padding: 1.25rem 0; border-bottom: 1px solid rgba(27,48,34,0.08); display: flex; justify-content: space-between; align-items: center;">' +
        '<div><div style="font-size: 1.125rem; font-weight: 500; color: #1B3022;">' + crop.name + '</div>' +
        '<div style="font-size: 0.85rem; color: rgba(27,48,34,0.85); margin-top: 0.25rem;">' + crop.note + '</div></div>' +
        '<div style="text-align: right; flex-shrink: 0; margin-left: 2rem;">' +
        '<div style="font-size: 0.8rem; color: #A67C27; text-transform: uppercase; letter-spacing: 0.1em;">' + crop.harvest_months + '</div>' +
        '<div style="font-size: 0.75rem; color: rgba(27,48,34,0.8); margin-top: 0.2rem;">' + crop.difficulty + '</div></div></div>'
    ).join('');

    // --- Impact Snapshot ---
    document.getElementById('impactProduce').textContent = plan.impact.produce;
    document.getElementById('impactSavings').textContent = plan.impact.savings + '/yr';

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

    // --- Debug Trace & Scenario Matrix (Phase 3) ---
    const debugContent = document.getElementById('debug-content');
    if (debugContent) {
        let traceHTML = '<div style="margin-bottom: 2rem;"><strong>Decision Trace:</strong><ul style="margin-top:0.5rem; color:rgba(27,48,34,0.65)">';
        if (plan.design.trace) {
            plan.design.trace.forEach(t => traceHTML += `<li>${t}</li>`);
        }
        traceHTML += '</ul></div>';

        traceHTML += '<strong>Scenario Matrix:</strong><div style="overflow-x:auto; margin-top:0.5rem;"><table style="width:100%; border-collapse:collapse; color:rgba(27,48,34,0.65); font-size:0.75rem;">';
        traceHTML += '<tr style="border-bottom:1px solid rgba(27,48,34,0.1); text-align:left;"><th>Field</th><th>Value</th></tr>';
        
        const intakeData = state.intake;
        for (const [key, val] of Object.entries(intakeData)) {
            traceHTML += `<tr style="border-bottom:1px solid rgba(27,48,34,0.08);"><td>${key}</td><td>${val}</td></tr>`;
        }
        
        traceHTML += `<tr style="border-bottom:1px solid rgba(27,48,34,0.08); color:#A67C27;"><td>Result</td><td>${plan.design.recommendation}</td></tr>`;
        traceHTML += '</table></div>';
        
        debugContent.innerHTML = traceHTML;
    }

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

    const titleEl = document.getElementById('modalTitle');
    const descEl = document.getElementById('modalDesc');
    const btnTextEl = document.getElementById('btnActionText');
    
    // Reset fields
    document.getElementById('groupPhone').style.display = 'none';
    document.getElementById('groupTime').style.display = 'none';
    document.getElementById('groupNotes').style.display = 'none';
    document.getElementById('actionSuccess').style.display = 'none';
    document.getElementById('actionForm').style.display = 'block';

    if (type === 'checkout') {
        titleEl.textContent = 'Get Your Starter Plan';
        descEl.textContent = 'Enter your details to receive your starter greenhouse plan — directional guidance, materials list, and crop calendar.';
        btnTextEl.textContent = 'Submit Request';
    } else if (type === 'blueprint') {
        titleEl.textContent = 'Get Your Tailored Blueprint';
        descEl.textContent = 'We\'ll create a custom greenhouse plan based on your property, sunlight, and build goals.';
        btnTextEl.textContent = 'Submit Request';
    } else if (type === 'quote') {
        titleEl.textContent = 'Request a Builder Quote';
        descEl.textContent = 'A local NS greenhouse builder will contact you within 48 hours.';
        document.getElementById('groupPhone').style.display = 'block';
        btnTextEl.textContent = 'Submit Quote Request';
    } else if (type === 'consultation') {
        titleEl.textContent = 'Book a Local Consultation';
        descEl.textContent = 'Connect with a greenhouse specialist to discuss your site and next steps.';
        document.getElementById('groupPhone').style.display = 'block';
        document.getElementById('groupTime').style.display = 'block';
        btnTextEl.textContent = 'Request Consultation';
    }
    openModal();
}

function openModal() {
    const modal = document.getElementById('actionModal');
    if (!modal) return;
    modal.classList.add('active');
    const emailEl = document.getElementById('actionEmail');
    const nameEl = document.getElementById('actionName');
    const phoneEl = document.getElementById('actionPhone');
    if (emailEl) { emailEl.value = ''; emailEl.focus(); }
    if (nameEl) nameEl.value = '';
    if (phoneEl) phoneEl.value = '';
}

function closeModal() {
    const modal = document.getElementById('actionModal');
    if (modal) modal.classList.remove('active');
    state.pendingAction = null;
}

async function submitAction(event) {
    if (event) event.preventDefault();
    
    const email = document.getElementById('actionEmail').value.trim();
    if (!email) { document.getElementById('actionEmail').style.borderColor = '#ff4444'; return; }
    
    const name = document.getElementById('actionName').value.trim();
    const phone = document.getElementById('actionPhone').value.trim();
    const preferred_time = document.getElementById('actionTime').value;
    const notes = document.getElementById('actionNotes').value.trim();
    const action = state.pendingAction;

    const btnSubmit = document.getElementById('btnActionSubmit');
    const spinner = document.getElementById('actionSpinner');
    if (btnSubmit) btnSubmit.disabled = true;
    if (spinner) spinner.style.display = 'inline-block';

    let endpoint, body;
    if (action === 'checkout') { endpoint = '/api/action/checkout'; body = { session_id: state.sessionId, email, plan_tier: 'basic' }; }
    else if (action === 'blueprint') { endpoint = '/api/action/checkout'; body = { session_id: state.sessionId, email, plan_tier: 'premium' }; }
    else if (action === 'quote') { endpoint = '/api/action/quote'; body = { session_id: state.sessionId, name, email, phone, notes }; }
    else { endpoint = '/api/action/consultation'; body = { session_id: state.sessionId, name, email, phone, preferred_time, notes }; }

    try {
        const resp = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const data = await resp.json();
        
        if (btnSubmit) btnSubmit.disabled = false;
        if (spinner) spinner.style.display = 'none';

        logEvent('action_submitted', { action, success: data.success });
        if (data.success) {
            if (data.checkout_url) { window.location.href = data.checkout_url; return; }
            
            // Show success within modal
            document.getElementById('actionForm').style.display = 'none';
            document.getElementById('actionSuccess').style.display = 'block';
            
            // Also update the confirmation screen for full page view if needed
            showConfirmation(data);
        } else {
            showToast(data.error || "Submission failed", "error");
        }
    } catch (err) { 
        console.error('Action error:', err);
        if (btnSubmit) btnSubmit.disabled = false;
        if (spinner) spinner.style.display = 'none';
        showToast("An unexpected error occurred", "error");
    }
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
    if (e.key === 'Enter' && document.getElementById('actionModal').classList.contains('active')) {
        // Only submit if not already submitting
        if (!document.getElementById('btnActionSubmit').disabled) {
            submitAction();
        }
    }
});

// ── Init & BFCache Protection ───────────────────────────────

function detectReturnFromSubmit(context, isPersisted) {
    if (sessionStorage.getItem('klara_intake_submitted') === 'true') {
        const navEntries = performance.getEntriesByType('navigation');
        const navType = navEntries.length > 0 ? navEntries[0].type : 'unknown';
        logDebug(`Detected return from submitted plan page via [${context}]. Persisted: ${isPersisted}, NavType: ${navType}. Forcing hard restart.`);
        window.location.replace('/?restart=1');
        return true;
    }
    return false;
}

// pageshow catches navigating back via bfcache
window.addEventListener('pageshow', (event) => {
    // Only apply hard restart on the index page
    if (!window.location.pathname.startsWith('/plan/')) {
        detectReturnFromSubmit('pageshow', event.persisted);
    }
});

window.addEventListener('load', () => {
    document.querySelectorAll('.hero .fade-in').forEach((el) => el.classList.add('visible'));
    logEvent('page_loaded');
    
    // Check if we are on the separate plan page
    if (window.location.pathname.startsWith('/plan/')) {
        const parts = window.location.pathname.split('/');
        const idFromUrl = parts[parts.length - 1];
        
        if (idFromUrl && idFromUrl !== 'plan') {
            state.sessionId = idFromUrl;
            console.log('[DEBUG] Loading plan from URL session ID:', state.sessionId);
            fetchPlan();
        } else {
            console.error('[DEBUG] No valid session ID found in URL');
            showToast("Plan not found. Please start a new plan.", "error");
        }
    } else {
        // On index page, handle intake state recovery
        const urlParams = new URLSearchParams(window.location.search);
        
        // If we just landed here via hard restart, process it and stop.
        if (urlParams.get('restart') === '1') {
            logDebug('Hard restart URL detected. Executing clean resetIntake.');
            resetIntake();
            return;
        }

        if (detectReturnFromSubmit('load', false)) {
            return;
        }

        const savedIntake = sessionStorage.getItem('klara_intake_state');
        if (savedIntake) {
            state.intake = JSON.parse(savedIntake);
            logDebug('Recovered intake state from sessionStorage', state.intake);
        }

        const stepParam = parseInt(urlParams.get('step'));
        const savedStep = parseInt(sessionStorage.getItem('klara_current_step')) || 1;
        const initialStep = stepParam || savedStep;

        // Seed initial history state if missing or not an intake view
        if (!window.history.state || window.history.state.view !== 'intake') {
            const initialState = { view: 'intake', step: initialStep };
            history.replaceState(initialState, "", window.location.search || "?step=" + initialStep);
            logDebug('Seeded initial history state:', initialState);
        }

        renderStep(initialStep);
    }
});

window.addEventListener('popstate', (event) => {
    logDebug(`popstate fired. Current URL: ${window.location.href}`, event.state);
    logDebug(`popstate stats: History state: ${JSON.stringify(window.history.state)}, Current Step before handling: ${state.currentStep}`);
    
    if (event.state && event.state.view === 'intake') {
        const targetStep = parseInt(event.state.step);
        if (!isNaN(targetStep) && targetStep >= 1 && targetStep <= state.totalSteps) {
            logDebug(`popstate: Navigating to target step ${targetStep}`);
            renderStep(targetStep);
        } else {
            logDebug(`popstate: Invalid step number ${targetStep}. Defaulting to Step 1.`);
            renderStep(1);
            scrollToSection('screen-hero');
        }
    } else {
        // Fallback: If we pop back to the beginning of the site where state is null
        // we safely reset to Step 1 and scroll up so we don't leave a blank page.
        logDebug(`popstate: NO valid state found. Defaulting to target step 1.`);
        renderStep(1);
        scrollToSection('screen-hero');
    }
});

// ── API Error Reporting (Toast UI) ────────────────────────────
function showToast(message, type = "error") {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background: ${type === 'error' ? '#ff3b30' : '#28a745'};
        color: white; padding: 12px 24px; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-family: 'Inter', sans-serif;
        font-size: 0.9rem; opacity: 0; transform: translateY(-20px);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    `;
    toast.textContent = message;
    container.appendChild(toast);
    
    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    });

    // Animate out and remove
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-20px)";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

