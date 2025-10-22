const processBtn = document.getElementById('process-btn')
const searchBtn = document.getElementById('search-button');
const modalSubmitBtn = document.getElementById('modal-submit-btn');
const loader = document.getElementById('spinner')
const rows = document.querySelectorAll('.transaction-table-body tr');
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const searchInput = document.getElementById('search-input');
const filterOptions = document.getElementById('filter-options');
const startDateInput = document.getElementById('datepicker1');
const endDateInput = document.getElementById('datepicker2');

var isScrolledToTop = true;
let isStartDateEmpty = true;
let isEndDateEmpty = true;
let selectedVendorsInvoiceNumber = [];
let selectedPageNumber = 1;
let numberOfPages = 0;
let hasClickedOnSearchBtn = false;
let query_params = [];
let selectedTransactionType = {};


let combinedValues = [];
sessionStorage.clear();

addCheckBoxandSelectValues(rows);
addEventListenerToCheckboxes(checkboxes);
addEventListenerToAnchorTag();
addEventListenersToSelect(rows)

function addEventListenersToSelect(rows) {
    rows.forEach(row => {
        const acctInputs = row.querySelectorAll('.account-live-input');
        acctInputs.forEach(input => {
            input.addEventListener('input', () => {
                const accountName = (input.value || '').trim();
                const trow = input.closest('tr');
                const inputElement = trow.querySelector('input[name="transaction"]');
                const value = inputElement.value;
                if (accountName) {
                    if (value) {
                        inputElement.removeAttribute('disabled');
                    } else {
                        inputElement.setAttribute('disabled', 'disabled');
                    }
                    sessionStorage.setItem("accountName-" + value, accountName);
                } else {
                    sessionStorage.removeItem("accountName-" + value);
                    inputElement.setAttribute('disabled', 'disabled');
                }
            });
        });
    });
}

function addCheckBoxandSelectValues(rows) {
    rows.forEach(row => {
        if (row.id) {
            const value = row.id;
            const inputElement = row.querySelector('input[name="transaction"]');
            const acctInput = row.querySelector('.account-live-input');
            const accountName = sessionStorage.getItem("accountName-" + value);
            const checkbox = sessionStorage.getItem(value)
            if (acctInput) {
                if (accountName) {
                    acctInput.value = accountName;
                    if (checkbox) {
                        inputElement.checked = true;
                    }
                    inputElement.removeAttribute('disabled');
                } else {
                    acctInput.value = '';
                    inputElement.setAttribute('disabled', 'disabled');
                }
            }
        }
    });
}


