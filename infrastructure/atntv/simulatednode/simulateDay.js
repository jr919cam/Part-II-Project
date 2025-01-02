const simulateDay = (event, configObj, wsObj, proxiedDataArrObj) => {
    if(wsObj.ws) {
        wsObj.ws.close()
        console.log("closed")
    }
    event.preventDefault();
    const form = event.target.form;
    const day = form.day.value;
    const startTime = form.startTime.value;
    const seat = form.seat.value;
    console.log(day)
    wsObj.ws = new WebSocket(`ws://localhost:8002/ws?speed=${configObj.speed}&day=${day}&startTime=${startTime}&alpha=${configObj.alpha}`);
    wsObj.ws.onclose = wsOnclose;
    wsObj.ws.onmessage = (event) => wsOnmessage(event, proxiedDataArrObj);
    wsObj.ws.onopen = (event) => wsOnopen(proxiedDataArrObj);
}

const wsOnopen = (proxiedDataArrObj) => {
    const oldData = document.getElementById("data");
    const newData = document.createElement("div");
    newData.id = "data"
    oldData?.replaceWith(newData);

    const oldLectureEvents = document.getElementById("lectureEvents");
    const newLectureEvents = document.createElement("div");
    newLectureEvents.id = "lectureEvents"
    oldLectureEvents?.replaceWith(newLectureEvents);

    proxiedDataArrObj.dataArr = []
}

const wsOnmessage = (event, proxiedDataArrObj) => {
    const dataList = document.getElementById("data");
    const dataLi = document.createElement("li")

    const lectureEvents = document.getElementById("lectureEvents");

    const dataObject = JSON.parse(event.data);

    const date = new Date(dataObject.acp_ts * 1000)
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    if(dataObject.type === "reading") {
        dataLi.textContent = `${dataObject.payload_cooked.crowdcount} @ ${hours}:${minutes}:${seconds}`;
        dataList?.appendChild(dataLi);
        proxiedDataArrObj.push({acp_ts: dataObject.acp_ts, crowdcount: dataObject.payload_cooked.crowdcount})
    }
    
    if(dataObject.type === "event"){
        const lectureEventLi = document.createElement("li")
        lectureEventLi.textContent = `Boundary @ ${hours}:${minutes}:${seconds}`;
        lectureEvents?.appendChild(lectureEventLi);
        proxiedDataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"boundary"})
    }
};

const wsOnclose = (event) => {
    console.log('Closed');
};

export default simulateDay