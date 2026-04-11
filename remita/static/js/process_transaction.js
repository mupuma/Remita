const processBtn = document.getElementById('process-btn');
const searchBtn = document.getElementById('search-button');
const modalSubmitBtn = document.getElementById('modal-submit-btn');
const loader = document.getElementById('spinner');
const rows = document.querySelectorAll('#table-body tr, .transaction-table-body tr');
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const searchInput = document.getElementById('search-input');
const filterOptions = document.getElementById('filter-options');

var isScrolledToTop = true;
let selectedVendorsInvoiceNumber = [];
let selectedPageNumber = 1;
let numberOfPages = 0;
let hasClickedOnSearchBtn = false;
let query_params = [];
let selectedTransactionType = {};
let combinedValues = [];

sessionStorage.clear();

// On page load: restore checkbox checked state from sessionStorage.
// Enabling/disabling is now handled entirely by the beneficiary dropdown's
// change handler — we only restore the checked tick here.
addCheckBoxandSelectValues(rows);
addEventListenerToCheckboxes(checkboxes);
addEventListenerToAnchorTag();

// ------------------------------------------------------------
// Checkbox state restoration (checked tick only — not enabled/disabled)
// Enabled state is controlled by the beneficiary dropdown JS
// ------------------------------------------------------------
function addCheckBoxandSelectValues(rows) {
    rows.forEach(row => {
        if (row.id) {
            const value = row.id;
            const inputElement = row.querySelector('input[name="transaction"]');
            if (!inputElement) return;
            const wasChecked = sessionStorage.getItem(value);
            if (wasChecked === 'true') {
                inputElement.checked = true;
                // Don't call removeAttribute('disabled') here —
                // the dropdown hasn't loaded yet at this point.
                // The dropdown's change event enables it on selection.
            }
        }
    });
}

// ------------------------------------------------------------
// Checkbox event listeners
// ------------------------------------------------------------
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
                const tbody = row ? row.closest('tbody') : null;
                if (tbody) {
                    rowData.project_id = parseInt(tbody.dataset.projectId || '1', 10);
                    rowData.project_name = tbody.dataset.projectName || '';
                }

                for (let j = 0; j < row.cells.length; j++) {
                    const cell = row.cells[j];

                    // Columns 1–5: Date, Amount, Invoice, Reference, Vendor ID
                    if (j >= 1 && j <= 5) {
                        rowData.values.push(cell.textContent.trim());
                        continue;
                    }

                    // Column 6: Beneficiary Account — read from hidden fields
                    if (j === 6) {
                        const beneficiaryEl = cell.querySelector('.beneficiary-account');
                        let accountName = '', accountNo = '', bankCode = '', bankName = '';

                        if (beneficiaryEl) {
                            accountName = (beneficiaryEl.querySelector('.account-name-input')?.value || '').trim();
                            accountNo   = (beneficiaryEl.querySelector('.account-no-input')?.value   || '').trim();
                            bankCode    = (beneficiaryEl.querySelector('.bank-code-input')?.value    || '').trim();
                            bankName    = (beneficiaryEl.querySelector('.bank-name-input')?.value    || '').trim();
                        }

                        rowData.values.push(accountName); // index 6
                        rowData.values.push('');           // index 7 — transaction_type placeholder
                        rowData.values.push(accountNo);    // index 8
                        rowData.values.push(bankCode);     // index 9
                        rowData.values.push(bankName);     // index 10
                    }
                    // Column 0 (checkbox) and 7 (actions) are skipped
                }

                // Deduplicate by invoice ID (index 2 = IDINVC)
                const invoiceId = cb.value;
                combinedValues = combinedValues.filter(item => item?.values?.[2] !== invoiceId);
                combinedValues.push(rowData);

                if (processBtn) processBtn.removeAttribute('disabled');

                addSelectedVendorsInvoiceNumber(cb.value);
                sessionStorage.setItem(cb.value, 'true');
                saveSelectedRows();

            } else {
                const value = cb.value;
                removeSelectedVendorsInvoiceNumber(value);
                sessionStorage.removeItem(value);
                combinedValues = combinedValues.filter(item => item?.values?.[2] !== value);
                saveSelectedRows();

                const anyChecked = document.querySelectorAll(
                    '#table-body input[type="checkbox"]:checked, .transaction-table-body input[type="checkbox"]:checked'
                ).length > 0;

                if (processBtn) {
                    anyChecked
                        ? processBtn.removeAttribute('disabled')
                        : processBtn.setAttribute('disabled', 'disabled');
                }
            }

            console.log('combinedValues:', combinedValues);
        });
    });
}

