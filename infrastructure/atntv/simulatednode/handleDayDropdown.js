const handleDayDropdown = (event, spansObj, configObj, timestampObj, crowdCountObj, wsObj, proxiedDataArrObj) => {
    if(wsObj.ws) {
        wsObj.ws.close()
        console.log("closed")
    }
    const day = event.target.value
    console.log(day)
    wsObj.ws = new WebSocket(`ws://localhost:8002/ws?speed=${configObj.speed}&day=${day}`);
    wsObj.ws.onclose = wsOnclose;
    wsObj.ws.onmessage = (event) => wsOnmessage(event, spansObj, timestampObj, crowdCountObj, configObj.alpha, proxiedDataArrObj);
    wsObj.ws.onopen = (event) => wsOnopen(event, proxiedDataArrObj);
}

const wsOnopen = (event, proxiedDataArrObj) => {
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

const wsOnmessage = (event, spansObj, timestampObj, crowdCountObj, alpha, proxiedDataArrObj) => {
    const dataList = document.getElementById("data");
    const dataLi = document.createElement("li")

    const lectureEvents = document.getElementById("lectureEvents");

    const dataObject = JSON.parse(event.data);

    const date = new Date(dataObject.acp_ts * 1000)
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    dataLi.textContent = `${dataObject.payload_cooked.crowdcount} @ ${hours}:${minutes}:${seconds}`;
    dataList?.appendChild(dataLi);

    proxiedDataArrObj.push({acp_ts: dataObject.acp_ts, crowdcount: dataObject.payload_cooked.crowdcount})

    crowdCountObj.diffCrowdCount = crowdCountObj.prevCrowdCount ? dataObject.payload_cooked.crowdcount - crowdCountObj.prevCrowdCount : 0;
    crowdCountObj.prevCrowdCount = dataObject.payload_cooked.crowdcount;

    timestampObj.diffts = timestampObj.prevts ? dataObject.acp_ts - timestampObj.prevts : 0;
    timestampObj.prevts = dataObject.acp_ts
    if(timestampObj.timeSinceLectureEvent !== undefined){
        timestampObj.timeSinceLectureEvent = timestampObj.timeSinceLectureEvent + timestampObj.diffts
    }
    crowdCountObj.EMA = alpha * crowdCountObj.diffCrowdCount + (1-alpha) * crowdCountObj.EMA

    if(
        Math.abs(crowdCountObj.EMA) > 1
        && (
            timestampObj.timeSinceLectureEvent === undefined ||
            timestampObj.timeSinceLectureEvent > 10*60  
        ) 
        && (
            +minutes <= 7.5 || +minutes >= 52.5 || (+minutes >= 22.5 && +minutes <= 37.5)
        )
    ) {
        const lectureEventLi = document.createElement("li")
        timestampObj.timeSinceLectureEvent = 0
        lectureEventLi.textContent = `Boundary @ ${hours}:${minutes}:${seconds}`;
        lectureEvents?.appendChild(lectureEventLi);
        proxiedDataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"boundary"})
    }

    if(spansObj.differenceSpan && spansObj.diffEMASpan) {
        spansObj.differenceSpan.textContent = String(crowdCountObj.diffCrowdCount)
        spansObj.diffEMASpan.textContent = String(crowdCountObj.EMA.toFixed(2))
    }
};

const wsOnclose = (event) => {
    console.log('Closed');
};

export default handleDayDropdown