function addEventListenerToCheckboxes(checkboxes) {
    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            const rowData = {
                values: [],
                project_id: null,
                project_name: null,
            };
            if (cb.checked) {
                const row = cb.closest('tr');
                // capture project info from tbody
                const tbody = row ? row.closest('tbody') : null;
                if (tbody) {
                    const pid = tbody.dataset.projectId || '1';
                    rowData.project_id = parseInt(pid, 10);
                    rowData.project_name = tbody.dataset.projectName || '';
                }

                // Iterate over each cell and construct values in expected order
                for (let j = 0; j < row.cells.length; j++) {
                    const cell = row.cells[j];

                    // Push textual columns: Date(1), Amount(2), Invoice(3), Reference(4), Vendor ID(5)
                    if (j >= 1 && j <= 5) {
                        rowData.values.push(cell.textContent);
                        continue;
                    }

                    // Account input + datalist column
                    if (j === 6) {
                        const input = cell.querySelector('.account-live-input');
                        const accountName = input ? (input.value || '').trim() : '';
                        // account_name
                        rowData.values.push(accountName);
                        // default transaction_type (kept for index compatibility)
                        rowData.values.push('');

                        // Try to resolve details from the selected datalist option
                        let accountNo = '';
                        let bankCode = '';
                        let bankName = '';
                        if (input && accountName) {
                            const listId = input.getAttribute('list');
                            const datalistEl = listId ? document.getElementById(listId) : null;
                            if (datalistEl) {
                                const options = Array.from(datalistEl.querySelectorAll('option'));
                                const match = options.find(opt => (opt.value || '').trim() === accountName);
                                if (match) {
                                    accountNo = match.getAttribute('data-account-no') || '';
                                    bankCode = match.getAttribute('data-bank-code') || '';
                                    bankName = match.getAttribute('data-bank-name') || '';
                                }
                            }
                        }
                        rowData.values.push(accountNo);
                        rowData.values.push(bankCode);
                        rowData.values.push(bankName);
                    }

                    // Ignore checkbox column (0) and actions column (7)
                }
                // Add or replace the row data by invoice ID to avoid duplicates across accordion sections
                const invoiceId = cb.value;
                combinedValues = combinedValues.filter(item => item && item.values && item.values[2] !== invoiceId);
                combinedValues.push(rowData);
                if (processBtn) {
                    processBtn.removeAttribute('disabled');
                }
                const value = cb.value;
                const checked = cb.checked;
                addSelectedVendorsInvoiceNumber(cb.value);
                sessionStorage.setItem(value, checked);
                saveSelectedRows();
            } else {
                const value = cb.value;
                removeSelectedVendorsInvoiceNumber(cb.value);
                sessionStorage.removeItem(value);
                saveSelectedRows();
                // Remove the row data from the combined values array by invoice ID
                combinedValues = combinedValues.filter(item => item && item.values && item.values[2] !== value);
                // Disable the process button only if no checkboxes remain checked across all tables
                const anyChecked = document.querySelectorAll('.transaction-table-body input[type="checkbox"]:checked').length > 0;
                if (processBtn) {
                    if (!anyChecked) {
                        processBtn.setAttribute('disabled', 'disabled');
                    } else {
                        processBtn.removeAttribute('disabled');
                    }
                }
            }
            console.log(combinedValues)
        })

    })
}

function scrollToTopOrBottom() {
    if (isScrolledToTop) {
        scrollToBottom();
        isScrolledToTop = false;
    } else {
        scrollToTop();
        isScrolledToTop = true;
    }
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: "smooth" // Optional: Add smooth scrolling animation
    });
}


function scrollToBottom() {
    window.scrollTo({
        top: document.documentElement.scrollHeight,
        behavior: "smooth" // Optional: Add smooth scrolling animation
    });
}




function addSelectedVendorsInvoiceNumber(invoiceId) {

    if (!selectedVendorsInvoiceNumber.includes(invoiceId)) {
        selectedVendorsInvoiceNumber.push(invoiceId);

    }
}

function removeSelectedVendorsInvoiceNumber(invoiceId) {
    const index = selectedVendorsInvoiceNumber.indexOf(invoiceId);
    if (index !== -1) {
        selectedVendorsInvoiceNumber.splice(index, 1);
    }
}

function saveSelectedRows() {
    let rows = document.querySelectorAll(`.transaction-table-body tr`);
    rows.forEach((row) => {
            let cb = row.querySelector('td input[type="checkbox"]')
            if (cb && cb.checked) {
                const transactionTypeEl = row.querySelector('td select[name="transaction_type"]');
                let transactionType = transactionTypeEl ? transactionTypeEl.value : 'IFT';
                selectedTransactionType[cb.value] = transactionType;
            }
        }
    )
}

