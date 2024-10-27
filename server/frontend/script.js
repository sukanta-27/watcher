// script.js

// API base URL
// const API_BASE_URL = 'http://localhost:8080/api';
// const API_BASE_URL = '/api';

const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8080/api'
    : 'https://watcher-sukanta.fly.dev/api';


let globalQueryParams = {};
let currentPage = 1;
let totalPages = 1;

// Load Data Functionality
if (document.getElementById('load-data-form')) {
    document.getElementById('load-data-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const csvUrl = document.getElementById('csv-url').value;

        if (!csvUrl) {
            M.toast({html: 'Please enter a valid CSV URL.', classes: 'red'});
            return;
        }

        fetch(`${API_BASE_URL}/upload_data_async`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_url: csvUrl })
        })
        .then(response => {
            const statusCode = response.status;
            document.getElementById('status-code').innerText = statusCode;
            document.getElementById('load-data-response').style.display = 'block';

            if (response.ok) {
                return response.json().then(data => {
                    displayResponseBody(data);
                    M.toast({html: 'Data loaded successfully!', classes: 'green'});
                });
            } else {
                return response.json().then(data => {
                    displayResponseBody(data);
                    M.toast({html: 'Failed to load data.', classes: 'red'});
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('status-code').innerText = 'Error';
            document.getElementById('response-body').innerText = 'An error occurred while processing your request.';
            document.getElementById('load-data-response').style.display = 'block';
            M.toast({html: 'Failed to load data.', classes: 'red'});
        });
    });
}

// Function to display the response body nicely
function displayResponseBody(data) {
    const responseBodyElement = document.getElementById('response-body');
    responseBodyElement.innerText = JSON.stringify(data, null, 2);
}

// Function to handle track task form submission
document.addEventListener('DOMContentLoaded', function () {
    const trackTaskForm = document.getElementById('track-task-form');

    if (trackTaskForm) {
        trackTaskForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const taskIdInput = document.getElementById('task-id');
            const taskId = taskIdInput.value.trim();

            if (!taskId) {
                M.toast({ html: 'Please enter a Task ID.', classes: 'red' });
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/upload_data_async/status?task_id=${encodeURIComponent(taskId)}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                const responseData = await response.json();

                const taskStatusResponse = document.getElementById('task-status-response');
                const taskStatus = document.getElementById('task-status');

                if (response.ok) {
                    // Display the task status
                    taskStatus.innerText = JSON.stringify(responseData, null, 2);
                    taskStatusResponse.style.display = 'block';
                } else {
                    // Display error message
                    taskStatus.innerText = `Error: ${responseData.detail || 'Unable to fetch task status.'}`;
                    taskStatusResponse.style.display = 'block';
                }
            } catch (error) {
                console.error('Error fetching task status:', error);
                M.toast({ html: 'An error occurred while fetching task status.', classes: 'red' });
            }
        });
    }

});

// Initialize Materialize components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize datepickers
    var datepickers = document.querySelectorAll('.datepicker');
    M.Datepicker.init(datepickers, {
        format: 'yyyy-mm-dd',
        autoClose: true,
        maxDate: new Date()
    });

    // Initialize select elements
    var selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);

    // Advanced Search Toggle
    const advancedToggle = document.getElementById('advanced-search-toggle');
    const advancedSection = document.getElementById('advanced-search-section');

    advancedToggle.addEventListener('click', function(event) {
        event.preventDefault();
        if (advancedSection.style.display === 'none') {
            advancedSection.style.display = 'block';
            advancedToggle.innerHTML = '<i class="material-icons left">expand_less</i>Hide Advanced Search';
        } else {
            advancedSection.style.display = 'none';
            advancedToggle.innerHTML = '<i class="material-icons left">expand_more</i>Advanced Search';
        }
    });

    // Add Field Buttons
    const addFieldButtons = document.querySelectorAll('.add-field-btn');
    addFieldButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            const fieldType = this.getAttribute('data-field');
            addDynamicField(fieldType);
        });
    });
});

// Function to add dynamic fields
function addDynamicField(fieldType) {
    const container = document.getElementById(`${fieldType}-container`);
    const fieldDiv = document.createElement('div');
    fieldDiv.className = `${fieldType}-field`;

    const input = document.createElement('input');
    input.type = 'text';
    input.name = fieldType;
    fieldDiv.appendChild(input);

    const removeBtn = document.createElement('a');
    removeBtn.href = '#';
    removeBtn.className = 'remove-field-btn';
    removeBtn.innerHTML = '<i class="material-icons small">remove</i>';
    removeBtn.addEventListener('click', function(event) {
        event.preventDefault();
        container.removeChild(fieldDiv);
    });
    fieldDiv.appendChild(removeBtn);

    container.appendChild(fieldDiv);
}

