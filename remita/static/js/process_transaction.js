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
        const selectTags = row.querySelectorAll('select');
        selectTags.forEach(select => {
            select.addEventListener('change', () => {

                const accountName = selectTags[0].value;

                const trow = select.closest('tr');
                const inputElement = trow.querySelector('input[name="transaction"]');
                const value = inputElement.value;
                if ( accountName) {
                    if (value) {
                        inputElement.removeAttribute('disabled');
                    } else {
                        inputElement.setAttribute('disabled', 'disabled');
                    }
                    sessionStorage.setItem("accountName-" + value, accountName);
                    console.log(sessionStorage)
                } else {
                    sessionStorage.removeItem("accountName-" + value);
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
            const selectTags = row.querySelectorAll('select');
            const accountName = sessionStorage.getItem("accountName-" + value);
            const checkbox = sessionStorage.getItem(value)
            if (accountName ) {
                if (checkbox) {
                    inputElement.checked = true
                }
                selectTags[0].value = accountName;
                inputElement.removeAttribute('disabled');
            } else {
                selectTags[0].value = ''; // Reset the select values if not found in sessionStorage

                inputElement.setAttribute('disabled', 'disabled');
            }
        }
    });
}


function addEventListenerToCheckboxes(checkboxes) {
    checkboxes.forEach(cb => {
        const rowData = {
            values: [],
        };
        cb.addEventListener('change', () => {
            if (cb.checked) {
                const row = cb.closest('tr');

                // Iterate over each cell and construct values in expected order
                for (let j = 0; j < row.cells.length; j++) {
                    const cell = row.cells[j];

                    // Push textual columns: Date(1), Amount(2), Invoice(3), Reference(4), Vendor ID(5)
                    if (j >= 1 && j <= 5) {
                        rowData.values.push(cell.textContent);
                        continue;
                    }

                    // Account select column
                    if (j === 6) {
                        const select = cell.querySelector('.form-select');
                        // account_name
                        rowData.values.push(select ? select.value : '');
                        // default transaction_type (since selector removed in current UI)
                        rowData.values.push('');
                        // fetch and append account details: account_no, sort_code, bicCode, bank_name
                        if (select && select.value) {
                            fetch(`account_details/?account_name=${select.value}`)
                                .then(response => response.json())
                                .then(res => {
                                    const det = res.account_details && res.account_details[0] ? res.account_details[0] : {};
                                    rowData.values.push(det.account_no || '');
                                    rowData.values.push(det.bank_code || '');
                                    rowData.values.push(det.bank_name || '');
                                })
                                .catch(() => {
                                    rowData.values.push('');
                                    rowData.values.push('');
                                    rowData.values.push('');
                                });
                        } else {
                            rowData.values.push('');
                            rowData.values.push('');

                            rowData.values.push('');
                        }

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
    combinedValues.forEach(item => {
        const tr = document.createElement('tr');
        console.log(item)
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
            `


        tableBody.appendChild(tr);
    })

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

if (processBtn){
    processBtn.addEventListener('click', (e) => {

        e.preventDefault();
        createModalTableBody('modal-table-body');
    
    });
}
if (modalSubmitBtn){
    modalSubmitBtn.addEventListener('click', (e) => {
        loader.classList.remove('d-none')
        e.preventDefault()
    ///    // Send selected invoice numbers & transaction type to server using ajax
        $.ajax({
            type: 'POST',
            url: 'post-transactions/',
            data: {
                'csrfmiddlewaretoken': getCSRFToken(),
                'transactions': JSON.stringify(combinedValues),
                'invoice_ids[]': JSON.stringify(selectedVendorsInvoiceNumber),
                'transaction_type': JSON.stringify(selectedTransactionType),
                //'account_name':JSON.stringify(selectedAccountName)
            },
            dataType: 'json',
        }).then(res => {
            loader.classList.add('d-none')
            if (res.stats !== 200) {
                Swal.fire({
                    icon: 'error',
                    title: 'Your Request Could Not Be processed:',
                    text: res.resps,
                    confirmButtonText: "OK",
                    timer: 2000,
                    footer: 'Try Again Later'
                })
                $('#post-transaction-modal').modal('hide');
            } else {
                Swal.fire({
                    icon: 'success',
                    title: 'Your Request Has Been Successfully Processed:',
                    confirmButtonText: "OK",
                    timer: 2000,
                    text: res.resps,
                }).then(() => {
                    window.location.href = 'dashboard';
                });
            }
    
        }).catch(err => console.log(err));
    
    });
}

if (searchBtn){searchBtn.addEventListener('click', (e) => {
    e.preventDefault();
    hasClickedOnSearchBtn = true;
    query_params = [searchInput.value, filterOptions.value];

    fetchSearchResults(query_params, selectedPageNumber);
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
