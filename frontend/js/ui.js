/**
 * UI Module — Timeline, Budget Chart, Intelligence Panels, Toasts
 * Clean version: No emojis, uses Lucide icons and text labels.
 */

const UI = (() => {
    let budgetChart = null;

    // Interest display names (no emojis)
    const INTEREST_LABELS = {
        culture: 'Culture', beaches: 'Beaches', food: 'Food & Cuisine',
        nature: 'Nature', adventure: 'Adventure', temples: 'Temples',
        islands: 'Islands', nightlife: 'Nightlife', luxury: 'Luxury',
        diving: 'Diving', shopping: 'Shopping', historical: 'Historical',
        architecture: 'Architecture', wildlife: 'Wildlife', technology: 'Tech',
        art: 'Art', wine: 'Wine & Spirits', photography: 'Photography',
        music: 'Music', wellness: 'Wellness & Spa', hiking: 'Hiking',
        festivals: 'Festivals', sports: 'Sports', surfing: 'Surfing',
        skiing: 'Winter Sports', romance: 'Romance', family: 'Family',
        desert: 'Desert', mountains: 'Mountains', safari: 'Safari',
        spiritual: 'Spiritual', cruise: 'Cruise', camping: 'Camping',
        cycling: 'Cycling', photography: 'Photography',
    };

    // Interest icons (Lucide icon names)
    const INTEREST_ICONS = {
        culture: 'palette', beaches: 'umbrella', food: 'utensils',
        nature: 'trees', adventure: 'mountain', temples: 'landmark',
        islands: 'palmtree', nightlife: 'moon', luxury: 'gem',
        diving: 'waves', shopping: 'shopping-bag', historical: 'castle',
        architecture: 'building-2', wildlife: 'bird', technology: 'cpu',
        art: 'brush', wine: 'wine', photography: 'camera',
        music: 'music', wellness: 'heart-pulse', hiking: 'footprints',
        festivals: 'party-popper', sports: 'trophy', surfing: 'waves',
        skiing: 'snowflake', romance: 'heart', family: 'users',
        desert: 'sun', mountains: 'mountain-snow', safari: 'binoculars',
        spiritual: 'flame', cruise: 'ship', camping: 'tent',
        cycling: 'bike',
    };

    const SEASON_BADGES = {
        'ideal': { label: 'Ideal Season', cls: 'badge--success', icon: 'check-circle' },
        'partial': { label: 'Partial Season', cls: 'badge--warning', icon: 'alert-triangle' },
        'off-season': { label: 'Off-Season', cls: 'badge--danger', icon: 'alert-circle' },
    };

    const VISA_BADGES = {
        'visa_free': { label: 'Visa Free', cls: 'badge--success', icon: 'check' },
        'visa_on_arrival': { label: 'Visa on Arrival', cls: 'badge--success', icon: 'check' },
        'e_visa': { label: 'e-Visa Needed', cls: 'badge--warning', icon: 'file-text' },
        'visa_required': { label: 'Visa Required', cls: 'badge--danger', icon: 'shield-alert' },
        'home': { label: 'Home', cls: 'badge--info', icon: 'home' },
        'unknown': { label: 'Check Visa', cls: 'badge--neutral', icon: 'help-circle' },
    };

    const SAFETY_MAP = {
        'very safe': { cls: 'badge--success', icon: 'shield-check' },
        'safe': { cls: 'badge--info', icon: 'shield' },
        'moderate': { cls: 'badge--warning', icon: 'shield-alert' },
        'caution': { cls: 'badge--danger', icon: 'shield-x' },
    };

    /**
     * Render the itinerary timeline with intelligence data.
     */
    function renderTimeline(stops, homeCountry) {
        const timeline = document.getElementById('timeline');
        timeline.innerHTML = '';

        stops.forEach((stop, index) => {
            const card = document.createElement('div');
            card.className = 'timeline-card';
            card.style.animationDelay = `${index * 80}ms`;

            // Interest tags
            const interestTags = stop.interests
                .map(i => `<span class="timeline-card__interest-tag">${INTEREST_LABELS[i] || i}</span>`)
                .join('');

            // Season badge
            const seasonRating = stop.season_info?.season_rating || 'ideal';
            const seasonBadge = SEASON_BADGES[seasonRating] || SEASON_BADGES['ideal'];

            // Visa badge
            const visaReq = stop.visa_info?.requirement || 'unknown';
            const visaBadge = VISA_BADGES[visaReq] || VISA_BADGES['unknown'];

            // Safety badge
            const safety = SAFETY_MAP[stop.safety_score] || SAFETY_MAP['moderate'];

            // Currency info
            const currInfo = stop.currency_info;
            const currencyDisplay = currInfo
                ? `<div class="timeline-card__meta-item">
                     <i data-lucide="repeat"></i>
                     1 USD = ${currInfo.exchange_rate} ${currInfo.currency_code}
                   </div>`
                : '';

            // Top cities
            const citiesHtml = stop.top_cities?.length
                ? `<div class="timeline-card__cities">
                     <span class="timeline-card__cities-label">Visit:</span>
                     ${stop.top_cities.map(c => `<span class="city-chip">${c}</span>`).join('')}
                   </div>`
                : '';

            // Spending guide
            const spend = stop.spending_guide;
            const spendingHtml = spend
                ? `<div class="timeline-card__spending">
                     <div class="spending-row"><span>Accommodation</span><span>${spend.daily_accommodation_local.toLocaleString()} ${spend.currency_code}/day</span></div>
                     <div class="spending-row"><span>Meals</span><span>${spend.daily_meals_local.toLocaleString()} ${spend.currency_code}/day</span></div>
                     <div class="spending-row"><span>Transport</span><span>${spend.daily_transport_local.toLocaleString()} ${spend.currency_code}/day</span></div>
                     <div class="spending-row"><span>Activities</span><span>${spend.daily_activities_local.toLocaleString()} ${spend.currency_code}/day</span></div>
                     <div class="spending-row spending-row--total"><span>Total (${stop.days} days)</span><span>${spend.total_local.toLocaleString()} ${spend.currency_code}</span></div>
                   </div>`
                : '';

            // Activities
            const rec = stop.recommendations;
            const activitiesHtml = rec?.suggested_activities?.length
                ? `<div class="timeline-card__activities">
                     <span class="activities-label">Suggested activities</span>
                     <div class="activities-list">
                       ${rec.suggested_activities.slice(0, 5).map(a =>
                    `<div class="activity-item">
                              <span class="activity-name">${a.name}</span>
                              <span class="activity-duration">${a.duration}</span>
                           </div>`
                ).join('')}
                     </div>
                   </div>`
                : '';

            // Packing tips
            const packingHtml = rec?.packing_tips?.length
                ? `<div class="timeline-card__packing">
                     <span class="packing-label">Pack:</span>
                     <span class="packing-items">${rec.packing_tips.slice(0, 4).join(' · ')}</span>
                   </div>`
                : '';

            // Season tip
            const seasonTipHtml = stop.season_info?.tip
                ? `<div class="timeline-card__season-tip">${stop.season_info.tip}</div>`
                : '';

            card.innerHTML = `
                <div class="timeline-card__header">
                    <div class="timeline-card__country">
                        <span class="timeline-card__flag">${stop.flag}</span>
                        <span class="timeline-card__name">${stop.country}</span>
                    </div>
                    <span class="timeline-card__days">${stop.days} days</span>
                </div>

                <div class="timeline-card__badges">
                    <span class="badge ${seasonBadge.cls}"><i data-lucide="${seasonBadge.icon}"></i> ${seasonBadge.label}</span>
                    <span class="badge ${visaBadge.cls}"><i data-lucide="${visaBadge.icon}"></i> ${visaBadge.label}</span>
                    <span class="badge ${safety.cls}"><i data-lucide="${safety.icon}"></i> ${stop.safety_score || 'Unknown'}</span>
                </div>

                <div class="timeline-card__dates">${stop.start_date} — ${stop.end_date}</div>

                <div class="timeline-card__meta">
                    <div class="timeline-card__meta-item">
                        <i data-lucide="plane"></i>
                        Travel: <span class="timeline-card__meta-value">$${stop.travel_cost.toLocaleString()}</span>
                    </div>
                    <div class="timeline-card__meta-item">
                        <i data-lucide="bed"></i>
                        Stay: <span class="timeline-card__meta-value">$${stop.accommodation_cost.toLocaleString()}</span>
                    </div>
                    <div class="timeline-card__meta-item">
                        <i data-lucide="wallet"></i>
                        Total: <span class="timeline-card__meta-value">$${stop.total_cost.toLocaleString()}</span>
                    </div>
                    ${currencyDisplay}
                </div>

                <div class="timeline-card__interests">${interestTags}</div>

                ${citiesHtml}

                <div class="timeline-card__expandable" data-expanded="false">
                    <button class="timeline-card__expand-btn" onclick="this.parentElement.dataset.expanded = this.parentElement.dataset.expanded === 'true' ? 'false' : 'true'; this.innerHTML = this.parentElement.dataset.expanded === 'true' ? '<i data-lucide=\\'chevron-up\\'></i> Less details' : '<i data-lucide=\\'chevron-down\\'></i> More details'; if(typeof lucide !== 'undefined') lucide.createIcons({attrs: {class: ['inline-icon']}});">
                        <i data-lucide="chevron-down"></i> More details
                    </button>
                    <div class="timeline-card__expand-content">
                        ${spendingHtml}
                        ${activitiesHtml}
                        ${packingHtml}
                        ${seasonTipHtml}
                        ${stop.visa_info?.note ? `<div class="timeline-card__visa-note">${stop.visa_info.note}</div>` : ''}
                    </div>
                </div>
            `;

            timeline.appendChild(card);
        });

        // Home return card
        const homeCard = document.createElement('div');
        homeCard.className = 'timeline-card timeline-card--home';
        homeCard.style.animationDelay = `${stops.length * 80}ms`;
        homeCard.innerHTML = `
            <div class="timeline-card__header">
                <div class="timeline-card__country">
                    <span class="timeline-card__flag"><i data-lucide="home" style="width:20px;height:20px;"></i></span>
                    <span class="timeline-card__name">${homeCountry}</span>
                </div>
                <span class="timeline-card__days">Home</span>
            </div>
            <div class="timeline-card__dates">Return flight home</div>
        `;
        timeline.appendChild(homeCard);

        // Re-render Lucide icons in dynamically created HTML
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    /**
     * Render the route summary bar.
     */
    function renderRouteSummary(routeInfo, numStops, totalDays) {
        const routeDisplay = document.getElementById('route-display');
        const parts = routeInfo.route;
        routeDisplay.innerHTML = parts.map((country, i) => {
            const badge = `<span class="route-badge">${country}</span>`;
            const arrow = i < parts.length - 1 ? `<span class="route-arrow">&rarr;</span>` : '';
            return badge + arrow;
        }).join('');

        document.getElementById('stat-countries').textContent = numStops;
        document.getElementById('stat-days').textContent = totalDays;
        document.getElementById('stat-distance').textContent = routeInfo.total_distance_km.toLocaleString();
    }

    /**
     * Render the budget dashboard.
     */
    function renderBudgetDashboard(summary) {
        const used = summary.total_cost;
        const remaining = Math.max(summary.remaining, 0);
        const percent = summary.utilization_percent;

        document.getElementById('budget-percent').textContent = `${percent}%`;

        let chartColor = '#111111';
        if (percent > 95) chartColor = '#dc2626';
        else if (percent > 85) chartColor = '#ca8a04';
        else if (percent < 60) chartColor = '#16a34a';

        const ctx = document.getElementById('budget-chart').getContext('2d');
        if (budgetChart) budgetChart.destroy();

        budgetChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Used', 'Remaining'],
                datasets: [{
                    data: [used, remaining],
                    backgroundColor: [chartColor, '#f5f5f5'],
                    borderColor: ['transparent', 'transparent'],
                    borderWidth: 0,
                    borderRadius: 4,
                    spacing: 2,
                }]
            },
            options: {
                cutout: '78%',
                responsive: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.label}: $${ctx.raw.toLocaleString()}`
                        }
                    }
                },
                animation: { animateRotate: true, duration: 800 }
            }
        });

        const statsEl = document.getElementById('budget-stats');
        const remainingClass = summary.remaining >= 0 ? 'budget-stat-row__value--success' : 'budget-stat-row__value--danger';

        statsEl.innerHTML = `
            <div class="budget-stat-row">
                <span class="budget-stat-row__label">Total Budget</span>
                <span class="budget-stat-row__value">$${summary.budget.toLocaleString()}</span>
            </div>
            <div class="budget-stat-row">
                <span class="budget-stat-row__label">Trip Cost</span>
                <span class="budget-stat-row__value">$${summary.total_cost.toLocaleString()}</span>
            </div>
            <div class="budget-stat-row">
                <span class="budget-stat-row__label">Remaining</span>
                <span class="budget-stat-row__value ${remainingClass}">$${summary.remaining.toLocaleString()}</span>
            </div>
            <div class="budget-stat-row">
                <span class="budget-stat-row__label">Daily Average</span>
                <span class="budget-stat-row__value">$${summary.average_daily_cost.toLocaleString()}</span>
            </div>
        `;

        const tipsEl = document.getElementById('budget-tips');
        const tipsListEl = document.getElementById('budget-tips-list');
        if (summary.cost_saving_tips && summary.cost_saving_tips.length > 0) {
            tipsEl.style.display = 'block';
            tipsListEl.innerHTML = summary.cost_saving_tips.map(t => `<li>${t}</li>`).join('');
        } else {
            tipsEl.style.display = 'none';
        }
    }

    /**
     * Render season and visa alerts.
     */
    function renderAlerts(seasonAlerts, visaAlerts) {
        const alertsEl = document.getElementById('intelligence-alerts');
        if (!alertsEl) return;

        const allAlerts = [];

        if (seasonAlerts?.length) {
            allAlerts.push(...seasonAlerts.map(a => ({
                text: a,
                cls: 'alert--season',
                iconName: 'cloud-sun'
            })));
        }

        if (visaAlerts?.length) {
            allAlerts.push(...visaAlerts.map(a => ({
                text: a,
                cls: 'alert--visa',
                iconName: 'shield-alert'
            })));
        }

        if (allAlerts.length === 0) {
            alertsEl.style.display = 'none';
            return;
        }

        alertsEl.style.display = 'block';
        alertsEl.innerHTML = `
            <h4 class="alerts-title"><i data-lucide="info"></i> Travel Alerts</h4>
            ${allAlerts.map(a => `
                <div class="alert-item ${a.cls}">
                    <span class="alert-icon"><i data-lucide="${a.iconName}"></i></span>
                    <span class="alert-text">${a.text}</span>
                </div>
            `).join('')}
        `;

        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    /**
     * Show warnings.
     */
    function renderWarnings(warnings) {
        const container = document.getElementById('warnings');
        const card = document.getElementById('warning-card');

        if (warnings && warnings.length > 0) {
            container.style.display = 'block';
            card.textContent = warnings.join(' | ');
        } else {
            container.style.display = 'none';
        }
    }

    function showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('visible');
        setTimeout(() => { toast.classList.remove('visible'); }, duration);
    }

    function setLoading(show) {
        document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
    }

    function showResults() {
        const panel = document.getElementById('results-panel');
        panel.style.display = 'block';
        panel.offsetHeight;
        document.getElementById('map-overlay').classList.add('hidden');
    }

    function hideResults() {
        document.getElementById('results-panel').style.display = 'none';
        document.getElementById('map-overlay').classList.remove('hidden');
        TourMap.clearRoute();
    }

    return {
        renderTimeline,
        renderRouteSummary,
        renderBudgetDashboard,
        renderAlerts,
        renderWarnings,
        showToast,
        setLoading,
        showResults,
        hideResults,
        INTEREST_ICONS,
        INTEREST_LABELS,
    };
})();