// ------------------------------------------------------------
// Scroll helpers
// ------------------------------------------------------------
function scrollToTopOrBottom() {
    if (isScrolledToTop) { scrollToBottom(); isScrolledToTop = false; }
    else                  { scrollToTop();   isScrolledToTop = true;  }
}
function scrollToTop()    { window.scrollTo({ top: 0,                                        behavior: 'smooth' }); }
function scrollToBottom() { window.scrollTo({ top: document.documentElement.scrollHeight,    behavior: 'smooth' }); }

// ------------------------------------------------------------
// Selected invoice tracking
// ------------------------------------------------------------
function addSelectedVendorsInvoiceNumber(invoiceId) {
    if (!selectedVendorsInvoiceNumber.includes(invoiceId))
        selectedVendorsInvoiceNumber.push(invoiceId);
}
function removeSelectedVendorsInvoiceNumber(invoiceId) {
    const index = selectedVendorsInvoiceNumber.indexOf(invoiceId);
    if (index !== -1) selectedVendorsInvoiceNumber.splice(index, 1);
}

// ------------------------------------------------------------
// Save selected rows / transaction types
// ------------------------------------------------------------
function saveSelectedRows() {
    document.querySelectorAll('#table-body tr, .transaction-table-body tr').forEach(row => {
        const cb = row.querySelector('td input[type="checkbox"]');
        if (cb && cb.checked) {
            const typeEl = row.querySelector('td select[name="transaction_type"]');
            selectedTransactionType[cb.value] = typeEl ? typeEl.value : 'IFT';
        }
    });
}

