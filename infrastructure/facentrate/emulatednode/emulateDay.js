import plotSeatDiagram from "/infrastructure/facentrate/emulatednode/plotSeatDiagram.js";

const emulateDay = (event, configObj, wsObj, proxiedDataArrObj) => {
    if(wsObj.ws) {
        wsObj.ws.close()
    }
    event.preventDefault();
    const form = event.target.form;
    const speed = form.speed.value;
    const day = form.day.value;
    const startTime = form.startTime.value;
    const endTime = form.endTime.value;
    const seat = form.seat.value;
    console.log(day)
    wsObj.ws = new WebSocket(
        `ws://localhost:8002/ws?speed=${speed}&day=${day}&startTime=${startTime}&endTime=${endTime}&seat=${seat}&alpha=${configObj.alpha}`);
    wsObj.ws.onclose = wsOnclose;
    wsObj.ws.onmessage = (event) => wsOnmessage(event, proxiedDataArrObj, seat);
    wsObj.ws.onopen = (event) => wsOnopen(proxiedDataArrObj, seat);
}

const wsOnopen = (proxiedDataArrObj, seat) => {
    const oldData = document.getElementById("data");
    const newData = document.createElement("div");
    newData.id = "data"
    oldData?.replaceWith(newData);

    const oldLectureEvents = document.getElementById("lectureEvents");
    const newLectureEvents = document.createElement("div");
    newLectureEvents.id = "lectureEvents"
    oldLectureEvents?.replaceWith(newLectureEvents);

    proxiedDataArrObj.dataArr = []
    proxiedDataArrObj.eventArr = []
    proxiedDataArrObj.barcodeArr = []
    proxiedDataArrObj.varianceArr = []
    proxiedDataArrObj.seatHistoryArr = [],
    proxiedDataArrObj.percentageConcentration = null,
    proxiedDataArrObj.concentrationEdges = seat ? 0 : null,
    proxiedDataArrObj.wholeRoomStability = {seatsOccupiedDiffCountTotal: 0, seatsOccupiedDiffCount: []},
    proxiedDataArrObj.isVisible = false,
    proxiedDataArrObj.wasVisible = false
}

const wsOnmessage = (event, proxiedDataArrObj, seat) => {
    const dataList = document.getElementById("data");
    const dataLi = document.createElement("li")

    const lectureEvents = document.getElementById("lectureEvents");

    const seatDiagramContainer = document.getElementById("seatDiagramContainer")

    const dataObject = JSON.parse(event.data);

    const date = new Date(dataObject.acp_ts * 1000)
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    if(dataObject.type === "reading") {
        if(dataObject.readingType === "node") {

            dataObject.payload_cooked.seats_occupied.forEach(seat => {
                if (!proxiedDataArrObj.seatHistoryArr.includes(seat)) {
                    proxiedDataArrObj.seatHistoryArr.push(seat);
                }
            });
            seatDiagramContainer.replaceChild(plotSeatDiagram(dataObject.payload_cooked.seats_occupied, proxiedDataArrObj.seatHistoryArr), seatDiagramContainer.firstChild)
            
            const prevDiffCount = proxiedDataArrObj.wholeRoomStability.seatsOccupiedDiffCount[proxiedDataArrObj.wholeRoomStability.seatsOccupiedDiffCount.length-1] ?? {value: 0}
            const diffCountValue = prevDiffCount.value > 0 ? prevDiffCount.value/2 + dataObject.payload_cooked.seatsOccupiedDiffCount : dataObject.payload_cooked.seatsOccupiedDiffCount
            console.log(diffCountValue)
            proxiedDataArrObj.wholeRoomStability.seatsOccupiedDiffCount.push({value: diffCountValue, acp_ts: +dataObject.acp_ts})
            proxiedDataArrObj.wholeRoomStability.seatsOccupiedDiffCountTotal = dataObject.payload_cooked.seatsOccupiedDiffCountTotal

            dataLi.textContent = `${dataObject.payload_cooked.crowdcount} @ ${hours}:${minutes}:${seconds}`;
            dataList?.appendChild(dataLi);
            proxiedDataArrObj.push({acp_ts: dataObject.acp_ts, crowdcount: dataObject.payload_cooked.crowdcount})

            if(dataObject.payload_cooked.percent_concentration !== undefined) {  
                proxiedDataArrObj.percentageConcentration = dataObject.payload_cooked.percent_concentration
            }

            if(proxiedDataArrObj.isVisible) {
                proxiedDataArrObj.barcodeArr[proxiedDataArrObj.barcodeArr.length-1].end_acp_ts = dataObject.acp_ts
                proxiedDataArrObj.isVisible = false
                proxiedDataArrObj.wasVisible = true
            }
            if(dataObject.payload_cooked.seats_occupied.includes(seat)) {
                if(!proxiedDataArrObj.wasVisible) {
                    // init a bar
                    proxiedDataArrObj.barcodeArr.push({start_acp_ts: dataObject.acp_ts, end_acp_ts: dataObject.acp_ts})
                    proxiedDataArrObj.concentrationEdges += 1
                }
                proxiedDataArrObj.isVisible = true
            } else {
                if(proxiedDataArrObj.wasVisible) {
                    proxiedDataArrObj.concentrationEdges += 1
                    proxiedDataArrObj.wasVisible = false
                }
            }
        } 
        if (dataObject.readingType === "variance") {
            proxiedDataArrObj.varianceArr.push({...dataObject})
        }
    }
    
    if(dataObject.type === "event"){
        if(dataObject.eventType === "lectureUp") {
            proxiedDataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"lectureUp"})
            const lectureEventLi = document.createElement("li")
            lectureEventLi.textContent = `Lecture up @ ${hours}:${minutes}:${seconds}`;
            lectureEvents?.appendChild(lectureEventLi);
            proxiedDataArrObj.seatHistoryArr = []
        }
        if(dataObject.eventType === "lectureDown") {
            proxiedDataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"lectureDown"})
            const lectureEventLi = document.createElement("li")
            lectureEventLi.textContent = `Lecture down @ ${hours}:${minutes}:${seconds}`;
            lectureEvents?.appendChild(lectureEventLi);
        }
    }
};

const wsOnclose = (event) => {
    console.log('Closed');
};

export default emulateDay