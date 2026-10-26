/**
 * Campus Facility Feedback Analysis System - Frontend Interactivity
 * Offline Chart.js implementation with local Inter font styling,
 * Home page overview chart, and Ratings page interactive chart & sortable table.
 */

// Set global Chart.js typography to Inter and dark body text
if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.color = "#4b5563";
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Home page components if present
    initHomeRatingChart();
    initFacilityInspector();

    // Initialize Ratings page components if present
    initRatingsPage();

    // Initialize Recurring Issues page components if present
    initIssuesPage();

    // Initialize Summaries page components if present
    initSummariesPage();

    // Initialize Flagged Comments page components if present
    initFlaggedPage();

    // Initialize Submit Feedback page components if present
    initSubmitPage();
});

// -------------------------------------------------------------
// Helper: Rating Tier Colors
// Green (>= 2.60): Good (#15803d)
// Amber (2.45 - 2.59): Moderate (#b45309)
// Red (< 2.45): Needs Attention (#b91c1c)
// -------------------------------------------------------------
function getRatingColor(rating) {
    if (rating >= 2.60) return "#15803d";
    if (rating >= 2.45) return "#b45309";
    return "#b91c1c";
}

function getRatingBadgeClass(rating) {
    if (rating >= 2.60) return "badge-good";
    if (rating >= 2.45) return "badge-mid";
    return "badge-bad";
}

// -------------------------------------------------------------
// 1. Home Page: Facility Ratings Overview Chart
// -------------------------------------------------------------
let homeRatingChartInstance = null;

