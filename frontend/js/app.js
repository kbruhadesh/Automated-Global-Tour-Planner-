/**
 * App Module — Main Logic
 * Handles form state, searchable dropdown, API calls, trip save/load.
 */

(() => {
    const API_BASE = `${window.location.origin}/api`;
    const STORAGE_KEY = 'tour-planner-saved-trip';

    let allCountries = [];
    let allInterests = [];
    let selectedInterests = new Set();
    let lastItineraryData = null;

    // ─── Initialize ──────────────────────────────────────────────

    async function init() {
        try {
            const res = await fetch(`${API_BASE}/countries`);
            const data = await res.json();

            allCountries = data.countries.map(c => typeof c === 'string' ? c : c.name).sort();
            allInterests = expandInterests(data.all_interests);

            // Show country count
            const countEl = document.getElementById('country-count');
            if (countEl) countEl.textContent = data.total_countries;

            setupSearchableDropdown();
            renderInterestChips();
            setDefaultDates();

            // Show load button if saved trip exists
            if (localStorage.getItem(STORAGE_KEY)) {
                const loadBtn = document.getElementById('btn-load-trip');
                if (loadBtn) loadBtn.style.display = '';
            }

            loadFromURL();
        } catch (e) {
            console.error('Init error:', e);
            UI.showToast('Failed to load countries');
        }

        // Wire up events
        document.getElementById('itinerary-form').addEventListener('submit', handleSubmit);
        document.getElementById('btn-print')?.addEventListener('click', () => window.print());
        document.getElementById('btn-share')?.addEventListener('click', shareLink);
        document.getElementById('btn-new')?.addEventListener('click', newTrip);
        document.getElementById('btn-save-trip')?.addEventListener('click', saveTrip);
        document.getElementById('btn-load-trip')?.addEventListener('click', loadTrip);
        document.getElementById('btn-sidebar-toggle')?.addEventListener('click', toggleSidebar);

        // Date change => show duration
        document.getElementById('start-date')?.addEventListener('change', updateDuration);
        document.getElementById('end-date')?.addEventListener('change', updateDuration);
    }

    // ─── Expand interest list ────────────────────────────────────

    function expandInterests(apiInterests) {
        // Extra interests introduced in Phase 3 redesign
        const extras = [
            'photography', 'music', 'wellness', 'hiking', 'festivals',
            'sports', 'surfing', 'skiing', 'romance', 'family',
            'desert', 'mountains', 'safari', 'spiritual', 'cruise',
            'camping', 'cycling'
        ];

        const all = new Set(apiInterests);
        extras.forEach(e => all.add(e));
        return [...all].sort();
    }

    // ─── Searchable Country Dropdown ─────────────────────────────

    function setupSearchableDropdown() {
        const input = document.getElementById('home-country-input');
        const hidden = document.getElementById('home-country');
        const dropdown = document.getElementById('home-country-dropdown');
        const wrapper = document.getElementById('home-country-wrapper');
        let highlightedIndex = -1;

        function renderDropdown(filter = '') {
            const filtered = filter
                ? allCountries.filter(c => c.toLowerCase().includes(filter.toLowerCase()))
                : allCountries;

            dropdown.innerHTML = '';
            highlightedIndex = -1;

            if (filtered.length === 0) {
                const li = document.createElement('li');
                li.className = 'no-results';
                li.textContent = 'No countries found';
                dropdown.appendChild(li);
                return;
            }

            filtered.forEach((country, idx) => {
                const li = document.createElement('li');
                li.textContent = country;
                li.dataset.value = country;
                li.addEventListener('click', () => selectCountry(country));
                dropdown.appendChild(li);
            });
        }

        function selectCountry(country) {
            input.value = country;
            hidden.value = country;
            dropdown.classList.remove('open');
        }

        function openDropdown() {
            renderDropdown(input.value);
            dropdown.classList.add('open');
        }

        function closeDropdown() {
            setTimeout(() => dropdown.classList.remove('open'), 150);
        }

        input.addEventListener('focus', openDropdown);
        input.addEventListener('input', () => {
            hidden.value = '';
            renderDropdown(input.value);
            dropdown.classList.add('open');
        });
        input.addEventListener('blur', closeDropdown);

        // Keyboard navigation
        input.addEventListener('keydown', (e) => {
            const items = dropdown.querySelectorAll('li:not(.no-results)');
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                highlightedIndex = Math.min(highlightedIndex + 1, items.length - 1);
                updateHighlight(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                highlightedIndex = Math.max(highlightedIndex - 1, 0);
                updateHighlight(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (highlightedIndex >= 0 && items[highlightedIndex]) {
                    selectCountry(items[highlightedIndex].dataset.value);
                }
            } else if (e.key === 'Escape') {
                closeDropdown();
            }
        });

        function updateHighlight(items) {
            items.forEach((li, idx) => {
                li.classList.toggle('highlighted', idx === highlightedIndex);
                if (idx === highlightedIndex) li.scrollIntoView({ block: 'nearest' });
            });
        }
    }

    // ─── Interest Chips ──────────────────────────────────────────

    function renderInterestChips() {
        const container = document.getElementById('interests-container');
        container.innerHTML = '';

        allInterests.forEach(interest => {
            const chip = document.createElement('button');
            chip.type = 'button';
            chip.className = 'chip';
            chip.dataset.interest = interest;

            const iconName = UI.INTEREST_ICONS[interest] || 'tag';
            chip.innerHTML = `<i data-lucide="${iconName}" class="chip__icon"></i> ${UI.INTEREST_LABELS[interest] || interest}`;

            chip.addEventListener('click', () => {
                chip.classList.toggle('active');
                if (chip.classList.contains('active')) {
                    selectedInterests.add(interest);
                } else {
                    selectedInterests.delete(interest);
                }
            });

            container.appendChild(chip);
        });

        // Re-init Lucide icons for the chips
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    // ─── Default Dates ───────────────────────────────────────────

    function setDefaultDates() {
        const startInput = document.getElementById('start-date');
        const endInput = document.getElementById('end-date');
        const today = new Date();
        const start = new Date(today);
        start.setDate(start.getDate() + 30);
        const end = new Date(start);
        end.setDate(end.getDate() + 14);

        startInput.value = start.toISOString().slice(0, 10);
        endInput.value = end.toISOString().slice(0, 10);
        startInput.min = today.toISOString().slice(0, 10);
        endInput.min = today.toISOString().slice(0, 10);
        updateDuration();
    }

    function updateDuration() {
        const start = new Date(document.getElementById('start-date').value);
        const end = new Date(document.getElementById('end-date').value);
        const durationEl = document.getElementById('trip-duration');
        const textEl = document.getElementById('trip-duration-text');

        if (!isNaN(start) && !isNaN(end) && end > start) {
            const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
            textEl.textContent = `${days} day${days !== 1 ? 's' : ''} trip`;
            durationEl.style.display = 'flex';
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } else {
            durationEl.style.display = 'none';
        }
    }

    // ─── Submit ──────────────────────────────────────────────────

    async function handleSubmit(e) {
        e.preventDefault();

        const homeCountry = document.getElementById('home-country').value;
        if (!homeCountry) {
            UI.showToast('Please select a home country');
            document.getElementById('home-country-input').focus();
            return;
        }

        if (selectedInterests.size === 0) {
            UI.showToast('Please select at least one interest');
            return;
        }

        const request = {
            home_country: homeCountry,
            num_countries: parseInt(document.getElementById('num-countries').value, 10),
            interests: [...selectedInterests],
            budget: parseInt(document.getElementById('budget').value, 10),
            start_date: document.getElementById('start-date').value,
            end_date: document.getElementById('end-date').value,
        };

        UI.setLoading(true);
        UI.hideResults();

        try {
            const res = await fetch(`${API_BASE}/generate-itinerary`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(request),
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'API error');

            // Store for saving
            lastItineraryData = { data, homeCountry: request.home_country, request };

            renderItinerary(data, request.home_country);
            UI.showToast('Itinerary generated');
            UI.renderAlerts(data.season_alerts, data.visa_alerts);
        } catch (err) {
            UI.showToast(`Error: ${err.message}`);
        } finally {
            UI.setLoading(false);
        }
    }

    // ─── Render ──────────────────────────────────────────────────

    function renderItinerary(data, homeCountry) {
        TourMap.init();

        const homeCoords = data.stops.length > 0
            ? getHomeCoords(homeCountry, data.route_info.route, data.stops)
            : null;

        TourMap.drawRoute(data.stops, homeCountry, homeCoords);
        UI.renderTimeline(data.stops, homeCountry);
        UI.renderRouteSummary(data.route_info, data.stops.length, data.total_days);
        UI.renderBudgetDashboard(data.budget_summary);

        if (data.warnings?.length) UI.renderWarnings(data.warnings);
        UI.showResults();
    }

    function getHomeCoords(homeCountry, route, stops) {
        // Try to infer home coordinates from the countries data
        // We'll just center on the first stop if we can't find it
        return null; // The backend should include home coords in route_info
    }

    // ─── Save / Load ─────────────────────────────────────────────

    function saveTrip() {
        if (!lastItineraryData) {
            UI.showToast('Generate an itinerary first');
            return;
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(lastItineraryData));
        UI.showToast('Trip saved');
        const loadBtn = document.getElementById('btn-load-trip');
        if (loadBtn) loadBtn.style.display = '';
    }

    function loadTrip() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (!saved) {
            UI.showToast('No saved trip found');
            return;
        }

        try {
            const { data, homeCountry, request } = JSON.parse(saved);
            lastItineraryData = { data, homeCountry, request };

            // Restore form
            document.getElementById('home-country-input').value = request.home_country;
            document.getElementById('home-country').value = request.home_country;
            document.getElementById('num-countries').value = request.num_countries;
            document.getElementById('budget').value = request.budget;
            document.getElementById('start-date').value = request.start_date;
            document.getElementById('end-date').value = request.end_date;

            // Restore interests
            selectedInterests.clear();
            document.querySelectorAll('.chip').forEach(chip => {
                const i = chip.dataset.interest;
                if (request.interests.includes(i)) {
                    chip.classList.add('active');
                    selectedInterests.add(i);
                } else {
                    chip.classList.remove('active');
                }
            });

            updateDuration();
            renderItinerary(data, homeCountry);
            UI.renderAlerts(data.season_alerts, data.visa_alerts);
            UI.showToast('Trip loaded');
        } catch (e) {
            UI.showToast('Error loading trip');
        }
    }

    // ─── Share ───────────────────────────────────────────────────

    function shareLink() {
        if (!lastItineraryData) {
            UI.showToast('Generate an itinerary first');
            return;
        }

        const req = lastItineraryData.request;
        const params = new URLSearchParams({
            home: req.home_country,
            n: req.num_countries,
            i: req.interests.join(','),
            b: req.budget,
            s: req.start_date,
            e: req.end_date,
        });

        const url = `${window.location.origin}?${params.toString()}`;
        navigator.clipboard.writeText(url)
            .then(() => UI.showToast('Link copied to clipboard'))
            .catch(() => UI.showToast('Could not copy link'));
    }

    function loadFromURL() {
        const params = new URLSearchParams(window.location.search);
        const home = params.get('home');
        if (!home) return;

        document.getElementById('home-country-input').value = home;
        document.getElementById('home-country').value = home;

        if (params.get('n')) document.getElementById('num-countries').value = params.get('n');
        if (params.get('b')) document.getElementById('budget').value = params.get('b');
        if (params.get('s')) document.getElementById('start-date').value = params.get('s');
        if (params.get('e')) document.getElementById('end-date').value = params.get('e');

        if (params.get('i')) {
            const interests = params.get('i').split(',');
            selectedInterests = new Set(interests);
            document.querySelectorAll('.chip').forEach(chip => {
                if (interests.includes(chip.dataset.interest)) {
                    chip.classList.add('active');
                }
            });
        }

        updateDuration();
    }

    function newTrip() {
        UI.hideResults();
        lastItineraryData = null;
        document.getElementById('itinerary-form').reset();
        selectedInterests.clear();
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        setDefaultDates();
        document.getElementById('home-country-input').value = '';
        document.getElementById('home-country').value = '';
    }

    function toggleSidebar() {
        document.getElementById('sidebar').classList.toggle('open');
    }

    // ─── Init on load ────────────────────────────────────────────

    document.addEventListener('DOMContentLoaded', init);
})();
