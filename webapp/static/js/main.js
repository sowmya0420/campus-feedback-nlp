/**
 * Campus Facility Feedback Analysis System - Dark Dashboard Interactive Logic
 * Offline Chart.js implementation and multi-stage live NLP demo pipeline.
 */

// Set global Chart.js typography and dark palette styling
if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    Chart.defaults.color = "#9aa3b0";
    Chart.defaults.borderColor = "#2b303a";
}

document.addEventListener("DOMContentLoaded", () => {
    // 0. Initialize Generic Inner Tabs across all pages
    initInnerTabs();

    // 1. Initialize Facility Explorer if present
    initExplorerPage();

    // 2. Initialize Live Demo components if present
    initLiveDemo();

    // 3. Initialize Ratings page components if present
    initRatingsPage();

    // 4. Initialize Recurring Issues page components if present
    initIssuesPage();

    // 5. Initialize Summaries / Briefs page components if present
    initSummariesPage();

    // 6. Initialize Flagged / Abusive Content page components if present
    initFlaggedPage();
});

// -------------------------------------------------------------
// Helper: Rating Tier Colors (Dark palette rules)
// Green (>= 2.60): Good (#4ade80)
// Amber (2.45 - 2.59): Moderate (#fbbf24)
// Red (< 2.45): Needs Attention (#f87171)
// -------------------------------------------------------------
function getRatingColor(rating) {
    if (rating >= 2.60) return "#4ade80";
    if (rating >= 2.45) return "#fbbf24";
    return "#f87171";
}

function getRatingBadgeClass(rating) {
    if (rating >= 2.60) return "badge-pos";
    if (rating >= 2.45) return "badge-neu";
    return "badge-neg";
}

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

// Helper: Draw Star Rating with clean outline/filled SVGs
function renderStarsHtml(stars) {
    const filledStar = `<svg class="star-svg star-filled" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
    const emptyStar = `<svg class="star-svg star-empty" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
    
    let html = '<div class="star-rating-cell">';
    for (let i = 1; i <= 5; i++) {
        html += (i <= stars) ? filledStar : emptyStar;
    }
    html += '<span class="rating-est-label">estimated from sentiment</span>';
    html += '</div>';
    return html;
}

// =============================================================
// GENERIC INNER TABS (For single-screen compact card views)
// =============================================================
function initInnerTabs() {
    const tabBars = document.querySelectorAll(".inner-tabs-bar");
    tabBars.forEach(bar => {
        const buttons = bar.querySelectorAll(".btn-inner-tab");
        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                const targetTab = btn.getAttribute("data-tab");
                if (!targetTab) return;

                buttons.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");

                const container = bar.closest(".page-container") || document;
                const panels = container.querySelectorAll(".inner-tab-panel");
                panels.forEach(p => {
                    if (p.id === `tabPanel-${targetTab}`) {
                        p.style.display = "block";
                    } else {
                        p.style.display = "none";
                    }
                });

                if (typeof ratingsChartInstance !== "undefined" && ratingsChartInstance) {
                    ratingsChartInstance.resize();
                }
                if (typeof issuesChartInstance !== "undefined" && issuesChartInstance) {
                    issuesChartInstance.resize();
                }
            });
        });
    });
}

// =============================================================
// 1. FACILITY EXPLORER
// =============================================================
let explorerChartInstance = null;

