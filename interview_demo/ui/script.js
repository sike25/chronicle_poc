let chronicleData = {};

// Load data from API endpoint or local JSON file
fetch('chronicle_data.json').then(response => response.json()).then(data => { 
    chronicleData = data;
    console.log('Chronicle data loaded:', chronicleData);
});


// Add click handlers to query buttons
document.addEventListener('DOMContentLoaded', () => {
    const queryButtons = document.querySelectorAll('.query-btn'); 
    queryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const query = button.dataset.query;
            runQuery(query);
        });
    });
});

async function runQuery(query) {
    console.log(`Running Chronicle for: ${query}`);

    // Display the logs container
    const logsContainer = document.getElementById('logsContainer');
    const logMessages   = document.getElementById('logMessages');
    logsContainer.style.display = 'block';
    logMessages.innerHTML = '';
    
    // Generate the logs
    try {
        // Step 1: Search archives
        addLog('Searching Nigerian archives...');
        const searchResults = await searchArchives(query);
        addLog(`📌 Found <span class="highlight">${searchResults.documentCount}</span> documents spanning <span class="highlight">${searchResults.dateRange.min.split('/')[2]}</span> to <span class="highlight">${searchResults.dateRange.max.split('/')[2]}</span>`);
        addLog('');

        // Step 2: Organize into periods
        addLog('Organizing documents into time periods...');
        const periods = await organizePeriods(searchResults);
        addLog(`📌 Created <span class="highlight">${periods.bucketCount}</span> time periods`);
        addLog('');

        // Step 3: Generate summaries
        addLog('Generating period summaries...');
        const enrichedData = await generateSummaries(periods);
        addLog('📌 Period summaries complete');
        addLog('');
        
        // Step 4: Build timeline
        addLog('Building timeline...');
        await buildTimeline(enrichedData);
    } catch (error) {
        console.error('Error running Chronicle:', error);
        logMessages.innerHTML += `<p style="color: red;">Error: ${error.message}</p>`;
    }

}

async function searchArchives(query) {
    const response = await fetch(`http://localhost:5000/api/search?query=${encodeURIComponent(query)}`);
    const data = await response.json();
    
    return {
        query: query,
        documentCount: data.documentCount,
        dateRange: data.dateRange,
        rawData: data
    };
}

async function organizePeriods(searchResults) {
    const response = await fetch('http://localhost:5000/api/organize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchResults.query })
    });
    
    const data = await response.json();
    
    return {
        query: searchResults.query,
        bucketCount: data.bucketCount,
        buckets: data.buckets
    };
}

async function generateSummaries(periods) {
    // THIS IS WHERE THE REAL CLAUDE API CALLS HAPPEN!
    const response = await fetch('http://localhost:5000/api/enrich', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: periods.query })
    });
    
    const data = await response.json();
    return data;
}

async function buildTimeline(data) {
    await sleep(300);
    showTimeline(data);
}

function showTimeline(data) {
    const timelineContainer = document.getElementById('timelineContainer');
    const timelineTitle = document.getElementById('timelineTitle');
    const timeline = document.getElementById('timeline');
    
    // Show container
    timelineContainer.style.display = 'block';
    
    // Update title
    const queryName = data.query.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    timelineTitle.textContent = `${queryName} Coverage Over Time`;
    
    // Clear previous timeline
    timeline.innerHTML = '';
    
    // Create timeline line
    const line = document.createElement('div');
    line.className = 'timeline-line';
    timeline.appendChild(line);
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'timeline-tooltip';
    document.body.appendChild(tooltip);
    
    // Calculate positions
    const bucketCount = data.buckets.length;
    
    // Create timeline points
    data.buckets.forEach((bucket, index) => {
        const point = document.createElement('div');
        point.className = 'timeline-point';
        
        // Position along the timeline
        const position = ((index + 0.5) / bucketCount) * 100;
        point.style.left = `${position}%`;
        
        // Create point circle
        const circle = document.createElement('div');
        circle.className = 'timeline-point-circle';
        point.appendChild(circle);
        
        // Label (period)
        const label = document.createElement('div');
        label.className = 'timeline-label';
        label.textContent = bucket.bucket_label;
        point.appendChild(label);
        
        // Count (number of articles)
        const count = document.createElement('div');
        count.className = 'timeline-count';
        count.textContent = `${bucket.article_count} article${bucket.article_count !== 1 ? 's' : ''}`;
        point.appendChild(count);
        
        // Hover for tooltip
        point.addEventListener('mouseenter', (e) => {
            tooltip.innerHTML = `
                <div class="tooltip-title">${bucket.bucket_title}</div>
                <div class="tooltip-summary">${bucket.bucket_summary}</div>
            `;
            tooltip.classList.add('visible');
            updateTooltipPosition(e, tooltip);
        });
        
        point.addEventListener('mousemove', (e) => {
            updateTooltipPosition(e, tooltip);
        });
        
        point.addEventListener('mouseleave', () => {
            tooltip.classList.remove('visible');
        });
        
        // Click to expand
        point.addEventListener('click', () => {
            showBucketDetails(bucket);
        });
        
        timeline.appendChild(point);
    });
    
    // Scroll to timeline
    timelineContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function updateTooltipPosition(event, tooltip) {
    tooltip.style.left = `${event.clientX + 15}px`;
    tooltip.style.top = `${event.clientY + 15}px`;
}
function showBucketDetails(bucket) {
    console.log('Showing bucket details:', bucket);
    
    const modal = document.getElementById('bucketModal');
    const period = document.getElementById('bucketPeriod');
    const title = document.getElementById('bucketTitle');
    const summary = document.getElementById('bucketSummary');
    const articlesContainer = document.getElementById('bucketArticles');
    
    // Set header information - period is now the main heading
    period.textContent = bucket.bucket_label;
    title.textContent = bucket.bucket_title;
    summary.textContent = bucket.bucket_summary;
    
    // Clear previous articles
    articlesContainer.innerHTML = '';
    
    // Add articles as linked text
    bucket.articles.forEach(article => {
        const link = document.createElement('a');
        link.className = 'article-link';
        link.href = `../nigerian_news_dataset/all_topics/${article.filename}`;
        link.target = '_blank';
        
        // Format: × Headline, Source, Date
        link.textContent = `${article.headline}, ${article.source}, ${formatDate(article.date)}.`;
        
        articlesContainer.appendChild(link);
    });
    
    // Show modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function formatDate(dateString) {
    // Convert "23/12/1987" to "23 December 1987"
    const [day, month, year] = dateString.split('/');
    const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December'];
    return `${parseInt(day)} ${months[parseInt(month) - 1]} ${year}`;
}
function closeBucketDetails() {
    const modal = document.getElementById('bucketModal');
    modal.style.display = 'none';
    document.body.style.overflow = ''; // Restore scrolling
}

function viewArticle(article) {
    // Open the full article image in a new window/tab
    window.open(`../nigerian_news_dataset/all_topics/${article.filename}`, '_blank');
}

// Close modal with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeBucketDetails();
    }
});

// UI Helper functions ----------------------
function addLog(message) {
    const logMessages = document.getElementById('logMessages');
    const logDiv = document.createElement('div');
    logDiv.className = 'log-message';
    logDiv.innerHTML = message;
    logMessages.appendChild(logDiv);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