// Query Data Functionality
if (document.getElementById('data-query-form')) {
    document.getElementById('data-query-form').addEventListener('submit', function(event) {
        event.preventDefault();

        // Reset current page to 1 when a new search is made
        currentPage = 1;

        // Collect query parameters
        globalQueryParams = collectQueryParams();

        // Fetch data for the first page
        fetchData(currentPage, globalQueryParams);
    });
}

// Function to collect query parameters
function collectQueryParams() {
    const params = {};

    // Basic Fields
    const basicFields = ['name', 'app_id', 'price', 'dlc_count', 'score_rank', 'positive_reviews', 'negative_reviews', 'required_age', 'about_the_game'];
    basicFields.forEach(field => {
        const value = document.getElementById(field).value;
        if (value) params[field] = value;
    });

    // Platforms
    const platforms = M.FormSelect.getInstance(document.getElementById('platforms')).getSelectedValues();
    if (platforms.length > 0) {
        params['platforms'] = platforms;
    }

    // Dynamic List Fields
    const listFields = ['developers', 'publishers', 'categories', 'genres', 'tags', 'supported_languages'];
    listFields.forEach(field => {
        const inputs = document.getElementsByName(field);
        const values = [];
        inputs.forEach(input => {
            if (input.value) values.push(input.value);
        });
        if (values.length > 0) {
            params[field] = values;
        }
    });

    // Range Fields
    const rangeFields = ['price', 'positive_reviews', 'negative_reviews'];
    rangeFields.forEach(field => {
        const minValue = document.getElementById(`${field}_min`).value;
        const maxValue = document.getElementById(`${field}_max`).value;
        if (minValue) params[`${field}_min`] = minValue;
        if (maxValue) params[`${field}_max`] = maxValue;
    });

    // Release Date Range
    const releaseDateMin = document.getElementById('release_date_min').value;
    const releaseDateMax = document.getElementById('release_date_max').value;
    if (releaseDateMin) params['release_date_min'] = releaseDateMin;
    if (releaseDateMax) params['release_date_max'] = releaseDateMax;

    // Page Size
    const page_size = document.getElementById('page_size').value || '10';
    params['page_size'] = page_size;

    return params;
}

// Function to fetch data for a specific page
function fetchData(page, queryParams) {
    // Update the current page
    currentPage = page;

    // Create URLSearchParams from queryParams
    const params = new URLSearchParams();

    // Append query parameters
    for (const key in queryParams) {
        const value = queryParams[key];
        if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
        } else {
            params.append(key, value);
        }
    }

    // Append the current page
    params.append('page', currentPage);

    // Make GET request to the data explorer API
    fetch(`${API_BASE_URL}/query?` + params.toString())
    .then(response => response.json())
    .then(data => {
        totalPages = data.total_pages;
        displayQueryResults(data.results);
        setupPagination(currentPage, totalPages);
    })
    .catch(error => {
        console.error('Error:', error);
        M.toast({html: 'Failed to retrieve data.', classes: 'red'});
    });
}

