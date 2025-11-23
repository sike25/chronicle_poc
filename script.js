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
        addLog(`📌 Found <span class="highlight">${searchResults.documentCount}</span> documents spanning <span class="highlight">${searchResults.dateRange.min} - ${searchResults.dateRange.max}</span>`);
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
        addLog('✨ Building timeline...');
        await buildTimeline(enrichedData);
    } catch (error) {
        console.error('Error running Chronicle:', error);
        logMessages.innerHTML += `<p style="color: red;">Error: ${error.message}</p>`;
    }

}

function showBucketDetails(bucket) {
    console.log('Clicked bucket:', bucket);
    // TODO: build the bucket expansion panel next
}
    

async function searchArchives(query) {
    // TODO: Replace with actual API call to /api/search
    // const response = await fetch(`/api/search?query=${query}`);
    // return await response.json();
    
    await sleep(500);
    const data = chronicleData[query];
    console.log('Search results:', data);
    return {
        query: query,
        documentCount: data.total_articles,
        dateRange: data.date_range,
        rawData: data
    };
}

async function organizePeriods(searchResults) {
    // TODO: Replace with actual API call to /api/organize
     // const response = await fetch('/api/organize', {
    //     method: 'POST',
    //     body: JSON.stringify(searchResults)
    // });
    // return await response.json();
    
    await sleep(500);
    return {
        query: searchResults.query,
        bucketCount: searchResults.rawData.buckets.length,
        buckets: searchResults.rawData.buckets
    };
}

async function generateSummaries(periods) {
    // TODO: Replace with actual API call to /api/summarize
    // This would call Claude's API to generate titles/summaries
    // const response = await fetch('/api/summarize', {
    //     method: 'POST',
    //     body: JSON.stringify(periods)
    // });
    // return await response.json();
    
    await sleep(800);
    return periods; // Already have summaries in our data
}

async function buildTimeline(data) {
    await sleep(300);
    showTimeline(data);
}

let currentChart = null;
function showTimeline(data) {
    const timelineContainer = document.getElementById('timelineContainer');
    const timelineTitle = document.getElementById('timelineTitle');
    const canvas = document.getElementById('timelineChart');
    
    // Show container
    timelineContainer.style.display = 'block';
    
    // Update title
    const queryName = data.query.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    timelineTitle.textContent = `${queryName} Coverage Over Time`;
    
    // Destroy previous chart if exists
    if (currentChart) {
        currentChart.destroy();
    }
    
    // Prepare data for Chart.js
    const labels = data.buckets.map(b => b.bucket_label);
    const counts = data.buckets.map(b => b.article_count);
    const bucketTitles = data.buckets.map(b => b.bucket_title);
    const bucketSummaries = data.buckets.map(b => b.bucket_summary);
    
    // Create chart
    const ctx = canvas.getContext('2d');
    currentChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Articles',
                data: counts,
                backgroundColor: '#FF6B35',
                borderColor: '#FF6B35',
                borderWidth: 1,
                hoverBackgroundColor: '#E55A2B',
                hoverBorderColor: '#E55A2B'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const index = context[0].dataIndex;
                            return bucketTitles[index];
                        },
                        label: function(context) {
                            return `${context.parsed.y} articles`;
                        },
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            return '\n' + bucketSummaries[index];
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    displayColors: false,
                    bodySpacing: 6
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: '#f0f0f0'
                    },
                    title: {
                        display: true,
                        text: 'Number of Articles',
                        font: {
                            size: 13,
                            weight: '600'
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Time Period',
                        font: {
                            size: 13,
                            weight: '600'
                        }
                    }
                }
            },
            onClick: (event, activeElements) => {
                if (activeElements.length > 0) {
                    const index = activeElements[0].index;
                    const bucket = data.buckets[index];
                    showBucketDetails(bucket);
                }
            }
        }
    });
    
    // Scroll to timeline
    timelineContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

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

