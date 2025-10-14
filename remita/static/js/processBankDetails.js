const sortCde = document.getElementById('sort_code');
const accountname = document.getElementById('accountname')
const bankNameInput = document.getElementById('bank_name')
const branchNameInput = document.getElementById('branch');
const submitBtn = document.getElementById('submit')
const accInput = document.getElementById('account_no')
const errorList = document.getElementById('acc_error');
const vendor = document.getElementById('vendor_id')
let groupedData = {};
const selectedBank = []

service_IDs = {
    'ATLAS MARA': 347,
    'AB BANK': 329,
    'ACCESS BANK': 332,
    'ABSA': 377,
    'BANK OF CHINA': 317,
    'FIRST CAPITAL': 314,
    'CITIBANK': 368,
    'ECOBANK': 320,
    'FIRST ALLIANCE BANK': 326,
    'FNB ZAMBIA': 383,
    'INDO ZAMBIA': 371,
    'INVESTRUST BANK PLC': 380,
    'STANCHART': 362,
    'STANBIC': 374,
    'UBA': 323,
    'ZANACO': 359,
    'ZNBS': 356
}
let bankN = null
loadBankList();

vendor.addEventListener('blur',(e)=>{
    verifyVendor(e.target.value)
})
sortCde.addEventListener('blur', (e)=>{
            const currentValue = e.target.value     
            searchBySortCode(currentValue);
            accInput.removeAttribute('readonly')
       
        });
accInput.addEventListener('blur', (ev)=>{
    const accountNo= ev.target.value
    const vendor_id = vendor.value
    checkAccountNumber(accountNo,vendor_id)
});

function searchBySortCode(sortC) {
    const bankDetails = document.getElementById('bankDetailDiv');
    // Assuming groupedData is the object of arrays of objects
  
    for (const bankEntries of Object.values(groupedData)) {
      const entry = bankEntries.find((entry) => entry.sortCode === sortC);
      if (entry) {
        // Update bank details
        sortCde.value = entry.sortCode;
        bankDetails.classList.remove('d-none');
        branchNameInput.value = entry.branchDesc;
        bankNameInput.value = entry.bankName;
        submitBtn.removeAttribute('disabled');
        return; // Exit the function once the entry is found
      }
    }
  
    // If the sort code is not found, handle default cases
    if (sortC === '140001') {
        bankDetails.classList.remove('d-none');
      branchNameInput.value = 'LUSAKA MAIN BRANCH';
      bankNameInput.value = 'ZICB';
      sortCde.value = sortC;
    } else if (sortC === '140000') {
        bankDetails.classList.remove('d-none');
      branchNameInput.value = 'HEAD OFFICE';
      bankNameInput.value = 'ZICB';
      sortCde.value = sortC;
    } else if (sortC === '140202') {
        bankDetails.classList.remove('d-none');
      branchNameInput.value = 'ECL MALL BRANCH';
      bankNameInput.value = 'ZICB';
      sortCde.value = sortC;
    } else {
      // Reset the bank details
      branchNameInput.value = '';
      bankNameInput.value = '';
      sortCde.value = '';
    }
  }
function verifyVendor(vendor) {
    const ul = document.getElementById('errorlist');
    if (ul) {
        ul.remove(); // Clear any previous error messages
    }
    fetch(`verify_vendor/?vendor_id=${vendor}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.response === false) {
                const div = document.getElementById('vid');
                const ul = document.createElement('ul');
                const li = document.createElement('li');
                ul.setAttribute('id', 'errorlist');
                li.textContent = 'No Matching Vendor Available';
                ul.appendChild(li);
                div.appendChild(ul);
                ul.style.paddingLeft = '2rem';
                ul.style.marginTop = '0px';
            } else {
                sortCde.removeAttribute('readonly');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle the error, e.g., display a generic error message
        });
}
function checkAccountNumber(accN,vendor){
    const ul = document.getElementById('errorlist');
    if (ul) {
        ul.remove(); // Clear any previous error messages
    }
    fetch(`verify_account/?account_no=${accN}&vendor_id=${vendor}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok')};
        
        return response.json()})
    .then(data=>{
        console.log(data)
        if (data.response===true){
            const div = document.getElementById('acc');
            const ul = document.createElement('ul');
            const li = document.createElement('li');
            ul.setAttribute('id','errorlist')
            li.textContent = 'Vendor already exists';
            ul.appendChild(li);
            div.appendChild(ul);
            ul.style.paddingLeft = '2rem';
            ul.style.marginTop = '0px';
            
        }
        else
        {
            handleAccInputBlur(accN)
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle the error, e.g., display a generic error message
    });
}
function handleAccInputBlur(accountNo) {
    if (bankN !== ""){
        const bankN= bankNameInput.value.toUpperCase()
        if (bankN === 'ZICB'){
            fetch(`verify_account/zicb?account_no=${accountNo}`)
            .then(response => response.json())
            .then(data=>{
                console.log(data.response)
                if(data.response !== false){
                    accountname.value = data.response[0].accountTitle
                    branchNameInput.value = data.response[0].brnCode  
                    submitBtn.removeAttribute('disabled') 
                }
                else
                {
                    accInput.value = ''
                    accountname.value = ''
                    branchNameInput.value = ''
                    bankNameInput.value = ''
                    submitBtn.setAttribute('disabled','disabled')
                }})
            }
            
        else
        {
            if (bankN in service_IDs)
            {
            const service_id = service_IDs[bankN]
            fetch(`verify_account/other?account_no=${accountNo}&service_id=${service_id}`)
            .then(response => response.json())
            .then(data =>{
                if(data.response !== false){
                    accountname.value = data.response[0].customerName
                    submitBtn.removeAttribute('disabled') 
                }
                else
                {
                    accInput.value = ''
                    accountname.value = ''
                    branchNameInput.value = ''
                    bankNameInput.value = ''
                    submitBtn.setAttribute('disabled','disabled')
                }})
            }
            else
            {
                const prevUl = document.getElementById('errorlist');
                if (prevUl) {
                    prevUl.remove(); // Clear any previous error messages
                }
                    const div = document.getElementById('acc');
                    const ul = document.createElement('ul');
                    const li = document.createElement('li');
                    ul.setAttribute('id', 'errorlist');
                    li.textContent = 'Account Number Cannot be Verified';
                    ul.appendChild(li);
                    div.appendChild(ul);
                    ul.style.paddingLeft = '2rem';
                    ul.style.marginTop = '0px'; 
                    submitBtn.removeAttribute('disabled')    
            }
    }
        }

    }

  



// Attach the event listener to the input field


function loadBankList() {
    fetch('/bank_details/upload/loadBanks/')
        .then(response => response.json())
        .then(data => {
                // Group the data by bank
                data.forEach(entry => {
                    const bankName = entry.bankName;
                    if (!groupedData[bankName]) {
                        groupedData[bankName] = [];
                    }
                    groupedData[bankName].push(entry);

                });
                
               
            }
        )
        .catch(error => {
            console.error(error);
        });
}

function addBankServiceID(bank) {
    if (selectedBank === []) {
        selectedBank.push(bank)
    } else {
        selectedBank[0] = bank
    }
}


