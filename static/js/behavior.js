// behavior.js - Client-side tracking logic (Fixed for HTMX Timing)

(function() {
    console.log("👁️ Behavioral Tracking Initialized");

    let lastPageTime = Date.now();
    let currentPage = window.location.pathname;

    // --- 1. Page View & Leave Tracking ---
    
    function trackPageView() {
        // Update current page from URL
        currentPage = window.location.pathname;
        lastPageTime = Date.now();
        
        console.log(`📡 Tracking Page View: ${currentPage}`); // Debug Log

        sendEvent({
            type: "page_view",
            page: currentPage,
            timestamp: Date.now() / 1000
        });
    }

    function trackPageLeave() {
        const now = Date.now();
        const dwellTime = (now - lastPageTime) / 1000;
        
        // Don't track insignificant dwells (< 0.5s)
        if (dwellTime < 0.5) return;

        console.log(`📡 Tracking Page Leave: ${currentPage} (${dwellTime.toFixed(1)}s)`);

        sendEvent({
            type: "page_leave",
            page: currentPage,
            timestamp: now / 1000,
            dwell_time: dwellTime
        });
    }

    // Hook into HTMX navigation
    document.body.addEventListener('htmx:afterSwap', (evt) => {
        // 1. Track leave of OLD page immediately
        trackPageLeave();
        
        // 2. Wait for URL to update, then track NEW page
        setTimeout(() => {
            trackPageView();
        }, 100); 
    });
    
    // Initial load
    trackPageView();

    // Handle browser tab close / refresh
    window.addEventListener('beforeunload', trackPageLeave);


    // --- 2. Rage Click Detection ---
    
    let clickHistory = [];
    const RAGE_THRESHOLD = 3; 
    const RAGE_WINDOW = 2000; 

    document.addEventListener('click', (e) => {
        const now = Date.now();
        const target = e.target;
        
        clickHistory = clickHistory.filter(t => (now - t.time) < RAGE_WINDOW);
        clickHistory.push({ time: now, target: target });

        const clicksOnTarget = clickHistory.filter(c => c.target === target).length;
        
        if (clicksOnTarget >= RAGE_THRESHOLD) {
            console.log("🤬 Rage Click Detected!");
            sendEvent({
                type: "rage_click",
                page: currentPage,
                timestamp: now / 1000,
                click_count: clicksOnTarget,
                element: target.tagName + (target.id ? `#${target.id}` : "")
            });
            clickHistory = []; 
        }
        
        if (target.matches('[data-track], [data-track] *')) {
            sendEvent({
                type: "click",
                page: currentPage,
                timestamp: now / 1000,
                element: target.innerText || target.id
            });
        }
    });


    // --- 3. Form Submission Tracking ---
    
    document.addEventListener('submit', (e) => {
        const form = e.target;
        sendEvent({
            type: "form_submit",
            page: currentPage,
            timestamp: Date.now() / 1000,
            metadata: { form_id: form.id || 'unknown_form' }
        });
    });


    // --- Helper: Send Data ---
    
    function sendEvent(data) {
        const url = "/api/track-event";
        
        // Always try sendBeacon first for reliability
        if (navigator.sendBeacon) {
            const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
        } else {
            // Fallback to fetch with credentials ensured
            fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data),
                credentials: 'same-origin' // Ensure cookie is sent
            }).catch(err => console.error("Tracking Error:", err));
        }
    }

})();