function initExplorerPage() {
    const select = document.getElementById("explorerFacilitySelect");
    if (!select || !window.EXPLORER_DATA) return;

    const facRating = document.getElementById("facRating");
    const facBadge = document.getElementById("facBadge");
    const facStatus = document.getElementById("facStatus");
    const facComments = document.getElementById("facComments");
    const facTopIssue = document.getElementById("facTopIssue");
    const facIssuesCount = document.getElementById("facIssuesCount");
    const chartCardTitle = document.getElementById("chartCardTitle");
    const aspectList = document.getElementById("explorerAspectList");
    const aspectCountHint = document.getElementById("aspectCountHint");
    const chartCanvas = document.getElementById("explorerChart");

    function renderFacility(facId) {
        const fac = window.EXPLORER_DATA.find(f => f.id === facId) || window.EXPLORER_DATA[0];
        if (!fac) return;

        if (facRating) facRating.textContent = fac.rating.toFixed(2);
        if (facBadge) {
            facBadge.textContent = `${fac.rating.toFixed(2)} / 5.0`;
            facBadge.className = `rating-badge ${getRatingBadgeClass(fac.rating)}`;
        }
        if (facStatus) facStatus.textContent = `Status: ${fac.status}`;
        if (facComments) facComments.textContent = `${fac.comments_count} comments`;
        if (facTopIssue) facTopIssue.textContent = fac.top_issue;
        if (facIssuesCount) facIssuesCount.textContent = `${fac.issues_count} recurring`;

        if (chartCardTitle) chartCardTitle.textContent = `${fac.name}: Aspect Sentiment Ratings`;
        if (aspectCountHint) aspectCountHint.textContent = `${fac.aspects ? fac.aspects.length : 0} detected aspects`;

        // Render aspect breakdown list
        if (aspectList && fac.aspects) {
            if (fac.aspects.length === 0) {
                aspectList.innerHTML = `<div style="padding: 16px; color: var(--text-muted); text-align: center;">No specific aspect ratings available.</div>`;
            } else {
                aspectList.innerHTML = fac.aspects.map(asp => `
                    <div class="aspect-scroll-item">
                        <div class="aspect-scroll-header">
                            <span class="aspect-item-title">${escapeHtml(asp.category)}</span>
                            <span class="${getRatingBadgeClass(asp.rating)}">${asp.rating.toFixed(2)}</span>
                        </div>
                        <div class="aspect-scroll-meta">
                            <span>${asp.mentions} mentions</span>
                        </div>
                    </div>
                `).join("");
            }
        }

        // Render small horizontal bar chart with Chart.js
        if (chartCanvas && fac.aspects && fac.aspects.length > 0) {
            const labels = fac.aspects.map(a => a.category);
            const values = fac.aspects.map(a => a.rating);
            const colors = fac.aspects.map(a => getRatingColor(a.rating));

            if (!explorerChartInstance) {
                explorerChartInstance = new Chart(chartCanvas, {
                    type: "bar",
                    data: {
                        labels: labels,
                        datasets: [{
                            label: "Rating",
                            data: values,
                            backgroundColor: colors,
                            borderRadius: 4,
                            barThickness: labels.length > 6 ? 16 : 24
                        }]
                    },
                    options: {
                        indexAxis: "y",
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: { duration: 250 },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: "#1f232b",
                                borderColor: "#2b303a",
                                borderWidth: 1,
                                titleColor: "#e8eaed",
                                bodyColor: "#9aa3b0",
                                callbacks: {
                                    label: function(ctx) {
                                        const asp = fac.aspects[ctx.dataIndex];
                                        return [` Rating: ${ctx.parsed.x.toFixed(2)} / 5.0`, ` Mentions: ${asp.mentions}`];
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                min: 1.0,
                                max: 4.0,
                                ticks: {
                                    stepSize: 0.5,
                                    color: "#9aa3b0",
                                    callback: function(v) { return v.toFixed(1); }
                                },
                                grid: { color: "#2b303a" }
                            },
                            y: {
                                ticks: { color: "#9aa3b0", font: { weight: "600" } },
                                grid: { display: false }
                            }
                        }
                    }
                });
            } else {
                explorerChartInstance.data.labels = labels;
                explorerChartInstance.data.datasets[0].data = values;
                explorerChartInstance.data.datasets[0].backgroundColor = colors;
                explorerChartInstance.data.datasets[0].barThickness = labels.length > 6 ? 16 : 24;
                explorerChartInstance.update();
            }
        }
    }

    select.addEventListener("change", () => renderFacility(select.value));
    renderFacility(select.value);
}

