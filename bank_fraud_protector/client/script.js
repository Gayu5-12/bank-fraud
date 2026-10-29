// client/script.js
const API = "http://127.0.0.1:5000";

async function sendSms() {
  const text = document.getElementById("sms_text").value;
  const userId = document.getElementById("user_id").value || "user1";
  const res = await fetch(API + "/receive_sms", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId, from: "BANK", text: text})
  });
  const data = await res.json();
  document.getElementById("sms_result").innerText = JSON.stringify(data, null, 2);
}

async function openLink() {
  const url = document.getElementById("open_url").value;
  const userId = document.getElementById("user_id").value || "user1";
  const res = await fetch(API + "/open_link", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId, url: url})
  });
  const data = await res.json();
  document.getElementById("open_result").innerText = JSON.stringify(data, null, 2);
}

async function initiateTransfer() {
  const to_account = document.getElementById("to_account").value;
  const amount = document.getElementById("amount").value;
  const userId = document.getElementById("user_id").value || "user1";
  const res = await fetch(API + "/initiate_transfer", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId, to_account: to_account, amount: amount})
  });
  const data = await res.json();
  document.getElementById("transfer_result").innerText = JSON.stringify(data, null, 2);
  if (data.session_id) {
    document.getElementById("session_id").value = data.session_id;
  }
}

async function confirmTransfer() {
  const session = document.getElementById("session_id").value;
  const otp = document.getElementById("otp").value;
  const approve = document.getElementById("approve_ben").checked;
  const res = await fetch(API + "/confirm_transfer", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({session_id: session, otp: otp, approve_beneficiary: approve})
  });
  const data = await res.json();
  document.getElementById("otp_result").innerText = JSON.stringify(data, null, 2);
}

async function getStatus() {
  const userId = document.getElementById("user_id").value || "user1";
  const res = await fetch(API + "/status/" + encodeURIComponent(userId));
  const data = await res.json();
  document.getElementById("status_area").innerText = JSON.stringify(data, null, 2);
}

async function unfreeze() {
  const userId = document.getElementById("user_id").value || "user1";
  const res = await fetch(API + "/unfreeze", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_id: userId})
  });
  const data = await res.json();
  alert("Unfreeze: " + JSON.stringify(data));
}