function initHomeRatingChart() {
    const ctx = document.getElementById("facilityRatingChart");
    if (!ctx || !window.FACILITY_DATA) return;

    let currentSort = "highest";
    let dataCopy = [...window.FACILITY_DATA];

    function sortData(mode) {
        if (mode === "highest") {
            dataCopy.sort((a, b) => b.rating - a.rating);
        } else if (mode === "lowest") {
            dataCopy.sort((a, b) => a.rating - b.rating);
        } else if (mode === "alpha") {
            dataCopy.sort((a, b) => a.name.localeCompare(b.name));
        }
    }

    sortData(currentSort);

    const chartConfig = {
        data: {
            labels: dataCopy.map(d => d.name),
            datasets: [
                {
                    type: "line",
                    label: "Campus Average (2.54)",
                    data: dataCopy.map(() => 2.54),
                    borderColor: "#4a2c6d",           // Main brand colour (#4a2c6d)
                    borderWidth: 2,
                    borderDash: [6, 4],
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    fill: false,
                    order: 1
                },
                {
                    type: "bar",
                    label: "Facility Rating",
                    data: dataCopy.map(d => d.rating),
                    backgroundColor: dataCopy.map(d => getRatingColor(d.rating)),
                    borderRadius: 4,
                    barThickness: 32,
                    order: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 250
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: "#111827",
                    titleFont: { family: "'Inter', sans-serif", size: 13, weight: "600" },
                    bodyFont: { family: "'Inter', sans-serif", size: 13 },
                    padding: 12,
                    cornerRadius: 4,
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return ` Campus Benchmark: 2.54 / 5.0`;
                            }
                            const val = context.parsed.y;
                            const item = dataCopy[context.dataIndex];
                            let tier = "Moderate";
                            if (val >= 2.60) tier = "Good (above average)";
                            else if (val < 2.45) tier = "Needs attention";

                            return [
                                ` Overall Rating: ${val.toFixed(2)} / 5.0`,
                                ` Performance: ${tier}`,
                                ` Primary Complaint: ${item.top_issue}`,
                                ` Verified Comments: ${item.comments_count}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 1.0,
                    max: 3.5,
                    ticks: {
                        stepSize: 0.5,
                        font: { family: "'Inter', sans-serif", size: 12 },
                        color: "#6b7280",
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    },
                    grid: {
                        color: "#f3f4f6"
                    }
                },
                x: {
                    ticks: {
                        font: { family: "'Inter', sans-serif", size: 13, weight: "600" },
                        color: "#111827"
                    },
                    grid: {
                        display: false
                    }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const el = elements.find(e => e.datasetIndex === 1);
                    if (el) {
                        const idx = el.index;
                        const selected = dataCopy[idx];
                        selectFacilityCard(selected.id);
                    }
                }
            }
        }
    };

    homeRatingChartInstance = new Chart(ctx, chartConfig);

    // Sort control listeners
    const sortButtons = document.querySelectorAll("#chartSortGroup .btn-sort");
    sortButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            sortButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const mode = btn.getAttribute("data-sort");
            sortData(mode);

            // Update chart data
            homeRatingChartInstance.data.labels = dataCopy.map(d => d.name);
            homeRatingChartInstance.data.datasets[0].data = dataCopy.map(() => 2.54);
            homeRatingChartInstance.data.datasets[1].data = dataCopy.map(d => d.rating);
            homeRatingChartInstance.data.datasets[1].backgroundColor = dataCopy.map(d => getRatingColor(d.rating));
            homeRatingChartInstance.update();
        });
    });
}

// -------------------------------------------------------------
// 2. Home Page: Interactive Facility Inspector & Search Filter
// -------------------------------------------------------------
function selectFacilityCard(facilityId) {
    const cards = document.querySelectorAll(".facility-card");
    let target = null;
    cards.forEach(card => {
        if (card.getAttribute("data-id") === facilityId) {
            target = card;
        }
    });

    if (target) {
        cards.forEach(c => c.classList.remove("selected"));
        target.classList.add("selected");
        updateInspectorDetail(target);
    }
}

function updateInspectorDetail(card) {
    const name = card.getAttribute("data-name");
    const rating = parseFloat(card.getAttribute("data-rating"));
    const comments = card.getAttribute("data-comments");
    const topIssue = card.getAttribute("data-topissue");

    const statusEl = document.getElementById("inspectStatus");
    const nameEl = document.getElementById("inspectName");
    const ratingEl = document.getElementById("inspectRating");
    const commentsEl = document.getElementById("inspectComments");
    const topIssueEl = document.getElementById("inspectTopIssue");

    if (statusEl) {
        if (rating >= 2.60) {
            statusEl.textContent = "Good (above average)";
            statusEl.style.color = "#15803d";
            statusEl.style.backgroundColor = "#f3eefc";
        } else if (rating >= 2.45) {
            statusEl.textContent = "Moderate";
            statusEl.style.color = "#b45309";
            statusEl.style.backgroundColor = "#fffbeb";
        } else {
            statusEl.textContent = "Needs attention";
            statusEl.style.color = "#b91c1c";
            statusEl.style.backgroundColor = "#fef2f2";
        }
    }
    if (nameEl) nameEl.textContent = name;
    if (ratingEl) ratingEl.textContent = `${rating.toFixed(2)} / 5.0`;
    if (commentsEl) commentsEl.textContent = comments;
    if (topIssueEl) topIssueEl.textContent = topIssue;
}

function initFacilityInspector() {
    const cards = document.querySelectorAll(".facility-card");
    const searchInput = document.getElementById("facilitySearchInput");

    // Click handler for cards
    cards.forEach(card => {
        card.addEventListener("click", () => {
            cards.forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            updateInspectorDetail(card);
        });
    });

    // Real-time search filter
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const term = e.target.value.toLowerCase().trim();
            cards.forEach(card => {
                const name = card.getAttribute("data-name").toLowerCase();
                const issue = card.getAttribute("data-topissue").toLowerCase();
                if (name.includes(term) || issue.includes(term)) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }
}

// =============================================================
// 3. Ratings Page: Interactive Chart & Sortable Data Table
// =============================================================
let ratingsChartInstance = null;
let currentSortColumn = "rating";
let currentSortAsc = false; // default highest rating first

function initRatingsPage() {
    const tableBody = document.getElementById("ratingsTableBody");
    const chartCtx = document.getElementById("ratingsChart");
    if (!tableBody || !chartCtx || !window.RATINGS_DATA) return;

    const facilitySelect = document.getElementById("facilitySelect");
    const topicSelect = document.getElementById("topicSelect");
    const topicSelectWrap = document.getElementById("topicSelectWrap");
    const btnModeOverall = document.getElementById("btnModeOverall");
    const btnModeTopics = document.getElementById("btnModeTopics");
    const searchInput = document.getElementById("ratingsTableSearch");
    const tableRowCount = document.getElementById("tableRowCount");
    const chartHeaderTitle = document.getElementById("chartHeaderTitle");
    const chartHeaderDesc = document.getElementById("chartHeaderDesc");

    let activeMode = "overall"; // "overall" | "topics"

    // ---------------------------------------------------------
    // Function: Render Data Table
    // ---------------------------------------------------------
    function renderTable() {
        const facFilter = facilitySelect.value;
        const topFilter = topicSelect.value;
        const searchTerm = searchInput.value.toLowerCase().trim();

        // 1. Filter rows
        let filtered = window.RATINGS_DATA.filter(row => {
            // Mode filter
            if (activeMode === "overall" && !row.is_overall) return false;
            if (activeMode === "topics" && row.is_overall) return false;

            // Facility filter
            if (facFilter !== "all" && row.facility !== facFilter) return false;

            // Topic filter
            if (topFilter !== "all" && row.category !== topFilter) return false;

            // Search filter
            if (searchTerm) {
                const matchFac = row.display_facility.toLowerCase().includes(searchTerm);
                const matchCat = row.category.toLowerCase().includes(searchTerm);
                if (!matchFac && !matchCat) return false;
            }

            return true;
        });

        // 2. Sort rows
        filtered.sort((a, b) => {
            let valA = a[currentSortColumn];
            let valB = b[currentSortColumn];

            // Handle nulls
            if (valA === null || valA === undefined) valA = -999;
            if (valB === null || valB === undefined) valB = -999;

            if (typeof valA === "string") {
                return currentSortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return currentSortAsc ? valA - valB : valB - valA;
        });

        // 3. Render HTML
        if (filtered.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 32px; color: var(--text-muted);">No matching rating records found.</td></tr>`;
        } else {
            tableBody.innerHTML = filtered.map(row => {
                const ratingBadge = `<span class="badge-rating ${getRatingBadgeClass(row.rating)}">${row.rating.toFixed(2)}</span>`;
                const catDisplay = row.is_overall ? `<span class="badge-overall">OVERALL</span>` : row.category;
                const posDisplay = row.positive !== null ? row.positive : `<span style="color:#9ca3af;">—</span>`;
                const neuDisplay = row.neutral !== null ? row.neutral : `<span style="color:#9ca3af;">—</span>`;
                const negDisplay = row.negative !== null ? row.negative : `<span style="color:#9ca3af;">—</span>`;
                const shareDisplay = row.negative_share !== null ? `${row.negative_share.toFixed(1)}%` : `<span style="color:#9ca3af;">—</span>`;

                return `
                    <tr>
                        <td><strong>${row.display_facility}</strong></td>
                        <td>${catDisplay}</td>
                        <td>${ratingBadge}</td>
                        <td>${row.mentions}</td>
                        <td>${posDisplay}</td>
                        <td>${neuDisplay}</td>
                        <td>${negDisplay}</td>
                        <td>${shareDisplay}</td>
                    </tr>
                `;
            }).join("");
        }

        // Update count badge
        if (tableRowCount) {
            tableRowCount.textContent = `Showing ${filtered.length} of ${window.RATINGS_DATA.length} records`;
        }
    }

    // ---------------------------------------------------------
    // Function: Update & Render Chart
    // ---------------------------------------------------------
    function updateChart() {
        const facFilter = facilitySelect.value;
        const topFilter = topicSelect.value;
        const benchmark = window.CAMPUS_AVG || 2.54;

        let chartItems = [];

        if (activeMode === "overall") {
            // Overall mode: show facilities
            let ovRows = window.RATINGS_DATA.filter(r => r.is_overall);
            if (facFilter !== "all") {
                ovRows = ovRows.filter(r => r.facility === facFilter);
            }
            ovRows.sort((a, b) => b.rating - a.rating);
            chartItems = ovRows.map(r => ({ label: r.display_facility, rating: r.rating, mentions: r.mentions, share: r.negative_share }));

            if (chartHeaderTitle) chartHeaderTitle.textContent = "Overall Facility Ratings";
            if (chartHeaderDesc) chartHeaderDesc.textContent = "Facility-level scores on a 1.0 to 5.0 scale. The dashed line marks the campus benchmark (2.54).";
        } else {
            // Topics mode
            let aspectRows = window.RATINGS_DATA.filter(r => !r.is_overall);
            if (facFilter !== "all") {
                aspectRows = aspectRows.filter(r => r.facility === facFilter);
            }
            if (topFilter !== "all") {
                aspectRows = aspectRows.filter(r => r.category === topFilter);
            }
            aspectRows.sort((a, b) => b.rating - a.rating);

            chartItems = aspectRows.map(r => {
                const label = facFilter === "all" ? `${r.display_facility}: ${r.category}` : r.category;
                return { label: label, rating: r.rating, mentions: r.mentions, share: r.negative_share };
            });

            // Limit chart bars if too many to keep readable
            if (chartItems.length > 20) {
                chartItems = chartItems.slice(0, 20);
            }

            const facName = facFilter !== "all" ? facilitySelect.options[facilitySelect.selectedIndex].text : "All Facilities";
            if (chartHeaderTitle) chartHeaderTitle.textContent = `${facName}: Topic Sentiment Ratings`;
            if (chartHeaderDesc) chartHeaderDesc.textContent = `Displaying topic-level scores on a 1.0 to 5.0 scale. Benchmark line at ${benchmark}.`;
        }

        const labels = chartItems.map(item => item.label);
        const dataValues = chartItems.map(item => item.rating);
        const colors = chartItems.map(item => getRatingColor(item.rating));

        if (!ratingsChartInstance) {
            ratingsChartInstance = new Chart(chartCtx, {
                data: {
                    labels: labels,
                    datasets: [
                        {
                            type: "line",
                            label: "Campus Average",
                            data: labels.map(() => benchmark),
                            borderColor: "#4a2c6d",
                            borderWidth: 2,
                            borderDash: [6, 4],
                            pointRadius: 0,
                            pointHoverRadius: 0,
                            fill: false,
                            order: 1
                        },
                        {
                            type: "bar",
                            label: "Rating",
                            data: dataValues,
                            backgroundColor: colors,
                            borderRadius: 4,
                            barThickness: labels.length > 10 ? 20 : 32,
                            order: 2
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 250 },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "#111827",
                            titleFont: { family: "'Inter', sans-serif", size: 13, weight: "600" },
                            bodyFont: { family: "'Inter', sans-serif", size: 13 },
                            padding: 12,
                            cornerRadius: 4,
                            callbacks: {
                                label: function(context) {
                                    if (context.datasetIndex === 0) {
                                        return ` Campus Benchmark: ${benchmark} / 5.0`;
                                    }
                                    const val = context.parsed.y;
                                    const item = chartItems[context.dataIndex];
                                    let lines = [` Score: ${val.toFixed(2)} / 5.0`];
                                    if (item && item.mentions) lines.push(` Mentions: ${item.mentions}`);
                                    if (item && item.share !== null && item.share !== undefined) {
                                        lines.push(` Negative Share: ${item.share.toFixed(1)}%`);
                                    }
                                    return lines;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            min: 1.0,
                            max: 4.0,
                            ticks: {
                                stepSize: 0.5,
                                font: { family: "'Inter', sans-serif", size: 12 },
                                color: "#6b7280",
                                callback: function(val) { return val.toFixed(1); }
                            },
                            grid: { color: "#f3f4f6" }
                        },
                        x: {
                            ticks: {
                                font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
                                color: "#111827",
                                maxRotation: 45,
                                minRotation: 0
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        } else {
            ratingsChartInstance.data.labels = labels;
            ratingsChartInstance.data.datasets[0].data = labels.map(() => benchmark);
            ratingsChartInstance.data.datasets[1].data = dataValues;
            ratingsChartInstance.data.datasets[1].backgroundColor = colors;
            ratingsChartInstance.data.datasets[1].barThickness = labels.length > 10 ? 20 : 32;
            ratingsChartInstance.update();
        }
    }

    // ---------------------------------------------------------
    // Event Listeners: Toggle Buttons
    // ---------------------------------------------------------
    btnModeOverall.addEventListener("click", () => {
        btnModeOverall.classList.add("active");
        btnModeTopics.classList.remove("active");
        activeMode = "overall";
        topicSelectWrap.style.display = "none";
        renderTable();
        updateChart();
    });

    btnModeTopics.addEventListener("click", () => {
        btnModeTopics.classList.add("active");
        btnModeOverall.classList.remove("active");
        activeMode = "topics";
        topicSelectWrap.style.display = "inline-flex";
        renderTable();
        updateChart();
    });

    // Event Listeners: Select Dropdowns
    facilitySelect.addEventListener("change", () => {
        if (facilitySelect.value !== "all" && activeMode === "overall") {
            // When specific facility selected in overall mode, auto switch to topics view for that facility
            btnModeTopics.click();
        } else {
            renderTable();
            updateChart();
        }
    });

    topicSelect.addEventListener("change", () => {
        renderTable();
        updateChart();
    });

    // Event Listener: Live Search Filter
    searchInput.addEventListener("input", () => {
        renderTable();
    });

    // Event Listeners: Sortable Table Headers
    const sortableHeaders = document.querySelectorAll(".sortable-th");
    sortableHeaders.forEach(th => {
        th.addEventListener("click", () => {
            const col = th.getAttribute("data-col");
            if (currentSortColumn === col) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortColumn = col;
                currentSortAsc = (col === "display_facility" || col === "category"); // strings default asc, numbers default desc
            }

            // Update header UI
            sortableHeaders.forEach(h => {
                h.classList.remove("active-sort");
                const icon = h.querySelector(".sort-icon");
                if (icon) icon.textContent = "⇕";
            });
            th.classList.add("active-sort");
            const icon = th.querySelector(".sort-icon");
            if (icon) icon.textContent = currentSortAsc ? "▲" : "▼";

            renderTable();
        });
    });

    // Initial table and chart render
    renderTable();
    updateChart();
}

// =============================================================
// 4. Recurring Issues Page: Chart & Expandable Comments List
// =============================================================
let issuesChartInstance = null;

function initIssuesPage() {
    const chartCtx = document.getElementById("issuesChart");
    const issuesContainer = document.getElementById("expandableIssuesList");
    if (!chartCtx || !issuesContainer || !window.ISSUES_DATA) return;

    const facilitySelect = document.getElementById("issueFacilitySelect");
    const severitySlider = document.getElementById("severitySlider");
    const sliderValueDisplay = document.getElementById("sliderValueDisplay");
    const sortSelect = document.getElementById("issueSortSelect");
    const issuesRowCount = document.getElementById("issuesRowCount");
    const chartTitle = document.getElementById("issuesChartTitle");
    const chartDesc = document.getElementById("issuesChartDesc");

    // Helper: Determine severity class & color
    function getSeverityProps(share) {
        if (share >= 85.0) {
            return { color: "#b91c1c", pillClass: "pill-severity-high", label: "High severity" };
        } else if (share >= 75.0) {
            return { color: "#b45309", pillClass: "pill-severity-mid", label: "Moderate severity" };
        }
        return { color: "#8b5cf6", pillClass: "pill-severity-notable", label: "Notable severity" };
    }

    // ---------------------------------------------------------
    // Function: Filter & Sort Issues Data
    // ---------------------------------------------------------
    function getProcessedIssues() {
        const facFilter = facilitySelect.value;
        const minThreshold = parseFloat(severitySlider.value);
        const sortMode = sortSelect.value;

        // 1. Filter
        let filtered = window.ISSUES_DATA.filter(item => {
            if (facFilter !== "all" && item.facility !== facFilter) return false;
            if (item.negative_share < minThreshold) return false;
            return true;
        });

        // 2. Sort
        filtered.sort((a, b) => {
            if (sortMode === "neg_share") {
                return b.negative_share - a.negative_share;
            } else if (sortMode === "mentions") {
                return b.mentions - a.mentions;
            } else if (sortMode === "rating") {
                return a.rating - b.rating; // lowest rating first
            }
            return 0;
        });

        return filtered;
    }

    // ---------------------------------------------------------
    // Function: Render Expandable Issues List
    // ---------------------------------------------------------
    function renderIssuesList(issues) {
        if (issuesRowCount) {
            issuesRowCount.textContent = `Showing ${issues.length} of ${window.ISSUES_DATA.length} recurring issues`;
        }

        if (issues.length === 0) {
            issuesContainer.innerHTML = `
                <div style="background:#ffffff; border:1px solid var(--border); border-radius:var(--radius); padding:36px 20px; text-align:center; color:var(--text-muted);">
                    No recurring issues meet the selected facility or severity threshold criteria.
                </div>
            `;
            return;
        }

        issuesContainer.innerHTML = issues.map((issue, index) => {
            const sev = getSeverityProps(issue.negative_share);
            
            // Format student quotes
            let quotesHtml = "";
            if (issue.comments && issue.comments.length > 0) {
                quotesHtml = issue.comments.map(c => `
                    <div class="comment-quote-item">
                        &ldquo;${escapeHtml(c)}&rdquo;
                    </div>
                `).join("");
            } else {
                quotesHtml = `<div class="no-comments-msg">No non-abusive negative comments recorded for this issue.</div>`;
            }

            return `
                <div class="issue-row-card" id="issueCard-${index}">
                    <div class="issue-row-header" onclick="toggleIssueRow(${index})">
                        <div class="issue-title-area">
                            <span class="issue-facility-badge">${issue.display_facility}</span>
                            <span class="issue-category-name">${issue.category}</span>
                        </div>
                        <div class="issue-metrics-row">
                            <span class="issue-metric-pill ${sev.pillClass}">${issue.negative_share.toFixed(1)}% negative</span>
                            <span style="font-size:0.82rem; color:var(--text-body); font-weight:500;">${issue.mentions} mentions (${issue.negative} negative)</span>
                            <span class="badge-rating ${getRatingBadgeClass(issue.rating)}" style="margin-left:4px;">${issue.rating.toFixed(2)}</span>
                            <span class="issue-expand-btn" id="expandBtnText-${index}">
                                Show comments <span style="font-size:0.75rem;">▼</span>
                            </span>
                        </div>
                    </div>
                    <div class="issue-drawer" id="issueDrawer-${index}">
                        <div class="drawer-header">
                            <span class="drawer-title">Verified Student Feedback (${issue.comments_count} comments)</span>
                            <span class="drawer-note">Filtered and verified by DistilBERT model</span>
                        </div>
                        <div class="comments-quotes-grid">
                            ${quotesHtml}
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    }

    // ---------------------------------------------------------
    // Function: Update Horizontal Bar Chart
    // ---------------------------------------------------------
    function updateIssuesChart(issues) {
        const facFilter = facilitySelect.value;
        const facName = facFilter !== "all" ? facilitySelect.options[facilitySelect.selectedIndex].text : "All Facilities";

        if (chartTitle) {
            chartTitle.textContent = `${facName}: Recurring Issues Ranked by Severity`;
        }
        if (chartDesc) {
            chartDesc.textContent = `Showing ${issues.length} recurring issues with a negative share of at least ${severitySlider.value}%.`;
        }

        const labels = issues.map(item => `${item.display_facility}: ${item.category}`);
        const dataValues = issues.map(item => item.negative_share);
        const barColors = issues.map(item => getSeverityProps(item.negative_share).color);

        if (!issuesChartInstance) {
            issuesChartInstance = new Chart(chartCtx, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Negative Share (%)",
                        data: dataValues,
                        backgroundColor: barColors,
                        borderRadius: 4,
                        barThickness: labels.length > 8 ? 16 : 24
                    }]
                },
                options: {
                    indexAxis: "y", // Horizontal bars for clear, easy-to-read labels
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 250 },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "#111827",
                            titleFont: { family: "'Inter', sans-serif", size: 13, weight: "600" },
                            bodyFont: { family: "'Inter', sans-serif", size: 13 },
                            padding: 12,
                            cornerRadius: 4,
                            callbacks: {
                                label: function(context) {
                                    const item = issues[context.dataIndex];
                                    return [
                                        ` Negative Share: ${item.negative_share.toFixed(1)}%`,
                                        ` Total Mentions: ${item.mentions}`,
                                        ` Negative Comments: ${item.negative}`,
                                        ` Overall Rating: ${item.rating.toFixed(2)} / 5.0`
                                    ];
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            min: 60,
                            max: 100,
                            ticks: {
                                stepSize: 10,
                                font: { family: "'Inter', sans-serif", size: 12 },
                                color: "#6b7280",
                                callback: function(val) { return val + "%"; }
                            },
                            grid: { color: "#f3f4f6" }
                        },
                        y: {
                            ticks: {
                                font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
                                color: "#111827"
                            },
                            grid: { display: false }
                        }
                    }
                }
            });
        } else {
            issuesChartInstance.data.labels = labels;
            issuesChartInstance.data.datasets[0].data = dataValues;
            issuesChartInstance.data.datasets[0].backgroundColor = barColors;
            issuesChartInstance.data.datasets[0].barThickness = labels.length > 8 ? 16 : 24;
            issuesChartInstance.update();
        }
    }

    // ---------------------------------------------------------
    // Event Handlers
    // ---------------------------------------------------------
    function refreshView() {
        const processed = getProcessedIssues();
        renderIssuesList(processed);
        updateIssuesChart(processed);
    }

    facilitySelect.addEventListener("change", refreshView);
    sortSelect.addEventListener("change", refreshView);

    severitySlider.addEventListener("input", () => {
        sliderValueDisplay.textContent = `${parseFloat(severitySlider.value).toFixed(1)}%`;
        refreshView();
    });

    // Initial render
    refreshView();
}

// Global toggle handler for expanding issue rows
window.toggleIssueRow = function(index) {
    const card = document.getElementById(`issueCard-${index}`);
    const btnText = document.getElementById(`expandBtnText-${index}`);
    if (!card || !btnText) return;

    const isExpanded = card.classList.contains("expanded");
    if (isExpanded) {
        card.classList.remove("expanded");
        btnText.innerHTML = `Show comments <span style="font-size:0.75rem;">▼</span>`;
    } else {
        card.classList.add("expanded");
        btnText.innerHTML = `Hide comments <span style="font-size:0.75rem;">▲</span>`;
    }
};

// Helper: Escape HTML to prevent injection
function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// =============================================================
// 5. Summaries Page: Interactive Tabs, Presentation Card & Compare
// =============================================================
function initSummariesPage() {
    const singleSection = document.getElementById("singleFacilitySection");
    const compareSection = document.getElementById("compareFacilitySection");
    const tabsBar = document.getElementById("facilityTabsBar");
    const singleCard = document.getElementById("singleSummaryCard");
    if (!singleSection || !compareSection || !tabsBar || !singleCard || !window.FACILITY_SUMMARIES) return;

    const btnModeSingle = document.getElementById("btnModeSingle");
    const btnModeCompare = document.getElementById("btnModeCompare");
    const tabSortWrap = document.getElementById("tabSortWrap");
    const tabSortButtons = document.querySelectorAll("#tabSortGroup .btn-sort");

    const compareSelectA = document.getElementById("compareSelectA");
    const compareSelectB = document.getElementById("compareSelectB");
    const cardCompareA = document.getElementById("cardCompareA");
    const cardCompareB = document.getElementById("cardCompareB");

    let currentTabSort = "highest"; // "highest" | "lowest" | "alpha"
    let selectedFacilityId = window.FACILITY_SUMMARIES[0] ? window.FACILITY_SUMMARIES[0].id : null;

    // Helper: Sort facility list
    function getSortedFacilities() {
        let copy = [...window.FACILITY_SUMMARIES];
        if (currentTabSort === "highest") {
            copy.sort((a, b) => b.rating - a.rating);
        } else if (currentTabSort === "lowest") {
            copy.sort((a, b) => a.rating - b.rating);
        } else if (currentTabSort === "alpha") {
            copy.sort((a, b) => a.name.localeCompare(b.name));
        }
        return copy;
    }

    // ---------------------------------------------------------
    // Function: Render Clickable Facility Tabs
    // ---------------------------------------------------------
    function renderTabs() {
        const sorted = getSortedFacilities();
        tabsBar.innerHTML = sorted.map(fac => {
            const isActive = fac.id === selectedFacilityId;
            const badgeClass = getRatingBadgeClass(fac.rating);
            return `
                <button type="button" 
                        class="facility-tab-btn ${isActive ? 'active' : ''}" 
                        onclick="selectSummaryTab('${fac.id}')">
                    <span>${fac.name}</span>
                    <span class="tab-rating ${badgeClass}">${fac.rating.toFixed(2)}</span>
                </button>
            `;
        }).join("");
    }

    // ---------------------------------------------------------
    // Function: Render Single Facility Presentation Card
    // ---------------------------------------------------------
    function renderSingleCard() {
        const fac = window.FACILITY_SUMMARIES.find(f => f.id === selectedFacilityId);
        if (!fac) {
            singleCard.innerHTML = `<div style="text-align:center; padding:32px; color:var(--text-muted);">No facility summary available.</div>`;
            return;
        }

        const badgeClass = getRatingBadgeClass(fac.rating);
        
        // Render complaint pills
        let complaintsHtml = "";
        if (fac.issues && fac.issues.length > 0) {
            complaintsHtml = fac.issues.map(iss => `
                <span class="complaint-pill">
                    ${iss.category} (${iss.negative_share.toFixed(1)}% negative)
                </span>
            `).join("");
        } else {
            complaintsHtml = `<span class="complaint-pill-none">No recurring issues meeting the 70% negative complaint threshold.</span>`;
        }

        const summaryText = fac.summary && fac.summary.trim() ? fac.summary : "No summary recorded for this facility.";

        singleCard.innerHTML = `
            <div class="summary-card-header">
                <h2 class="summary-facility-title">${fac.name}</h2>
                <div class="summary-rating-badge ${badgeClass}">
                    <span>${fac.rating.toFixed(2)}</span>
                    <span style="font-size:0.85rem; font-weight:500;">/ 5.0</span>
                </div>
            </div>

            <div class="summary-meta-strip">
                <div class="summary-meta-item">
                    <span class="summary-meta-label">Verified Comments</span>
                    <span class="summary-meta-val">${fac.comments_count}</span>
                </div>
                <div class="summary-meta-item">
                    <span class="summary-meta-label">Recurring Problem Areas</span>
                    <span class="summary-meta-val">${fac.issues_count}</span>
                </div>
                <div class="summary-meta-item">
                    <span class="summary-meta-label">Performance Tier</span>
                    <span class="summary-meta-val" style="color:${getRatingColor(fac.rating)};">
                        ${fac.rating >= 2.60 ? 'Good' : (fac.rating >= 2.45 ? 'Moderate' : 'Needs attention')}
                    </span>
                </div>
            </div>

            <div class="complaints-section">
                <div class="complaints-title">Primary student complaint areas:</div>
                <div class="complaint-pills-row">
                    ${complaintsHtml}
                </div>
            </div>

            <div class="summary-text-box">
                <p class="summary-prose">${escapeHtml(summaryText)}</p>
            </div>

            <div class="summary-actions-bar">
                <button type="button" class="btn-copy-summary" onclick="copySummaryText('${fac.id}', this)">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                    <span>Copy summary</span>
                </button>
            </div>
        `;
    }

    // ---------------------------------------------------------
    // Function: Render Compare Mode Cards
    // ---------------------------------------------------------
    function renderCompareView() {
        const idA = compareSelectA.value;
        const idB = compareSelectB.value;

        const facA = window.FACILITY_SUMMARIES.find(f => f.id === idA);
        const facB = window.FACILITY_SUMMARIES.find(f => f.id === idB);
        if (!facA || !facB) return;

        const diff = Math.abs(facA.rating - facB.rating).toFixed(2);
        let badgeA = "";
        let badgeB = "";

        if (facA.rating > facB.rating) {
            badgeA = `<div class="compare-badge-winner">Higher rated facility (+${diff})</div>`;
            badgeB = `<div class="compare-badge-neutral">Rating difference: -${diff}</div>`;
        } else if (facB.rating > facA.rating) {
            badgeB = `<div class="compare-badge-winner">Higher rated facility (+${diff})</div>`;
            badgeA = `<div class="compare-badge-neutral">Rating difference: -${diff}</div>`;
        } else {
            badgeA = `<div class="compare-badge-neutral">Equal rating benchmark</div>`;
            badgeB = `<div class="compare-badge-neutral">Equal rating benchmark</div>`;
        }

        function buildCardHtml(fac, winnerBadge) {
            const badgeClass = getRatingBadgeClass(fac.rating);

            let complaintsHtml = "";
            if (fac.issues && fac.issues.length > 0) {
                complaintsHtml = fac.issues.map(iss => `
                    <span class="complaint-pill" style="font-size:0.78rem; padding:3px 8px;">
                        ${iss.category} (${iss.negative_share.toFixed(1)}%)
                    </span>
                `).join("");
            } else {
                complaintsHtml = `<span class="complaint-pill-none">No recurring issues (&ge; 70% neg).</span>`;
            }

            const summaryText = fac.summary && fac.summary.trim() ? fac.summary : "No summary recorded for this facility.";

            return `
                ${winnerBadge}
                <div class="summary-card-header" style="margin-bottom:12px;">
                    <h3 style="font-size:1.35rem; font-weight:700; color:var(--main-color);">${fac.name}</h3>
                    <div class="summary-rating-badge ${badgeClass}" style="font-size:0.95rem; padding:4px 10px;">
                        ${fac.rating.toFixed(2)}
                    </div>
                </div>

                <div class="summary-meta-strip" style="gap:16px; padding-bottom:12px; margin-bottom:14px;">
                    <div class="summary-meta-item">
                        <span class="summary-meta-label">Comments</span>
                        <span class="summary-meta-val" style="font-size:0.95rem;">${fac.comments_count}</span>
                    </div>
                    <div class="summary-meta-item">
                        <span class="summary-meta-label">Recurring Issues</span>
                        <span class="summary-meta-val" style="font-size:0.95rem;">${fac.issues_count}</span>
                    </div>
                </div>

                <div class="complaints-section" style="margin-bottom:16px;">
                    <div class="complaints-title" style="font-size:0.82rem; margin-bottom:6px;">Main Complaints:</div>
                    <div class="complaint-pills-row">
                        ${complaintsHtml}
                    </div>
                </div>

                <div class="summary-text-box" style="padding:16px; margin-bottom:16px;">
                    <p class="summary-prose" style="font-size:0.96rem; line-height:1.65;">${escapeHtml(summaryText)}</p>
                </div>

                <div class="summary-actions-bar">
                    <button type="button" class="btn-copy-summary" onclick="copySummaryText('${fac.id}', this)">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
                        <span>Copy summary</span>
                    </button>
                </div>
            `;
        }

        cardCompareA.innerHTML = buildCardHtml(facA, badgeA);
        cardCompareB.innerHTML = buildCardHtml(facB, badgeB);
    }

    // ---------------------------------------------------------
    // Event Listeners: Mode Switching
    // ---------------------------------------------------------
    btnModeSingle.addEventListener("click", () => {
        btnModeSingle.classList.add("active");
        btnModeCompare.classList.remove("active");
        singleSection.style.display = "block";
        compareSection.style.display = "none";
        tabSortWrap.style.display = "flex";
    });

    btnModeCompare.addEventListener("click", () => {
        btnModeCompare.classList.add("active");
        btnModeSingle.classList.remove("active");
        singleSection.style.display = "none";
        compareSection.style.display = "block";
        tabSortWrap.style.display = "none";
        renderCompareView();
    });

    // Event Listeners: Tab Sorting
    tabSortButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tabSortButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentTabSort = btn.getAttribute("data-sort");
            renderTabs();
        });
    });

    // Event Listeners: Compare Select Dropdowns
    compareSelectA.addEventListener("change", renderCompareView);
    compareSelectB.addEventListener("change", renderCompareView);

    // Global helper: Select tab
    window.selectSummaryTab = function(facilityId) {
        selectedFacilityId = facilityId;
        renderTabs();
        renderSingleCard();
    };

    // Initial render
    renderTabs();
    renderSingleCard();
}

// Global helper: Copy summary text to clipboard with visual feedback
window.copySummaryText = function(facilityId, btnElement) {
    const fac = window.FACILITY_SUMMARIES ? window.FACILITY_SUMMARIES.find(f => f.id === facilityId) : null;
    if (!fac || !fac.summary) return;

    const textToCopy = fac.summary.trim();

    function showFeedback() {
        if (!btnElement) return;
        const originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = `<span>✓ Copied to clipboard!</span>`;
        btnElement.style.backgroundColor = "var(--rating-good)";
        btnElement.style.color = "#ffffff";
        btnElement.style.borderColor = "var(--rating-good)";

        setTimeout(() => {
            btnElement.innerHTML = originalHtml;
            btnElement.style.backgroundColor = "";
            btnElement.style.color = "";
            btnElement.style.borderColor = "";
        }, 2000);
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textToCopy).then(showFeedback).catch(() => {
            fallbackCopy(textToCopy);
            showFeedback();
        });
    } else {
        fallbackCopy(textToCopy);
        showFeedback();
    }
};

function fallbackCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
}


// -------------------------------------------------------------
// 5. Flagged Comments Page: Policy, Distribution, and Safe Table
// -------------------------------------------------------------
function initFlaggedPage() {
    const tableEl = document.getElementById("flaggedDataTable");
    if (!tableEl || !window.FLAGGED_DATA) return;

    const facilitySelect = document.getElementById("flaggedFacilitySelect");
    const searchInput = document.getElementById("flaggedSearchInput");
    const rowCountEl = document.getElementById("flaggedRowCount");
    const tableBody = document.getElementById("flaggedTableBody");
    const btnResetFacility = document.getElementById("btnResetFacilityFilter");
    const sortableHeaders = document.querySelectorAll("#flaggedDataTable .sortable-th");
    const distCards = document.querySelectorAll(".dist-card");

    let currentSortCol = "bert_score";
    let currentSortAsc = false; // Highest toxicity first by default
    const expandedCommentIds = new Set();

    // ---------------------------------------------------------
    // Function: Render Quarantined Comments Table
    // ---------------------------------------------------------
    function renderTable() {
        const facFilter = facilitySelect ? facilitySelect.value : "all";
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";

        // 1. Filter rows
        let filtered = window.FLAGGED_DATA.filter(row => {
            // Facility filter
            if (facFilter !== "all" && row.facility !== facFilter) return false;

            // Search filter
            if (searchTerm) {
                const matchId = row.id.toLowerCase().includes(searchTerm);
                const matchText = row.text.toLowerCase().includes(searchTerm);
                const matchFac = row.display_facility.toLowerCase().includes(searchTerm);
                if (!matchId && !matchText && !matchFac) return false;
            }

            return true;
        });

        // 2. Sort rows
        filtered.sort((a, b) => {
            let valA = a[currentSortCol];
            let valB = b[currentSortCol];

            if (valA === null || valA === undefined) valA = -999;
            if (valB === null || valB === undefined) valB = -999;

            if (typeof valA === "string") {
                return currentSortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return currentSortAsc ? valA - valB : valB - valA;
        });

        // 3. Render HTML
        if (filtered.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 32px; color: var(--text-muted);">No quarantined comments match the filter or search criteria.</td></tr>';
        } else {
            tableBody.innerHTML = filtered.map(row => {
                const isExpanded = expandedCommentIds.has(row.id);
                const fullText = row.text;
                
                // Truncate to first line or 100 characters for safety
                const firstLine = fullText.split("\n")[0].trim();
                const needsTruncation = fullText.length > 100 || fullText.includes("\n");
                
                let textHtml = "";
                let toggleBtn = "";

                if (needsTruncation) {
                    if (isExpanded) {
                        textHtml = escapeHtml(fullText);
                        toggleBtn = `<br><button type="button" class="btn-toggle-expand" onclick="window.toggleCommentExpand('${row.id}')">Collapse comment &uarr;</button>`;
                    } else {
                        const snippet = firstLine.length > 100 ? firstLine.substring(0, 97) + "..." : firstLine;
                        textHtml = escapeHtml(snippet);
                        toggleBtn = `<br><button type="button" class="btn-toggle-expand" onclick="window.toggleCommentExpand('${row.id}')">Show full comment &darr;</button>`;
                    }
                } else {
                    textHtml = escapeHtml(fullText);
                }

                const scorePercent = (row.bert_score * 100).toFixed(1);

                return `
                    <tr>
                        <td style="font-family: monospace; font-size: 0.85rem; color: var(--text-heading); font-weight: 600;">
                            ${escapeHtml(row.id)}
                        </td>
                        <td>
                            <strong>${escapeHtml(row.display_facility)}</strong>
                        </td>
                        <td>
                            <span class="tox-badge" title="Toxicity confidence: ${row.bert_score.toFixed(3)}">
                                ${row.bert_score.toFixed(3)} (${scorePercent}%)
                            </span>
                        </td>
                        <td>
                            <div class="comment-cell-wrap">
                                <span class="comment-preview-text">${textHtml}</span>
                                ${toggleBtn}
                            </div>
                        </td>
                    </tr>
                `;
            }).join("");
        }

        // 4. Update row count text
        if (rowCountEl) {
            rowCountEl.textContent = `Showing ${filtered.length} of ${window.FLAGGED_DATA.length} flagged comments`;
        }

        // 5. Update header sort indicators
        sortableHeaders.forEach(th => {
            const col = th.getAttribute("data-col");
            const icon = th.querySelector(".sort-icon");
            if (icon) {
                if (col === currentSortCol) {
                    icon.innerHTML = currentSortAsc ? "&uarr;" : "&darr;";
                    th.style.color = "var(--accent-color)";
                } else {
                    icon.innerHTML = "&updownarrow;";
                    th.style.color = "";
                }
            }
        });
    }

    // ---------------------------------------------------------
    // Function: Update Mini Facility Bar Highlight
    // ---------------------------------------------------------
    function updateActiveFacilityCard(facId) {
        distCards.forEach(card => {
            if (card.getAttribute("data-fac") === facId && facId !== "all") {
                card.classList.add("active");
            } else {
                card.classList.remove("active");
            }
        });
    }

    // Global helper: Filter by clicking facility distribution card
    window.filterByFacilityCard = function(facId) {
        if (!facilitySelect) return;
        facilitySelect.value = facId;
        updateActiveFacilityCard(facId);
        renderTable();
    };

    // Global helper: Toggle expand/collapse of individual comment
    window.toggleCommentExpand = function(commentId) {
        if (expandedCommentIds.has(commentId)) {
            expandedCommentIds.delete(commentId);
        } else {
            expandedCommentIds.add(commentId);
        }
        renderTable();
    };

    // Event listener: Reset facility filter
    if (btnResetFacility) {
        btnResetFacility.addEventListener("click", () => {
            if (facilitySelect) facilitySelect.value = "all";
            updateActiveFacilityCard("all");
            renderTable();
        });
    }

    // Event listener: Facility select dropdown change
    if (facilitySelect) {
        facilitySelect.addEventListener("change", () => {
            updateActiveFacilityCard(facilitySelect.value);
            renderTable();
        });
    }

    // Event listener: Search input
    if (searchInput) {
        searchInput.addEventListener("input", renderTable);
    }

    // Event listener: Sortable column headers
    sortableHeaders.forEach(th => {
        th.addEventListener("click", () => {
            const col = th.getAttribute("data-col");
            if (currentSortCol === col) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortCol = col;
                currentSortAsc = col === "bert_score" ? false : true;
            }
            renderTable();
        });
    });

    // Initial render
    renderTable();
}


// -------------------------------------------------------------
// 6. Submit Feedback Page: Real-Time NLP Evaluation
// -------------------------------------------------------------
window.FEEDBACK_EXAMPLES = {
    positive: {
        facility: 'library',
        text: 'The library is very quiet and peaceful with plenty of clean study desks.'
    },
    negative: {
        facility: 'canteen',
        text: 'The food in the canteen is oily, stale and completely cold.'
    },
    mixed: {
        facility: 'classrooms',
        text: 'The projectors in the classrooms work well but the air conditioning is broken and noisy.'
    },
    neutral: {
        facility: 'library',
        text: 'The library hours are posted on the notice board.'
    },
    abusive: {
        facility: 'canteen',
        text: 'The canteen staff are complete idiots and stupid fools.'
    }
};

function initSubmitPage() {
    const form = document.getElementById("feedbackForm");
    if (!form) return;

    const submitFacility = document.getElementById("submitFacility");
    const submitText = document.getElementById("submitText");
    const charCounter = document.getElementById("charCounter");
    const formErrorMessage = document.getElementById("formErrorMessage");
    const btnSubmitAnalyse = document.getElementById("btnSubmitAnalyse");
    const btnSubmitSpinner = document.getElementById("btnSubmitSpinner");
    const btnSubmitText = document.getElementById("btnSubmitText");
    const resultsSection = document.getElementById("resultsSection");
    const metaDetailsBadge = document.getElementById("metaDetailsBadge");
    const truncationNoticeBox = document.getElementById("truncationNoticeBox");
    const quarantineAlertBox = document.getElementById("quarantineAlertBox");
    const quarantineScoreBadge = document.getElementById("quarantineScoreBadge");
    const safeAssessmentBox = document.getElementById("safeAssessmentBox");
    const safeScoreBadge = document.getElementById("safeScoreBadge");
    const aspectsContainer = document.getElementById("aspectsContainer");
    const aspectsCardsGrid = document.getElementById("aspectsCardsGrid");
    const noAspectsBox = document.getElementById("noAspectsBox");

    // Helper: Update character counter
    function updateCharCount() {
        if (!submitText || !charCounter) return;
        const count = submitText.value.length;
        charCounter.textContent = `${count} / 1000 characters`;
        if (count > 1000) {
            charCounter.style.color = "var(--rating-mid)";
            charCounter.style.fontWeight = "700";
        } else {
            charCounter.style.color = "";
            charCounter.style.fontWeight = "";
        }
    }

    if (submitText) {
        submitText.addEventListener("input", updateCharCount);
    }

    // Global helper: Load demo example
    window.loadExample = function(key) {
        if (!window.FEEDBACK_EXAMPLES || !window.FEEDBACK_EXAMPLES[key]) return;
        const ex = window.FEEDBACK_EXAMPLES[key];
        if (submitFacility) submitFacility.value = ex.facility;
        if (submitText) {
            submitText.value = ex.text;
            updateCharCount();
            submitText.focus();
        }
        if (formErrorMessage) formErrorMessage.style.display = "none";
    };

    // Global helper: Clear form
    window.clearFeedbackForm = function() {
        if (submitText) {
            submitText.value = "";
            updateCharCount();
        }
        if (formErrorMessage) formErrorMessage.style.display = "none";
        if (resultsSection) resultsSection.style.display = "none";
    };

    // Global helper: Submit analysis
    window.handleFeedbackSubmit = async function(e) {
        if (e) e.preventDefault();

        const rawText = submitText ? submitText.value.trim() : "";
        if (!rawText) {
            if (formErrorMessage) {
                formErrorMessage.textContent = "Please enter a student feedback comment before analysing.";
                formErrorMessage.style.display = "block";
            }
            if (resultsSection) resultsSection.style.display = "none";
            return;
        }

        if (formErrorMessage) formErrorMessage.style.display = "none";

        // Set button loading state
        if (btnSubmitSpinner) btnSubmitSpinner.style.display = "inline-block";
        if (btnSubmitText) btnSubmitText.textContent = "Analysing with NLP models...";
        if (btnSubmitAnalyse) btnSubmitAnalyse.disabled = true;

        try {
            const payload = {
                facility: submitFacility ? submitFacility.value : "canteen",
                text: rawText
            };

            const response = await fetch("/api/analyse", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!data.success) {
                if (formErrorMessage) {
                    formErrorMessage.textContent = data.error || "An error occurred during model analysis.";
                    formErrorMessage.style.display = "block";
                }
                if (resultsSection) resultsSection.style.display = "none";
                return;
            }

            // Analysis Success: Populate Results Section
            if (resultsSection) resultsSection.style.display = "block";

            // Metadata pill
            if (metaDetailsBadge) {
                metaDetailsBadge.textContent = `${data.facility_name} • ${data.char_count} chars`;
            }

            // Truncation Notice
            if (truncationNoticeBox) {
                if (data.truncated) {
                    truncationNoticeBox.innerHTML = `<strong>Note:</strong> Your comment exceeded 1,000 characters (${data.char_count} characters entered). It was automatically truncated to the first 1,000 characters for analysis.`;
                    truncationNoticeBox.style.display = "block";
                } else {
                    truncationNoticeBox.style.display = "none";
                }
            }

            // Moderation: Abusive vs Safe
            if (data.abusive) {
                if (quarantineAlertBox) quarantineAlertBox.style.display = "block";
                if (quarantineScoreBadge) {
                    quarantineScoreBadge.textContent = `Toxicity score: ${data.toxicity_score.toFixed(3)} (${data.toxicity_pct}%)`;
                }
                if (safeAssessmentBox) safeAssessmentBox.style.display = "none";
                if (aspectsContainer) aspectsContainer.style.display = "none";
                if (noAspectsBox) noAspectsBox.style.display = "none";
            } else {
                if (quarantineAlertBox) quarantineAlertBox.style.display = "none";
                if (safeAssessmentBox) safeAssessmentBox.style.display = "block";
                if (safeScoreBadge) {
                    safeScoreBadge.textContent = `Toxicity score: ${data.toxicity_score.toFixed(3)} (Safe)`;
                }

                // Aspect Sentiment Topics
                if (data.aspects && data.aspects.length > 0) {
                    if (aspectsContainer) aspectsContainer.style.display = "block";
                    if (noAspectsBox) noAspectsBox.style.display = "none";

                    if (aspectsCardsGrid) {
                        aspectsCardsGrid.innerHTML = data.aspects.map(a => {
                            let badgeClass = "badge-sentiment-neu";
                            let badgeLabel = "Neutral";
                            if (a.sentiment === "positive") {
                                badgeClass = "badge-sentiment-pos";
                                badgeLabel = "Positive";
                            } else if (a.sentiment === "negative") {
                                badgeClass = "badge-sentiment-neg";
                                badgeLabel = "Negative";
                            }

                            const clauseHtml = a.clause ? `
                                <div class="aspect-clause-quote">
                                    &ldquo;${escapeHtml(a.clause)}&rdquo;
                                </div>
                            ` : "";

                            const termHtml = a.aspect_term ? `
                                <div class="aspect-keyword-meta">
                                    Identified term: <strong>${escapeHtml(a.aspect_term)}</strong>
                                </div>
                            ` : `<div class="aspect-keyword-meta" style="color:var(--accent-color);">Inferred by DistilBERT model</div>`;

                            return `
                                <div class="aspect-card">
                                    <div class="aspect-card-header">
                                        <span class="aspect-topic-name">${escapeHtml(a.category)}</span>
                                        <span class="${badgeClass}">${badgeLabel}</span>
                                    </div>
                                    ${clauseHtml}
                                    ${termHtml}
                                </div>
                            `;
                        }).join("");
                    }
                } else {
                    if (aspectsContainer) aspectsContainer.style.display = "none";
                    if (noAspectsBox) noAspectsBox.style.display = "block";
                }
            }

            // Scroll down smoothly to results
            if (resultsSection) {
                resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }

        } catch (err) {
            if (formErrorMessage) {
                formErrorMessage.textContent = "Could not communicate with the analysis server. Please ensure the web application is running.";
                formErrorMessage.style.display = "block";
            }
        } finally {
            if (btnSubmitSpinner) btnSubmitSpinner.style.display = "none";
            if (btnSubmitText) btnSubmitText.textContent = "Analyse comment";
            if (btnSubmitAnalyse) btnSubmitAnalyse.disabled = false;
        }
    };
}