// Function to display query results
// Function to display query results
function displayQueryResults(results) {
    const container = document.getElementById('query-results');
    container.innerHTML = '';

    if (!results || results.length === 0) {
        container.innerHTML = '<p>No results found.</p>';
        return;
    }

    // Create table
    const table = document.createElement('table');
    table.classList.add('striped', 'responsive-table');

    // Table headers
    const headers = [
        'App ID',
        'Name',
        'Release Date',
        'Required Age',
        'Price',
        'DLC Count',
        'About the Game',
        'Supported Languages',
        'Platforms',
        'Positive Reviews',
        'Negative Reviews',
        'Score Rank',
        'Developers',
        'Publishers',
        'Categories',
        'Genres',
        'Tags'
    ];

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    headers.forEach(headerText => {
        const th = document.createElement('th');
        th.innerText = headerText;
        // Add style to wrap text if needed
        th.style.wordWrap = 'break-word';
        th.style.whiteSpace = 'normal';
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Table body
    const tbody = document.createElement('tbody');

    results.forEach(game => {
        const row = document.createElement('tr');

        // App ID
        const appIdCell = document.createElement('td');
        appIdCell.innerText = game.app_id;
        row.appendChild(appIdCell);

        // Name
        const nameCell = document.createElement('td');
        nameCell.innerText = game.name;
        row.appendChild(nameCell);

        // Release Date
        const releaseDateCell = document.createElement('td');
        releaseDateCell.innerText = game.release_date;
        row.appendChild(releaseDateCell);

        // Required Age
        const requiredAgeCell = document.createElement('td');
        requiredAgeCell.innerText = game.required_age;
        row.appendChild(requiredAgeCell);

        // Price
        const priceCell = document.createElement('td');
        priceCell.innerText = `$${game.price}`;
        row.appendChild(priceCell);

        // DLC Count
        const dlcCountCell = document.createElement('td');
        dlcCountCell.innerText = game.dlc_count;
        row.appendChild(dlcCountCell);

        // About the Game
        const aboutCell = document.createElement('td');
        const truncatedText = game.about_the_game.length > 100
            ? game.about_the_game.substring(0, 100) + '...'
            : game.about_the_game;
        aboutCell.innerText = truncatedText;
        aboutCell.classList.add('tooltipped');
        aboutCell.setAttribute('data-position', 'bottom');
        aboutCell.setAttribute('data-tooltip', game.about_the_game);
        M.Tooltip.init(aboutCell);
        row.appendChild(aboutCell);

        // Supported Languages
        const languagesCell = document.createElement('td');
        languagesCell.innerText = game.supported_languages.join(', ');
        row.appendChild(languagesCell);

        // Platforms
        const platformsCell = document.createElement('td');
        const availablePlatforms = [];
        for (const [platform, isAvailable] of Object.entries(game.platforms)) {
            if (isAvailable) {
                availablePlatforms.push(platform.charAt(0).toUpperCase() + platform.slice(1));
            }
        }
        platformsCell.innerText = availablePlatforms.join(', ');
        row.appendChild(platformsCell);

        // Positive Reviews
        const positiveReviewsCell = document.createElement('td');
        positiveReviewsCell.innerText = game.positive_reviews;
        row.appendChild(positiveReviewsCell);

        // Negative Reviews
        const negativeReviewsCell = document.createElement('td');
        negativeReviewsCell.innerText = game.negative_reviews;
        row.appendChild(negativeReviewsCell);

        // Score Rank
        const scoreRankCell = document.createElement('td');
        scoreRankCell.innerText = game.score_rank !== null ? game.score_rank : 'N/A';
        row.appendChild(scoreRankCell);

        // Developers
        const developersCell = document.createElement('td');
        developersCell.innerText = game.developers.join(', ');
        row.appendChild(developersCell);

        // Publishers
        const publishersCell = document.createElement('td');
        publishersCell.innerText = game.publishers.join(', ');
        row.appendChild(publishersCell);

        // Categories
        const categoriesCell = document.createElement('td');
        categoriesCell.innerText = game.categories.join(', ');
        row.appendChild(categoriesCell);

        // Genres
        const genresCell = document.createElement('td');
        genresCell.innerText = game.genres.join(', ');
        row.appendChild(genresCell);

        // Tags
        const tagsCell = document.createElement('td');
        tagsCell.innerText = game.tags.join(', ');
        row.appendChild(tagsCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.appendChild(table);
}


// Function to setup pagination controls
function setupPagination(currentPage, totalPages) {
    const container = document.getElementById('pagination-controls');
    container.innerHTML = '';

    // Create pagination controls
    const paginationDiv = document.createElement('div');
    paginationDiv.className = 'pagination';

    // Previous Button
    const prevBtn = document.createElement('a');
    prevBtn.href = '#';
    prevBtn.className = currentPage === 1 ? 'disabled' : 'waves-effect';
    prevBtn.innerHTML = '<i class="material-icons">previous</i>';
    prevBtn.addEventListener('click', function(event) {
        event.preventDefault();
        if (currentPage > 1) {
            fetchData(currentPage - 1, globalQueryParams);
        }
    });
    paginationDiv.appendChild(prevBtn);

    // Page Info
    const pageInfo = document.createElement('span');
    pageInfo.style.margin = '0 15px';
    pageInfo.innerText = `Page ${currentPage} of ${totalPages}`;
    paginationDiv.appendChild(pageInfo);

    // Next Button
    const nextBtn = document.createElement('a');
    nextBtn.href = '#';
    nextBtn.className = currentPage === totalPages ? 'disabled' : 'waves-effect';
    nextBtn.innerHTML = '<i class="material-icons">next</i>';
    nextBtn.addEventListener('click', function(event) {
        event.preventDefault();
        if (currentPage < totalPages) {
            fetchData(currentPage + 1, globalQueryParams);
        }
    });
    paginationDiv.appendChild(nextBtn);

    container.appendChild(paginationDiv);
}
