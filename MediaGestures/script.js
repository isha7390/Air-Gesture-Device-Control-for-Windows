let leftHand =[];
let rightHand =[];
let actions =[];
let fingers=[];

const popup = document.getElementById('details');
const open = document.getElementById('oButton');
const close = document.getElementById('cButton');
const settings = document.getElementById('settings')
const sButton = document.getElementById('sButton')
const saveButton = document.getElementById('save')
const rightDrop = document.getElementById('right-hand')
const leftDrop = document.getElementById('left-hand')
const actionDrop = document.getElementById('action')
const fingerDrop = document.getElementById('finger')
const gestureDetail = document.getElementById('gesture-list')
const actionDetail = document.getElementById('action-list')
const start = document.getElementById('start')
let camPreview;

open.addEventListener('click', () =>{
    console.log("this is supposed to open");
    popup.showModal();
});

close.addEventListener('click', () =>{
    popup.close();
});

sButton.addEventListener('click', () =>{
    console.log("this is supposed to open");
    settings.showModal();
});

sCButton.addEventListener('click', () =>{
    console.log("this is supposed to open");
    settings.close();
});

saveButton.addEventListener('click', ()=>{
    console.log("save has been called");
    const right = rightDrop.value;
    const left = leftDrop.value;
    const action = actionDrop.value;
    const finger = fingerDrop.value;

    let drops = [right, left,finger, action];
    let dropId = ['rightVal', 'leftVal','fingerVal', 'actionVal']

    if(right == "" ||left == "" || action == "" || finger =="")
    {
        for(let i = 0; i < 3 ;i++){
            if(drops[i]== ""){
                errorMessage(dropId[i]);
                console.log("msg is empty");
            }
        }

    }
    else{
        leftHand.push(left);
        rightHand.push(right);
        actions.push(action);
        fingers.push(finger)

        console.log(left+", "+right+", "+action+", "+finger);
        updateDetails();
        popup.close();
        rightDrop.value = "";
        leftDrop.value = "";
        actionDrop.value = "";
        fingerDrop.value="";
        console.log(left+", "+right+", "+action);
        const leftVal = document.getElementById('leftVal');
        const rightVal = document.getElementById('rightVal');
        const actionVal = document.getElementById('actionVal');
        const fingerVal = document.getElementById('fingerVal')

        leftVal.textContent ="";
        rightVal.textContent ="";
        actionVal.textContent ="";
        fingerVal.textContent ="";


    }

   
})

function updateDetails() {
    gestureDetail.innerHTML="";
    for (let i = 0; i < leftHand.length; i++) {
        
        const text = "Left: "+leftHand[i]+"   Right: "+rightHand[i];
        const li = document.createElement('li');
        li.textContent = text;
        gestureDetail.appendChild(li)
    }

    actionDetail.innerHTML ="";
    actions.forEach(a =>{
        const li = document.createElement('li');
        li.textContent = a;
        actionDetail.appendChild(li);
    })

}

function errorMessage(area) {
    const drop = document.getElementById(area);
    drop.textContent = "Please select a value!";

}


start.addEventListener('click', () => {
    console.log("the button has been pressed");
    const data = {left: leftHand, right: rightHand,finger:fingers, action: actions};
    fetch('http://127.0.0.1:5000/receive-data', {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => console.log("Sent successfully!"))
    .catch(error => console.error("Error sending:", error));

});