// =============================================================
// LIVE DEMO: Six-Stage Pipeline Inference & Ollama Summary
// =============================================================
window.DEMO_EXAMPLES = {
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

function initLiveDemo() {
    const form = document.getElementById("demoFeedbackForm") || document.getElementById("feedbackForm");
    if (!form) return;

    const demoFacility = document.getElementById("demoFacility") || document.getElementById("submitFacility");
    const demoCommentText = document.getElementById("demoCommentText") || document.getElementById("submitText");
    const demoCharCounter = document.getElementById("demoCharCounter") || document.getElementById("charCounter");
    const demoFormError = document.getElementById("demoFormError") || document.getElementById("formErrorMessage");
    const btnAnalyse = document.getElementById("btnAnalyse") || document.getElementById("btnSubmitAnalyse");
    const btnAnalyseSpinner = document.getElementById("btnAnalyseSpinner") || document.getElementById("btnSubmitSpinner");
    const btnAnalyseText = document.getElementById("btnAnalyseText") || document.getElementById("btnSubmitText");

    const emptyPlaceholder = document.getElementById("emptyPlaceholder");
    const resultsContent = document.getElementById("resultsContent") || document.getElementById("resultsSection");
    const checkCleanBox = document.getElementById("checkCleanBox");
    const checkCleanScore = document.getElementById("checkCleanScore");
    const checkAbusiveBox = document.getElementById("checkAbusiveBox");
    const checkAbusiveScore = document.getElementById("checkAbusiveScore");
    const cleanResultsSection = document.getElementById("cleanResultsSection");
    const aspectsTableBody = document.getElementById("aspectsTableBody");
    const noAspectsMessage = document.getElementById("noAspectsMessage");
    const summaryCard = document.getElementById("summaryCard");
    const summarySourceBadge = document.getElementById("summarySourceBadge");
    const summaryLoading = document.getElementById("summaryLoading");
    const summaryText = document.getElementById("summaryText");

    // Live character count listener
    function updateCounter() {
        if (!demoCommentText || !demoCharCounter) return;
        const len = demoCommentText.value.length;
        demoCharCounter.textContent = `${len} / 1000 characters`;
        if (len >= 1000) {
            demoCharCounter.style.color = "var(--sentiment-neu)";
        } else {
            demoCharCounter.style.color = "";
        }
    }

    if (demoCommentText) {
        demoCommentText.addEventListener("input", updateCounter);
    }

    // Step strip controller
    function resetStepStrip() {
        for (let i = 1; i <= 6; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.className = (i === 1) ? "step-item active" : "step-item";
            }
            const conn = document.getElementById(`conn${i}`);
            if (conn) {
                conn.className = "step-connector";
            }
        }
    }

    function setStepState(stepNum, state) {
        const step = document.getElementById(`step${stepNum}`);
        if (!step) return;
        if (state === "active") {
            step.className = "step-item active";
        } else if (state === "complete") {
            step.className = "step-item complete";
        } else if (state === "flagged") {
            step.className = "step-item flagged-abusive";
        } else {
            step.className = "step-item";
        }
    }

    function setConnActive(connNum) {
        const conn = document.getElementById(`conn${connNum}`);
        if (conn) conn.classList.add("active");
    }

    // Quick example loader
    window.loadDemoExample = function(key) {
        if (!window.DEMO_EXAMPLES || !window.DEMO_EXAMPLES[key]) return;
        const ex = window.DEMO_EXAMPLES[key];
        if (demoFacility) demoFacility.value = ex.facility;
        if (demoCommentText) {
            demoCommentText.value = ex.text;
            updateCounter();
            demoCommentText.focus();
        }
        if (demoFormError) demoFormError.style.display = "none";
    };
    window.loadExample = window.loadDemoExample;

    // Clear form helper
    window.clearDemoForm = function() {
        if (demoCommentText) {
            demoCommentText.value = "";
            updateCounter();
        }
        if (demoFormError) demoFormError.style.display = "none";
        if (emptyPlaceholder) emptyPlaceholder.style.display = "flex";
        if (resultsContent) resultsContent.style.display = "none";
        resetStepStrip();
    };
    window.clearFeedbackForm = window.clearDemoForm;

    // Submit handler
    window.handleDemoSubmit = async function(e) {
        if (e) e.preventDefault();

        const rawText = demoCommentText ? demoCommentText.value.trim() : "";
        if (!rawText) {
            if (demoFormError) {
                demoFormError.textContent = "Please enter a comment to analyse.";
                demoFormError.style.display = "block";
            }
            return;
        }

        if (demoFormError) demoFormError.style.display = "none";

        // Loading state
        if (btnAnalyseSpinner) btnAnalyseSpinner.style.display = "inline-block";
        if (btnAnalyseText) btnAnalyseText.textContent = "Analysing...";
        if (btnAnalyse) btnAnalyse.disabled = true;

        // Reset step strip & start stage progression
        resetStepStrip();
        setStepState(1, "complete");
        setConnActive(1);
        setStepState(2, "active");

        try {
            const facility = demoFacility ? demoFacility.value : "library";

            // Stage 1 & 2: Real-time Toxicity and Aspect Analysis
            const resp = await fetch("/api/analyse", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ facility: facility, text: rawText })
            });

            const data = await resp.json();

            if (!data.success) {
                if (demoFormError) {
                    demoFormError.textContent = data.error || "An error occurred during analysis.";
                    demoFormError.style.display = "block";
                }
                resetStepStrip();
                return;
            }

            // Reveal results content area
            if (emptyPlaceholder) emptyPlaceholder.style.display = "none";
            if (resultsContent) resultsContent.style.display = "flex";

            if (data.abusive) {
                // Abusive comment: STOP strip at stage 2 and mark it red
                setStepState(2, "flagged");
                
                // Show abusive result box
                if (checkAbusiveBox) {
                    checkAbusiveBox.style.display = "flex";
                    if (checkAbusiveScore) {
                        checkAbusiveScore.textContent = `Toxicity score: ${data.toxicity_score_display || data.toxicity_score.toFixed(3)}`;
                    }
                }
                if (checkCleanBox) checkCleanBox.style.display = "none";
                if (cleanResultsSection) cleanResultsSection.style.display = "none";

            } else {
                // Clean comment: Complete stage 2 and proceed through stages 3, 4, 5
                setStepState(2, "complete");
                setConnActive(2);

                // Calm sequential lighting of stages
                await new Promise(r => setTimeout(r, 120));
                setStepState(3, "complete");
                setConnActive(3);

                await new Promise(r => setTimeout(r, 120));
                setStepState(4, "complete");
                setConnActive(4);

                await new Promise(r => setTimeout(r, 120));
                setStepState(5, "complete");
                setConnActive(5);

                setStepState(6, "active");

                // Show clean check box
                if (checkCleanBox) {
                    checkCleanBox.style.display = "flex";
                    if (checkCleanScore) {
                        checkCleanScore.textContent = `Toxicity score: ${data.toxicity_score_display || data.toxicity_score.toFixed(3)}`;
                    }
                }
                if (checkAbusiveBox) checkAbusiveBox.style.display = "none";
                if (cleanResultsSection) cleanResultsSection.style.display = "block";

                // Toggle honest disclaimer and header note
                const allFacDisclaimer = document.getElementById("allFacDisclaimer");
                if (allFacDisclaimer) {
                    allFacDisclaimer.style.display = (data.is_all_mode && data.has_topics) ? "block" : "none";
                }
                const tableHeaderNote = document.getElementById("tableHeaderNote");
                if (tableHeaderNote) {
                    tableHeaderNote.textContent = data.is_all_mode ? "Grouped by facility & aspect" : "One row per detected aspect";
                }

                // Render aspects table (one row per aspect group)
                const hasGroups = data.aspect_groups && data.aspect_groups.length > 0;
                if (hasGroups) {
                    if (aspectsTableBody) {
                        aspectsTableBody.innerHTML = data.aspect_groups.map(grp => {
                            let badgeClass = "badge-neu";
                            if (grp.sentiment === "positive") {
                                badgeClass = "badge-pos";
                            } else if (grp.sentiment === "negative") {
                                badgeClass = "badge-neg";
                            } else if (grp.sentiment === "mixed") {
                                badgeClass = "badge-mixed";
                            }

                            const facTagHtml = data.is_all_mode ? `
                                <div class="facility-tag-row">
                                    <span class="facility-tag">${escapeHtml(grp.facility_display)}</span>
                                    ${grp.facility_note ? `<span class="facility-subnote">(${escapeHtml(grp.facility_note)})</span>` : ''}
                                </div>
                            ` : "";

                            return `
                                <tr>
                                    <td>
                                        ${facTagHtml}
                                        <span class="aspect-cell-title">${escapeHtml(grp.display_category)}</span>
                                        ${grp.evidence ? `<span class="aspect-evidence">${escapeHtml(grp.evidence)}</span>` : ''}
                                    </td>
                                    <td>
                                        <span class="${badgeClass}">${escapeHtml(grp.badge_label)}</span>
                                    </td>
                                    <td>
                                        ${renderStarsHtml(grp.stars || 3)}
                                    </td>
                                </tr>
                            `;
                        }).join("");
                    }
                    if (noAspectsMessage) noAspectsMessage.style.display = "none";
                    if (summaryCard) summaryCard.style.display = "block";
                } else {
                    if (aspectsTableBody) aspectsTableBody.innerHTML = "";
                    if (noAspectsMessage) noAspectsMessage.style.display = "block";
                    if (allFacDisclaimer) allFacDisclaimer.style.display = "none";
                    if (summaryCard) summaryCard.style.display = "none";
                }

                if (hasGroups) {
                    // Show summary loading indicator while model works
                    if (summaryLoading) summaryLoading.style.display = "flex";
                    if (summaryText) {
                        summaryText.style.display = "none";
                        summaryText.textContent = "";
                    }
                    if (summarySourceBadge) {
                        summarySourceBadge.textContent = "Writing summary...";
                        summarySourceBadge.className = "summary-badge";
                    }

                    // Stage 6: Call Ollama Live Summary API
                    try {
                        const sumResp = await fetch("/api/summarize-live", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                facility: facility,
                                text: rawText,
                                aspect_groups: data.aspect_groups,
                                abusive: data.abusive
                            })
                        });

                        const sumData = await sumResp.json();
                        
                        if (summaryLoading) summaryLoading.style.display = "none";
                        if (summaryText) {
                            summaryText.textContent = sumData.summary || "No summary could be generated.";
                            summaryText.style.display = "block";
                        }
                        if (summarySourceBadge) {
                            summarySourceBadge.textContent = sumData.label || "AI summary (local model)";
                            if (sumData.source === "ollama") {
                                summarySourceBadge.className = "summary-badge ai-badge";
                            } else {
                                summarySourceBadge.className = "summary-badge";
                            }
                        }
                        setStepState(6, "complete");

                    } catch (sumErr) {
                        if (summaryLoading) summaryLoading.style.display = "none";
                        if (summaryText) {
                            summaryText.textContent = "Student feedback was evaluated across detected campus facilities.";
                            summaryText.style.display = "block";
                        }
                        if (summarySourceBadge) {
                            summarySourceBadge.textContent = "Auto-generated from detected aspects";
                            summarySourceBadge.className = "summary-badge";
                        }
                        setStepState(6, "complete");
                    }
                } else {
                    setStepState(6, "complete");
                }
            }

        } catch (err) {
            if (demoFormError) {
                demoFormError.textContent = "Could not communicate with the analysis server. Please ensure the web application is running.";
                demoFormError.style.display = "block";
            }
            resetStepStrip();
        } finally {
            if (btnAnalyseSpinner) btnAnalyseSpinner.style.display = "none";
            if (btnAnalyseText) btnAnalyseText.textContent = "Analyse comment";
            if (btnAnalyse) btnAnalyse.disabled = false;
        }
    };
    window.handleFeedbackSubmit = window.handleDemoSubmit;
}