// ------------------------------------------------------------
// Modal table body builder
// ------------------------------------------------------------
function createModalTableBody(tableBodyID) {
    const tableBody = document.getElementById(tableBodyID);
    if (!tableBody) return;
    tableBody.innerHTML = '';

    // Group by project_id
    const groups = {};
    combinedValues.forEach(item => {
        const pid = item.project_id || 0;
        if (!groups[pid]) groups[pid] = { name: item.project_name || ('Project ' + pid), items: [] };
        groups[pid].items.push(item);
    });

    Object.keys(groups).forEach(pid => {
        const group = groups[pid];

        const headerRow = document.createElement('tr');
        headerRow.innerHTML = `<td colspan="7" class="fw-bold bg-light">${group.name} (Project ID: ${pid})</td>`;
        tableBody.appendChild(headerRow);

        group.items.forEach(item => {
            const accountName = item.values[6]  || 'N/A';
            const accountNo   = item.values[8]  || 'N/A';
            const bankCode    = item.values[9]  || 'N/A';
            const bankName    = item.values[10] || 'N/A';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.values[0] || ''}</td>
                <td>${item.values[1] || ''}</td>
                <td>${item.values[2] || ''}</td>
                <td>${item.values[3] || ''}</td>
                <td>${item.values[4] || ''}</td>
                <td>${accountName} — ${accountNo}</td>
                <td>${bankCode} (${bankName})</td>
            `;
            tableBody.appendChild(tr);
        });
    });

    // Transaction count badge
    const countBadge = document.getElementById('transaction-count');
    const count = combinedValues.length;
    if (countBadge) countBadge.innerHTML = `<i class="bi bi-check-circle me-1"></i>${count} Transaction${count !== 1 ? 's' : ''}`;

    // No-transactions message
    const noMsg = document.getElementById('no-transactions-message');
    if (noMsg) noMsg.style.display = count > 0 ? 'none' : 'block';

    // Modal submit button
    if (modalSubmitBtn) {
        count > 0
            ? modalSubmitBtn.removeAttribute('disabled')
            : modalSubmitBtn.setAttribute('disabled', 'disabled');
    }
}

// ------------------------------------------------------------
// Pagination
// ------------------------------------------------------------
function handleClick(event) {
    event.preventDefault();
    const url = event.target.getAttribute('href');
    fetch(url)
        .then(r => r.text())
        .then(html => {
            updateTableAndPaginator(html);
            addEventListenerToAnchorTag();
        });
}

function addEventListenerToAnchorTag() {
    document.querySelectorAll('.custom-pagination a').forEach(link => {
        link.addEventListener('click', handleClick);
    });
}

function updateTableAndPaginator(html) {
    const parser = new DOMParser();
    const newDoc = parser.parseFromString(html, 'text/html');

    const newRows       = newDoc.querySelectorAll('#table-body tr');
    const newCheckboxes = newDoc.querySelectorAll('input[type="checkbox"]');
    const newTable      = newDoc.getElementById('table-body');
    const newPaginator  = newDoc.getElementById('paginator');

    addCheckBoxandSelectValues(newRows);
    addEventListenerToCheckboxes(newCheckboxes);

    if (newTable)     document.getElementById('table-body')?.replaceWith(newTable);
    if (newPaginator) document.getElementById('paginator')?.replaceWith(newPaginator);
}

function fetchSearchResults(queryParams, page) {
    const [searchParam, filterParam] = queryParams;
    fetch(`/remita/search/?search_params=${searchParam}&filter_options=${filterParam}&page=${page}`)
        .then(r => r.text())
        .then(html => {
            const parser    = new DOMParser();
            const newDoc    = parser.parseFromString(html, 'text/html');
            const newRows   = newDoc.querySelectorAll('#table-body tr');
            const newCBs    = newDoc.querySelectorAll('input[type="checkbox"]');
            const newTable  = newDoc.getElementById('table-body');
            const newPager  = newDoc.getElementById('paginator');

            numberOfPages = parseInt(newPager?.dataset.numPages || '1', 10);

            addCheckBoxandSelectValues(newRows);
            addEventListenerToCheckboxes(newCBs);

            document.getElementById('table-body')?.replaceWith(newTable);
            document.getElementById('paginator')?.replaceWith(newPager);
            updatePaginationLinks(newPager);
        })
        .catch(err => console.error('Search error:', err));
}

async function goToPage() {
    try { fetchSearchResults(query_params, selectedPageNumber); }
    catch (err) { console.error(err); }
}

function updatePaginationLinks(newDoc) {
    const map = { '#next': nextPageLink, '#first': firstPageLink, '#last': lastPageLink, '#previous': previousPageLink };
    Object.entries(map).forEach(([sel, fn]) => {
        const el = newDoc?.querySelector(sel);
        if (el) fn(el);
    });
}

function nextPageLink(el) {
    el.addEventListener('click', e => {
        if (!hasClickedOnSearchBtn) return;
        e.preventDefault();
        if (selectedPageNumber < numberOfPages) selectedPageNumber++;
        goToPage();
    });
}
function previousPageLink(el) {
    el.addEventListener('click', e => {
        if (!hasClickedOnSearchBtn) return;
        e.preventDefault();
        if (selectedPageNumber > 1) selectedPageNumber--;
        goToPage();
    });
}
function lastPageLink(el) {
    el.addEventListener('click', e => {
        if (!hasClickedOnSearchBtn) return;
        e.preventDefault();
        selectedPageNumber = numberOfPages;
        goToPage();
    });
}
function firstPageLink(el) {
    el.addEventListener('click', e => {
        if (!hasClickedOnSearchBtn) return;
        e.preventDefault();
        selectedPageNumber = 1;
        goToPage();
    });
}

// ------------------------------------------------------------
// Batch ref generation
// ------------------------------------------------------------
function generateBatchRef() {
    const ts   = new Date().toISOString().replace(/[-T:.Z]/g, '').slice(0, 14);
    const rand = Math.random().toString(36).slice(2, 8).toUpperCase();
    return `BR-${ts}-${rand}`;
}

// ------------------------------------------------------------
// Modal show/hide hooks
// ------------------------------------------------------------
$(document).ready(function () {
    const $modal = $('#post-transaction-modal');
    if ($modal.length) {
        $modal.on('show.bs.modal', function () {
            $('#batch-ref-input').val(generateBatchRef());
            $('#batch-desc-input').val('');
            createModalTableBody('modal-table-body');
        });
        $modal.on('hidden.bs.modal', function () {
            $('#batch-ref-input').val('');
            $('#batch-desc-input').val('');
        });
    }
});

// ------------------------------------------------------------
// Process button
// ------------------------------------------------------------
if (processBtn) {
    processBtn.addEventListener('click', e => {
        e.preventDefault();
        createModalTableBody('modal-table-body');
    });
}

// ------------------------------------------------------------
// Modal submit button
// ------------------------------------------------------------
if (modalSubmitBtn) {
    modalSubmitBtn.addEventListener('click', e => {
        e.preventDefault();
        loader?.classList.remove('d-none');

        const freshBatchRef = generateBatchRef();
        const batchRefInput = document.getElementById('batch-ref-input');
        if (batchRefInput) batchRefInput.value = freshBatchRef;

        const batchDesc = document.getElementById('batch-desc-input')?.value || '';

        const txRefsMap = {};
        const ts       = new Date().toISOString().replace(/[-T:.Z]/g, '').slice(0, 14);
        const baseRand = Math.random().toString(36).slice(2, 8).toUpperCase();
        combinedValues.forEach((item, idx) => {
            const invoiceId = item?.values?.[2] ?? `IDX${idx}`;
            txRefsMap[invoiceId] = `TR-${ts}-${baseRand}-${String(idx + 1).padStart(3, '0')}`;
        });

        const sourceBankId = document.getElementById('source-bank-select')?.value || '';

        $.ajax({
            type: 'POST',
            url: 'post-transactions/',
            data: {
                csrfmiddlewaretoken: getCSRFToken(),
                transactions:        JSON.stringify(combinedValues),
                'invoice_ids[]':     JSON.stringify(selectedVendorsInvoiceNumber),
                transaction_type:    JSON.stringify(selectedTransactionType),
                batch_ref:           freshBatchRef,
                narration:           batchDesc,
                transaction_refs:    JSON.stringify(txRefsMap),
                source_bank_id:      sourceBankId,
            },
            dataType: 'json',
        })
        .done(res => {
            loader?.classList.add('d-none');
            $('#post-transaction-modal').modal('hide');

            const extractMessage = p => {
                if (!p) return '';
                const d = p.data || {};
                return p.message || d.message || d.responseMessage || d.statusMessage || d.status || p.error || '';
            };

            Swal.fire({
                icon:              res.success ? 'success' : 'error',
                title:             res.success ? 'Transaction processing' : 'Transaction failed',
                text:              extractMessage(res) || 'Request processed.',
                confirmButtonText: 'OK',
            }).then(() => { if (res.success) window.location.href = 'dashboard'; });
        })
        .fail(xhr => {
            loader?.classList.add('d-none');
            $('#post-transaction-modal').modal('hide');

            let payload = null;
            try { payload = xhr.responseJSON ?? JSON.parse(xhr.responseText); } catch (_) {}
            const d   = payload?.data ?? {};
            const msg = payload?.message || payload?.error || d.message || d.responseMessage || d.statusMessage || d.status || 'Your request could not be processed.';

            Swal.fire({ icon: 'error', title: 'Transaction failed', text: msg, confirmButtonText: 'OK', footer: 'Try again later' });
        });
    });
}

// ------------------------------------------------------------
// Search button
// ------------------------------------------------------------
if (searchBtn) {
    searchBtn.addEventListener('click', e => {
        e.preventDefault();
        const q = encodeURIComponent(searchInput?.value || '');
        const f = encodeURIComponent(filterOptions?.value || '');
        window.location.href = `/remita/search/?search_params=${q}&filter_options=${f}`;
    });
}

// ------------------------------------------------------------
// Filter options — Flatpickr date picker
// ------------------------------------------------------------
if (filterOptions) {
    filterOptions.addEventListener('change', () => {
        if (!searchInput) return;
        searchInput.removeAttribute('readonly');

        if (searchInput._flatpickr) {
            searchInput._flatpickr.destroy();
            delete searchInput._flatpickr;
        }

        if (filterOptions.value === 'date') {
            searchInput._flatpickr = flatpickr(searchInput, { dateFormat: 'Ymd' });
        }
    });
}

// ------------------------------------------------------------
// CSRF helper
// ------------------------------------------------------------
function getCSRFToken() {
    const fromCookie = document.cookie.split('; ').find(r => r.startsWith('csrftoken='));
    if (fromCookie) return fromCookie.split('=')[1];
    return document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
}