function createModalTableBody(tableBodyID) {

    let tableBody = document.getElementById(tableBodyID);
    tableBody.innerHTML = '';

    // Group items by project_id
    const groups = {};
    combinedValues.forEach(item => {
        const pid = item.project_id || 0;
        if (!groups[pid]) {
            groups[pid] = { name: item.project_name || ('Project ' + pid), items: [] };
        }
        groups[pid].items.push(item);
    });

    // Render groups with a header row per project
    Object.keys(groups).forEach(pid => {
        const group = groups[pid];
        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `<td colspan="9" class="fw-bold bg-light">${group.name} (Project ID: ${pid})</td>`;
        tableBody.appendChild(headerRow);

        group.items.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.values[0]}</td>
                <td>${item.values[1]}</td>
                <td>${item.values[2]}</td>
                <td>${item.values[3]}</td>
                <td>${item.values[4]}</td>
                <td>${item.values[5]}</td>
                <td>${item.values[7]}</td>
                <td>${item.values[8]}</td>
                <td>${item.values[9]}</td>
                `;
            tableBody.appendChild(tr);
        });
    });

}


// handles the click even of the anchor tags
function handleClick(event) {
    event.preventDefault();
    const url = event.target.getAttribute('href');
    fetch(url)
        .then(response => response.text())
        .then(html => {
            updateTableAndPaginator(html)
            addEventListenerToAnchorTag();
        });
}

function addEventListenerToAnchorTag() {
    const paginationLinks = document.querySelectorAll('.custom-pagination a');
    paginationLinks.forEach(link => {
        link.addEventListener('click', handleClick); // Add the handleClick function as the event listener
    });
}

function removeEventListenerFromAnchorTag() {
    const paginationLinks = document.querySelectorAll('.custom-pagination a');
    paginationLinks.forEach(link => {
        link.removeEventListener('click', handleClick); // Remove the handleClick function as the event listener
    });
}

function updateTableAndPaginator(html) {
    const parser = new DOMParser();
    const newDoc = parser.parseFromString(html, 'text/html');

    const newRow = newDoc.querySelectorAll("#table-body tr");
    const newCheckboxes = newDoc.querySelectorAll('input[type="checkbox"]');

    addCheckBoxandSelectValues(newRow);
    addEventListenersToSelect(newRow);
    addEventListenerToCheckboxes(newCheckboxes);

    const newTable = newDoc.getElementById('table-body');
    const newPaginator = newDoc.getElementById('paginator');
    document.getElementById('table-body').replaceWith(newTable);
    document.getElementById('paginator').replaceWith(newPaginator);

    // Add any other necessary post-update operations
}

function fetchSearchResults(queryParams, page) {
    const searchInput = queryParams[0];
    const filterOptions = queryParams[1];

    fetch(`search/?search_params=${searchInput}&filter_options=${filterOptions}&page=${page}`)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML response
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');

            // Get the new HTML elements
            const newRow = newDoc.querySelectorAll("#table-body tr");
            const newCheckboxes = newDoc.querySelectorAll('input[type="checkbox"]');
            const newTable = newDoc.getElementById('table-body');
            const newPaginator = newDoc.getElementById('paginator');
            numberOfPages = parseInt(newPaginator.dataset.numPages);
            console.log(numberOfPages, selectedPageNumber)
            // Update the pagination links
            // Add event listeners to the new elements
            addCheckBoxandSelectValues(newRow);
            addEventListenersToSelect(newRow);
            addEventListenerToCheckboxes(newCheckboxes);

            // Replace the existing table and paginator with the new ones
            const tableBody = document.getElementById('table-body');
            const paginator = document.getElementById('paginator');

            tableBody.replaceWith(newTable);
            paginator.replaceWith(newPaginator)
            console.log(newPaginator)
            updatePaginationLinks(newPaginator);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}
function fetchHistorySearchResults(queryParams, page) {
    const historySearchInput = queryParams[0];
    const historyFilterOptions = queryParams[1];

    fetch(`history-search/?search_params=${historySearchInput}&filter_options=${historyFilterOptions}&page=${page}`)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML response
            const parser = new DOMParser();
            const newDoc = parser.parseFromString(html, 'text/html');
            const newChart = newDoc.getElementById('chart-div')
            // Get the new HTML elements
            const newTable = newDoc.getElementById('table-body');
            const newPaginator = newDoc.getElementById('paginator');
            numberOfPages = parseInt(newPaginator.dataset.numPages);
            console.log(numberOfPages, selectedPageNumber)
            const chart = document.getElementById('chart-div')
            // Replace the existing table and paginator with the new ones
            const tableBody = document.getElementById('table-body');
            const paginator = document.getElementById('paginator');
            chart.replaceWith(newChart);
            tableBody.replaceWith(newTable);
            paginator.replaceWith(newPaginator)
            console.log(newPaginator)
            updatePaginationLinks(newPaginator);
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}
// Add event listener to change page links

function getCSRFToken() {
    let csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken')).split('=')[1];
    if (csrfToken == null) {
        csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    }
    return csrfToken;
}

function updatePaginationLinks(newDoc) {
    const nextLink = newDoc.querySelector('#next')
    if (nextLink) {
        nextPageLink(nextLink)
    }
    const firstLink = newDoc.querySelector('#first')
    if (firstLink) {
        firstPageLink(firstLink)
    }
    const lastLink = newDoc.querySelector('#last')
    if (lastLink) {
        lastPageLink(lastLink)
    }
    const previousLink = newDoc.querySelector('#previous')
    if (previousLink) {
        previousPageLink(previousLink)
    }
}

async function goToPage() {

    try {
        fetchSearchResults(query_params, selectedPageNumber)
    } catch (err) {
        console.log(err);
    }
}

function nextPageLink(nextLink) {
    nextLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            if (selectedPageNumber !== numberOfPages) {
                selectedPageNumber += 1;
            }

            goToPage();

        }
    });
}

function previousPageLink(previousLink) {
    previousLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            if (selectedPageNumber !== 1) {
                selectedPageNumber -= 1;
            }

            goToPage();
        }
    });
}

function lastPageLink(lastLink) {
    lastLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            selectedPageNumber = numberOfPages;
            goToPage();
        }
    });
}

function firstPageLink(firstLink) {
    firstLink.addEventListener('click', (e) => {
        if (hasClickedOnSearchBtn === true) {
            e.preventDefault();
            selectedPageNumber = 1;
            goToPage();
        }
    });
}

// Generate a batch reference (JS-side) when the modal is about to show
function generateBatchRef() {
    const ts = new Date().toISOString().replace(/[-T:.Z]/g, '').slice(0, 14); // yyyymmddhhmmss
    const rand = Math.random().toString(36).slice(2, 8).toUpperCase();
    return `BR-${ts}-${rand}`;
}

// Hook into Bootstrap modal show/hide to set/reset values
$(document).ready(function () {
    const $modal = $('#post-transaction-modal');
    if ($modal.length) {
        $modal.on('show.bs.modal', function () {
            // Auto-generate and set batch reference
            const ref = generateBatchRef();
            $('#batch-ref-input').val(ref);
            $('#batch-desc-input').val('');
            // Refresh the table content in the modal
            createModalTableBody('modal-table-body');
        });
        $modal.on('hidden.bs.modal', function () {
            // Reset values when modal is closed
            $('#batch-ref-input').val('');
            $('#batch-desc-input').val('');
        });
    }
});

if (processBtn){
    processBtn.addEventListener('click', (e) => {
        e.preventDefault();
        // Table body will also be created on show event, but we keep this for safety
        createModalTableBody('modal-table-body');
    });
}
if (modalSubmitBtn){
    modalSubmitBtn.addEventListener('click', (e) => {
        loader.classList.remove('d-none')
        e.preventDefault()
        // Always generate a fresh batch reference at submission time to avoid reuse on retries
        const freshBatchRef = generateBatchRef();
        if (document.getElementById('batch-ref-input')) {
            document.getElementById('batch-ref-input').value = freshBatchRef;
        }
        const batchRef = freshBatchRef;
        const batchDesc = document.getElementById('batch-desc-input') ? document.getElementById('batch-desc-input').value : '';

        // Build unique transaction references per item for this submission only
        const txRefsMap = {};
        const ts = new Date().toISOString().replace(/[-T:.Z]/g, '').slice(0, 14);
        const baseRand = Math.random().toString(36).slice(2, 8).toUpperCase();
        combinedValues.forEach((item, idx) => {
            try {
                const invoiceId = item && item.values ? item.values[2] : `IDX${idx}`;
                // TR-<timestamp>-<rand>-<seq>
                txRefsMap[invoiceId] = `TR-${ts}-${baseRand}-${(idx+1).toString().padStart(3,'0')}`;
            } catch (_) {}
        });

        // Send selected invoice numbers & transaction type to server using ajax
        $.ajax({
            type: 'POST',
            url: 'post-transactions/',
            data: {
                'csrfmiddlewaretoken': getCSRFToken(),
                'transactions': JSON.stringify(combinedValues),
                'invoice_ids[]': JSON.stringify(selectedVendorsInvoiceNumber),
                'transaction_type': JSON.stringify(selectedTransactionType),
                'batch_ref': batchRef,
                'narration': batchDesc,
                'transaction_refs': JSON.stringify(txRefsMap),
                                'source_bank_id': (function(){ var el = document.getElementById('source-bank-select'); return el ? el.value : ''; })()
            },
            dataType: 'json',
        })
        .done(res => {
            loader.classList.add('d-none');
            $('#post-transaction-modal').modal('hide');

            // Prefer backend-provided messages
            const extractMessage = (payload) => {
                if (!payload) return '';
                const d = payload.data || {};
                // Common backend fields
                return (
                    payload.message ||
                    d.message ||
                    d.responseMessage ||
                    d.statusMessage ||
                    d.status ||
                    payload.error ||
                    (typeof payload === 'string' ? payload : '') ||
                    ''
                );
            };

            const msg = extractMessage(res) || 'Request processed.';
            const icon = res.success ? 'success' : 'error';
            const title = res.success ? 'Transaction processing' : 'Transaction failed';

            Swal.fire({
                icon: icon,
                title: title,
                text: msg,
                confirmButtonText: 'OK'
            }).then(() => {
                if (res.success) {
                    // If backend returns a dashboard redirect previously, keep behavior
                    window.location.href = 'dashboard';
                }
            });
        })
        .fail((xhr) => {
            loader.classList.add('d-none');
            $('#post-transaction-modal').modal('hide');

            let payload = null;
            try {
                payload = xhr.responseJSON ? xhr.responseJSON : JSON.parse(xhr.responseText);
            } catch (_) {}

            const d = payload && payload.data ? payload.data : {};
            const msg = (payload && (payload.message || payload.error)) || d.message || d.responseMessage || d.statusMessage || d.status || 'Your request could not be processed.';

            Swal.fire({
                icon: 'error',
                title: 'Transaction failed',
                text: msg,
                confirmButtonText: 'OK',
                footer: 'Try again later'
            });
        });
    });
}

if (searchBtn){searchBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const q = encodeURIComponent(searchInput.value || '');
    const f = encodeURIComponent(filterOptions.value || '');
    window.location.href = `search/?search_params=${q}&filter_options=${f}`;
})}
if (filterOptions){
    filterOptions.addEventListener('change', () => {
        searchInput.removeAttribute('readonly');
    
        if (filterOptions.value === 'date') {
            // Destroy any existing Flatpickr instance
            if (searchInput._flatpickr) {
                searchInput._flatpickr.destroy();
            }
            searchInput._flatpickr = flatpickr(searchInput, {
                dateFormat: 'Ymd',
    
            });
        } else {
            // Destroy Flatpickr if it's not the "date" option
            if (searchInput._flatpickr) {
                searchInput._flatpickr.destroy();
            }
        }
    });
    
}