// =============================================================
// 4. Aspect-wise Ratings Page: Chart & Sortable Data Table
// =============================================================
let ratingsChartInstance = null;

function initRatingsPage() {
    const chartCtx = document.getElementById("ratingsChart");
    const tableBody = document.getElementById("ratingsTableBody");
    if (!chartCtx || !tableBody || !window.RATINGS_DATA) return;

    let currentSortColumn = "rating";
    let currentSortAsc = false;

    const btnModeOverall = document.getElementById("btnModeOverall");
    const btnModeTopics = document.getElementById("btnModeTopics");
    const facilitySelect = document.getElementById("facilitySelect");
    const topicSelect = document.getElementById("topicSelect");
    const topicSelectWrap = document.getElementById("topicSelectWrap");
    const searchInput = document.getElementById("ratingsTableSearch");
    const tableRowCount = document.getElementById("tableRowCount");
    const chartHeaderTitle = document.getElementById("chartHeaderTitle");
    const chartHeaderDesc = document.getElementById("chartHeaderDesc");

    let activeMode = "overall";

    function renderTable() {
        const facFilter = facilitySelect.value;
        const topFilter = topicSelect.value;
        const searchTerm = searchInput.value.toLowerCase().trim();

        let filtered = window.RATINGS_DATA.filter(row => {
            if (activeMode === "overall" && !row.is_overall) return false;
            if (activeMode === "topics" && row.is_overall) return false;

            if (facFilter !== "all" && row.facility !== facFilter) return false;
            if (topFilter !== "all" && row.category !== topFilter) return false;

            if (searchTerm) {
                const matchFac = row.display_facility.toLowerCase().includes(searchTerm);
                const matchCat = row.category.toLowerCase().includes(searchTerm);
                if (!matchFac && !matchCat) return false;
            }
            return true;
        });

        filtered.sort((a, b) => {
            let valA = a[currentSortColumn];
            let valB = b[currentSortColumn];

            if (valA === null || valA === undefined) valA = -999;
            if (valB === null || valB === undefined) valB = -999;

            if (typeof valA === "string") {
                return currentSortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return currentSortAsc ? valA - valB : valB - valA;
        });

        if (filtered.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 32px; color: var(--text-muted);">No matching rating records found.</td></tr>`;
        } else {
            tableBody.innerHTML = filtered.map(row => {
                const ratingBadge = `<span class="${getRatingBadgeClass(row.rating)}">${row.rating.toFixed(2)}</span>`;
                const catDisplay = row.is_overall ? `<span class="badge-neu" style="letter-spacing:0.04em;">OVERALL</span>` : row.category;
                const posDisplay = row.positive !== null ? row.positive : `<span style="color:var(--text-muted);">—</span>`;
                const neuDisplay = row.neutral !== null ? row.neutral : `<span style="color:var(--text-muted);">—</span>`;
                const negDisplay = row.negative !== null ? row.negative : `<span style="color:var(--text-muted);">—</span>`;
                const shareDisplay = row.negative_share !== null ? `${row.negative_share.toFixed(1)}%` : `<span style="color:var(--text-muted);">—</span>`;

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

        if (tableRowCount) {
            tableRowCount.textContent = `Showing ${filtered.length} of ${window.RATINGS_DATA.length} records`;
        }
    }

    function updateChart() {
        const facFilter = facilitySelect.value;
        const topFilter = topicSelect.value;
        const benchmark = window.CAMPUS_AVG || 2.54;

        let chartItems = [];

        if (activeMode === "overall") {
            let ovRows = window.RATINGS_DATA.filter(r => r.is_overall);
            if (facFilter !== "all") {
                ovRows = ovRows.filter(r => r.facility === facFilter);
            }
            ovRows.sort((a, b) => b.rating - a.rating);
            chartItems = ovRows.map(r => ({ label: r.display_facility, rating: r.rating, mentions: r.mentions, share: r.negative_share }));

            if (chartHeaderTitle) chartHeaderTitle.textContent = "Overall Facility Ratings";
            if (chartHeaderDesc) chartHeaderDesc.textContent = "Facility-level scores on a 1.0 to 5.0 scale. The dashed line marks the campus benchmark (2.54).";
        } else {
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
                            borderColor: "#fb923c",
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
                            backgroundColor: "#1f232b",
                            borderColor: "#2b303a",
                            borderWidth: 1,
                            titleColor: "#e8eaed",
                            bodyColor: "#9aa3b0",
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
                                color: "#9aa3b0",
                                callback: function(val) { return val.toFixed(1); }
                            },
                            grid: { color: "#2b303a" }
                        },
                        x: {
                            ticks: {
                                font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
                                color: "#9aa3b0",
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

    if (btnModeOverall) {
        btnModeOverall.addEventListener("click", () => {
            btnModeOverall.classList.add("active");
            btnModeTopics.classList.remove("active");
            activeMode = "overall";
            if (topicSelectWrap) topicSelectWrap.style.display = "none";
            renderTable();
            updateChart();
        });
    }

    if (btnModeTopics) {
        btnModeTopics.addEventListener("click", () => {
            btnModeTopics.classList.add("active");
            btnModeOverall.classList.remove("active");
            activeMode = "topics";
            if (topicSelectWrap) topicSelectWrap.style.display = "inline-flex";
            renderTable();
            updateChart();
        });
    }

    if (facilitySelect) {
        facilitySelect.addEventListener("change", () => {
            if (facilitySelect.value !== "all" && activeMode === "overall") {
                if (btnModeTopics) btnModeTopics.click();
            } else {
                renderTable();
                updateChart();
            }
        });
    }

    if (topicSelect) {
        topicSelect.addEventListener("change", () => {
            renderTable();
            updateChart();
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", renderTable);
    }

    const sortableHeaders = document.querySelectorAll(".sortable-th");
    sortableHeaders.forEach(th => {
        th.addEventListener("click", () => {
            const col = th.getAttribute("data-col");
            if (currentSortColumn === col) {
                currentSortAsc = !currentSortAsc;
            } else {
                currentSortColumn = col;
                currentSortAsc = (col === "display_facility" || col === "category");
            }
            renderTable();
        });
    });

    renderTable();
    updateChart();
}

// =============================================================
// 5. Recurring Issues Page: Horizontal Bar Chart & List
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

    function getSeverityProps(share) {
        if (share >= 85.0) {
            return { color: "#f87171", pillClass: "badge-neg", label: "High severity" };
        } else if (share >= 75.0) {
            return { color: "#fbbf24", pillClass: "badge-neu", label: "Moderate severity" };
        }
        return { color: "#fb923c", pillClass: "badge-neu", label: "Notable severity" };
    }

    function getProcessedIssues() {
        const facFilter = facilitySelect.value;
        const minThreshold = parseFloat(severitySlider.value);
        const sortMode = sortSelect.value;

        let filtered = window.ISSUES_DATA.filter(item => {
            if (facFilter !== "all" && item.facility !== facFilter) return false;
            if (item.negative_share < minThreshold) return false;
            return true;
        });

        filtered.sort((a, b) => {
            if (sortMode === "neg_share") return b.negative_share - a.negative_share;
            if (sortMode === "mentions") return b.mentions - a.mentions;
            if (sortMode === "rating") return a.rating - b.rating;
            return 0;
        });

        return filtered;
    }

    function renderIssuesList(issues) {
        if (issuesRowCount) {
            issuesRowCount.textContent = `Showing ${issues.length} of ${window.ISSUES_DATA.length} recurring issues`;
        }

        if (issues.length === 0) {
            issuesContainer.innerHTML = `
                <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:32px 20px; text-align:center; color:var(--text-muted);">
                    No recurring issues meet the selected facility or severity threshold criteria.
                </div>
            `;
            return;
        }

        issuesContainer.innerHTML = issues.map((issue, index) => {
            const sev = getSeverityProps(issue.negative_share);
            
            let quotesHtml = "";
            if (issue.comments && issue.comments.length > 0) {
                quotesHtml = issue.comments.map(c => `
                    <div style="padding:8px 10px; background:var(--bg-raised); border-radius:var(--radius-sm); margin-bottom:6px; font-size:0.82rem; color:var(--text-primary); border:1px solid var(--border);">
                        &ldquo;${escapeHtml(c)}&rdquo;
                    </div>
                `).join("");
            } else {
                quotesHtml = `<div style="font-size:0.8rem; color:var(--text-muted);">No non-abusive negative comments recorded for this issue.</div>`;
            }

            return `
                <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:12px 14px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="toggleIssueRow(${index})">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="badge-neu">${issue.display_facility}</span>
                            <strong style="color:var(--text-primary); font-size:0.9rem;">${issue.category}</strong>
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="${sev.pillClass}">${issue.negative_share.toFixed(1)}% negative</span>
                            <span style="font-size:0.8rem; color:var(--text-muted);">${issue.mentions} mentions</span>
                            <span class="${getRatingBadgeClass(issue.rating)}">${issue.rating.toFixed(2)}</span>
                            <span style="font-size:0.75rem; color:var(--accent);" id="expandBtnText-${index}">▼</span>
                        </div>
                    </div>
                    <div id="issueDrawer-${index}" style="display:none; margin-top:10px; padding-top:10px; border-top:1px solid var(--border);">
                        ${quotesHtml}
                    </div>
                </div>
            `;
        }).join("");
    }

    function updateIssuesChart(issues) {
        const facFilter = facilitySelect.value;
        const facName = facFilter !== "all" ? facilitySelect.options[facilitySelect.selectedIndex].text : "All Facilities";

        if (chartTitle) chartTitle.textContent = `${facName}: Recurring Issues Ranked by Severity`;
        if (chartDesc) chartDesc.textContent = `Showing ${issues.length} recurring issues with a negative share of at least ${severitySlider.value}%.`;

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
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 250 },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: "#1f232b",
                            borderColor: "#2b303a",
                            borderWidth: 1,
                            titleColor: "#e8eaed",
                            bodyColor: "#9aa3b0",
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
                                color: "#9aa3b0",
                                callback: function(val) { return val + "%"; }
                            },
                            grid: { color: "#2b303a" }
                        },
                        y: {
                            ticks: {
                                font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
                                color: "#9aa3b0"
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

    refreshView();
}

window.toggleIssueRow = function(index) {
    const drawer = document.getElementById(`issueDrawer-${index}`);
    const btnText = document.getElementById(`expandBtnText-${index}`);
    if (!drawer) return;

    if (drawer.style.display === "none") {
        drawer.style.display = "block";
        if (btnText) btnText.textContent = "▲";
    } else {
        drawer.style.display = "none";
        if (btnText) btnText.textContent = "▼";
    }
};

// =============================================================
// 6. Summaries / Facility Briefs Page
// =============================================================
function initSummariesPage() {
    const singleSection = document.getElementById("singleFacilitySection");
    const compareSection = document.getElementById("compareFacilitySection");
    const tabsBar = document.getElementById("facilityTabsBar");
    const singleCard = document.getElementById("singleSummaryCard");
    if (!singleSection || !compareSection || !tabsBar || !singleCard || !window.FACILITY_SUMMARIES) return;

    const btnModeSingle = document.getElementById("btnModeSingle");
    const btnModeCompare = document.getElementById("btnModeCompare");
    const tabSortButtons = document.querySelectorAll("#tabSortGroup .btn-sort");
    let currentTabSort = "highest";
    let selectedFacilityId = window.FACILITY_SUMMARIES[0] ? window.FACILITY_SUMMARIES[0].id : null;

    function getSortedFacilities() {
        let copy = [...window.FACILITY_SUMMARIES];
        if (currentTabSort === "highest") copy.sort((a, b) => b.rating - a.rating);
        else if (currentTabSort === "lowest") copy.sort((a, b) => a.rating - b.rating);
        else if (currentTabSort === "alpha") copy.sort((a, b) => a.name.localeCompare(b.name));
        return copy;
    }

    const compareSelectA = document.getElementById("compareSelectA");
    const compareSelectB = document.getElementById("compareSelectB");
    const cardCompareA = document.getElementById("cardCompareA");
    const cardCompareB = document.getElementById("cardCompareB");

    function renderTabs() {
        const sorted = getSortedFacilities();
        tabsBar.innerHTML = sorted.map(fac => {
            const isActive = fac.id === selectedFacilityId;
            return `
                <button type="button" 
                        class="btn-sort ${isActive ? 'active' : ''}" 
                        style="margin-right:6px; margin-bottom:6px;"
                        onclick="selectSummaryTab('${fac.id}')">
                    <span>${fac.name}</span>
                    <span class="${getRatingBadgeClass(fac.rating)}" style="margin-left:4px;">${fac.rating.toFixed(2)}</span>
                </button>
            `;
        }).join("");
    }

    function renderSingleCard() {
        const fac = window.FACILITY_SUMMARIES.find(f => f.id === selectedFacilityId);
        if (!fac) return;

        singleCard.innerHTML = `
            <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <h2 style="font-size:1.15rem; font-weight:700; color:var(--text-primary); margin:0;">${fac.name}</h2>
                    <span class="${getRatingBadgeClass(fac.rating)}" style="font-size:0.95rem; font-weight:700;">${fac.rating.toFixed(2)} / 5.0</span>
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:12px;">
                    ${fac.comments_count} verified comments &bull; ${fac.issues_count} recurring complaint areas
                </div>
                <p style="font-size:0.88rem; color:var(--text-primary); line-height:1.6; margin-bottom:16px;">
                    ${escapeHtml(fac.summary)}
                </p>
                <button type="button" class="btn-secondary" onclick="copySummaryText('${fac.id}', this)" style="font-size:0.78rem;">
                    Copy summary
                </button>
            </div>
        `;
    }

    function renderCompareCard(container, facilityId) {
        if (!container) return;
        const fac = window.FACILITY_SUMMARIES.find(f => f.id === facilityId);
        if (!fac) {
            container.innerHTML = `<div style="padding: 20px; color: var(--text-muted);">No data available.</div>`;
            return;
        }

        container.innerHTML = `
            <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="font-size:1.05rem; font-weight:700; color:var(--text-primary); margin:0;">${fac.name}</h3>
                    <span class="${getRatingBadgeClass(fac.rating)}" style="font-weight:700;">${fac.rating.toFixed(2)} / 5.0</span>
                </div>
                <div style="font-size:0.78rem; color:var(--text-muted); margin-bottom:10px;">
                    ${fac.comments_count} verified comments &bull; ${fac.issues_count} recurring complaint areas
                </div>
                <p style="font-size:0.84rem; color:var(--text-primary); line-height:1.55; margin-bottom:14px;">
                    ${escapeHtml(fac.summary)}
                </p>
                <button type="button" class="btn-secondary" onclick="copySummaryText('${fac.id}', this)" style="font-size:0.75rem; padding:4px 10px;">
                    Copy summary
                </button>
            </div>
        `;
    }

    function refreshCompareView() {
        if (compareSelectA && cardCompareA) renderCompareCard(cardCompareA, compareSelectA.value);
        if (compareSelectB && cardCompareB) renderCompareCard(cardCompareB, compareSelectB.value);
    }

    if (btnModeSingle) {
        btnModeSingle.addEventListener("click", () => {
            btnModeSingle.classList.add("active");
            btnModeCompare.classList.remove("active");
            singleSection.style.display = "block";
            compareSection.style.display = "none";
        });
    }

    if (btnModeCompare) {
        btnModeCompare.addEventListener("click", () => {
            btnModeCompare.classList.add("active");
            btnModeSingle.classList.remove("active");
            singleSection.style.display = "none";
            compareSection.style.display = "block";
            refreshCompareView();
        });
    }

    if (compareSelectA) compareSelectA.addEventListener("change", refreshCompareView);
    if (compareSelectB) compareSelectB.addEventListener("change", refreshCompareView);

    tabSortButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tabSortButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentTabSort = btn.getAttribute("data-sort");
            renderTabs();
        });
    });

    window.selectSummaryTab = function(facilityId) {
        selectedFacilityId = facilityId;
        renderTabs();
        renderSingleCard();
    };

    renderTabs();
    renderSingleCard();
}

window.copySummaryText = function(facilityId, btnElement) {
    const fac = window.FACILITY_SUMMARIES ? window.FACILITY_SUMMARIES.find(f => f.id === facilityId) : null;
    if (!fac || !fac.summary) return;

    navigator.clipboard.writeText(fac.summary.trim()).then(() => {
        if (!btnElement) return;
        const oldText = btnElement.textContent;
        btnElement.textContent = "Copied!";
        btnElement.style.color = "var(--sentiment-pos)";
        setTimeout(() => {
            btnElement.textContent = oldText;
            btnElement.style.color = "";
        }, 1800);
    });
};

// =============================================================
// 7. Flagged / Abusive Content Page
// =============================================================
function initFlaggedPage() {
    const tableEl = document.getElementById("flaggedDataTable");
    if (!tableEl || !window.FLAGGED_DATA) return;

    const facilitySelect = document.getElementById("flaggedFacilitySelect");
    const searchInput = document.getElementById("flaggedSearchInput");
    const rowCountEl = document.getElementById("flaggedRowCount");
    const tableBody = document.getElementById("flaggedTableBody");
    const expandedCommentIds = new Set();

    function renderTable() {
        const facFilter = facilitySelect ? facilitySelect.value : "all";
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : "";

        let filtered = window.FLAGGED_DATA.filter(row => {
            if (facFilter !== "all" && row.facility !== facFilter) return false;
            if (searchTerm) {
                const matchId = row.id.toLowerCase().includes(searchTerm);
                const matchText = row.text.toLowerCase().includes(searchTerm);
                const matchFac = row.display_facility.toLowerCase().includes(searchTerm);
                if (!matchId && !matchText && !matchFac) return false;
            }
            return true;
        });

        filtered.sort((a, b) => b.bert_score - a.bert_score);

        if (filtered.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 32px; color: var(--text-muted);">No quarantined comments match criteria.</td></tr>';
        } else {
            tableBody.innerHTML = filtered.map(row => {
                const isExpanded = expandedCommentIds.has(row.id);
                const fullText = row.text;
                const snippet = fullText.length > 90 ? fullText.substring(0, 87) + "..." : fullText;
                const textHtml = isExpanded ? escapeHtml(fullText) : escapeHtml(snippet);
                const toggleBtn = fullText.length > 90 ? `<button type="button" class="btn-sort" style="margin-left:6px; font-size:0.72rem; padding:2px 6px;" onclick="window.toggleCommentExpand('${row.id}')">${isExpanded ? 'Collapse' : 'Show full comment'}</button>` : '';

                return `
                    <tr>
                        <td style="font-family: monospace; font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(row.id)}</td>
                        <td><strong>${escapeHtml(row.display_facility)}</strong></td>
                        <td><span class="badge-neg">${row.bert_score.toFixed(3)}</span></td>
                        <td>${textHtml} ${toggleBtn}</td>
                    </tr>
                `;
            }).join("");
        }

        if (rowCountEl) {
            rowCountEl.textContent = `Showing ${filtered.length} of ${window.FLAGGED_DATA.length} flagged comments`;
        }
    }

    window.toggleCommentExpand = function(commentId) {
        if (expandedCommentIds.has(commentId)) {
            expandedCommentIds.delete(commentId);
        } else {
            expandedCommentIds.add(commentId);
        }
        renderTable();
    };

    if (facilitySelect) facilitySelect.addEventListener("change", renderTable);
    if (searchInput) searchInput.addEventListener("input", renderTable);

    renderTable();
}
