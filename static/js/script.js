// script.js
let client
let stationId = document.getElementById("stationId").textContent
let statusMessage = document.getElementById("statusMessage")
let startButton = document.getElementById("startButton")
let stopButton = document.getElementById("stopButton")
const energyValue = document.getElementById("energy-value")
let timeCounter = document.getElementById("time")
let sessionId = document.getElementById("sessionId")
let elementEnergy = document.getElementById("energy-rate")
let userMoney = document.getElementById("user-money")
let moneyValue = document.getElementById("money-value")
let energyConsumed = 0
let interval
let charging = false
let chargingSessionsId = ""
let money = 0
let chargingCost = 0

// Connect to MQTT Broker
function connectToBroker() {
    client = new Paho.MQTT.Client("broker.hivemq.com", 8000, stationId) // Change to your MQTT broker details
    client.onConnectionLost = onConnectionLost
    client.onMessageArrived = onMessageArrived
    client.connect({ onSuccess: onConnect })
}

function onConnect() {
    console.log("Connected to MQTT broker")
    client.subscribe("charging/" + stationId) // Subscribe to topic
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("Connection lost: " + responseObject.errorMessage)
    }
}

function onMessageArrived(message) {
    // {"boothId":"df859aad-20db-4454-82fb-9f121c3fc73b","sessionsId":"f27c2950-67f2-4d39-a7d3-3d483ee4262d","money":10,"command":"start"}
    // decode json message
    let msg = JSON.parse(message.payloadString)
    console.log(msg.sessionsId)
    if (msg.command === "start") {
        chargingSessionsId = msg.sessionsId
        // console.log(chargingSessionsId)
        sessionId.textContent = chargingSessionsId
        console.log(sessionId.textContent)
        money = msg.money
        userMoney.textContent = money
        statusMessage.innerHTML = "Charging session started."
        startCharging()
    }
    if (msg.command === "stop") {
        stopCharging()
    }
}

function sendMQTTMessage(senderMessage) {
    if (!client.isConnected()) {
        return
    }
    let message = new Paho.MQTT.Message(senderMessage)
    message.destinationName = "charging/" + stationId
    client.send(message)
}

// Generate QR code for station ID
let qr = new QRious({
    element: document.getElementById("qrCode"),
    size: 150,
    value: stationId,
})

// Connect to WebSocket
let socket = new WebSocket(
    "ws://ecocharge.azurewebsites.net/charging_sessions/ws/" + stationId + "/"
)
let boothStatus = new WebSocket(
    "ws://ecocharge.azurewebsites.net/charging_booth/ws/" + stationId + "/"
)

socket.onopen = function () {
    console.log("Connection established.")
}

socket.onmessage = function (event) {
    // Here you can handle incoming messages
    console.log("Message from server: " + event.data)
}

boothStatus.onopen = function () {
    console.log("Booth is online.")
}

connectToBroker()
startButton.onclick = startCharging

function startCharging() {
    if (charging) {
        console.log("Charging already started.")
        return
    }
    charging = true
    clearValues()
    statusMessage.innerHTML = "Charging started..."
    interval = setInterval(async () => {
        // timer show 00:00
        let time = timeCounter.textContent.split(":")
        let minutes = parseInt(time[0])
        let seconds = parseInt(time[1])
        seconds++
        if (seconds === 60) {
            minutes++
            seconds = 0
        }
        timeCounter.textContent = `${minutes < 10 ? "0" + minutes : minutes}:${
            seconds < 10 ? "0" + seconds : seconds
        }`
        energyRate = Math.random() * 0.1
        elementEnergy.textContent = `${energyRate.toFixed(2)} Watt/sec`
        // if (energyConsumed < 0) {
        //     stopCharging()
        //     return
        // }
        energyConsumed += energyRate
        energyValue.textContent = `${energyConsumed.toFixed(2)} kWh`

        chargingCost = energyConsumed * 7.5
        chargingCost = chargingCost.toFixed(2)
        moneyValue.textContent = chargingCost
        // Charge equal to the money you have.

        // Send energy consumed to server
        await socket.send(
            JSON.stringify({
                boothId: stationId,
                sessionsId: sessionId.textContent,
                power: energyConsumed.toFixed(2),
                action: "start",
            })
        )
        await boothStatus.send(
            JSON.stringify({
                status: "charging",
                rate: energyRate.toFixed(2),
            })
        )
        if (chargingCost > (money - 0.4).toFixed(2) || chargingCost > money) {
            stopCharging()
            return
        }
    }, 1000)
    // Send start charging message to server
}

stopButton.onclick = stopCharging

function stopCharging() {
    if (!charging) {
        console.log("Charging already stopped.")
        return
    }
    charging = false
    // stop Interval
    clearInterval(interval)
    console.log("Charging stopped.")
    statusMessage.innerHTML = "Charging stopped."
    // Send stop charging message to server
    socket.send(
        JSON.stringify({
            boothId: stationId,
            sessionsId: sessionId.textContent,
            power: energyConsumed.toFixed(2),
            action: "stop",
        })
    )
    boothStatus.send(
        JSON.stringify({
            status: "online",
        })
    )
}

function clearValues() {
    energyValue.textContent = "0.00 kWh"
    timeCounter.textContent = "00:00"
    elementEnergy.textContent = "0.00 Watt/sec"
    moneyValue.textContent = "0.00"
    chargingSessionsId = ""
    energyConsumed = 0
}
