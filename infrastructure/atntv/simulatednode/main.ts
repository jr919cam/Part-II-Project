import { ConfigObj, SpansObj, CrowdCountObj, TimestampObj, WsObj} from './mainTypes.ts'

export const handleDayDropdown = (event, spansObj: SpansObj, configObj:ConfigObj, timestampObj:TimestampObj, crowdCountObj: CrowdCountObj, wsObj:WsObj, ): void => {
    if(wsObj.ws) {
        wsObj.ws.close()
        console.log("closed")
    }
    const day = event.target.value
    console.log(day)
    wsObj.ws = new WebSocket(`ws://localhost:8002/ws?speed=${configObj.speed}&day=${day}`);
    wsObj.ws.onclose = wsOnclose;
    wsObj.ws.onmessage = (event) => wsOnmessage(event, spansObj, timestampObj, crowdCountObj, configObj.alpha);
    wsObj.ws.onopen = wsOnopen;
}

const wsOnopen = (event: Event): void => {
    const oldData = document.getElementById("data");
    const newData = document.createElement("div");
    newData.id = "data"
    oldData?.replaceWith(newData);
}

const wsOnmessage = (event: MessageEvent, spansObj: SpansObj, timestampObj: TimestampObj, crowdCountObj: CrowdCountObj, alpha:number) => {
    const dataList = document.getElementById("data");
    const dataLi = document.createElement("li")

    const lectureEvents = document.getElementById("lectureEvents");

    const dataObject = JSON.parse(event.data);

    const date = new Date(dataObject.acp_ts * 1000)
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    dataLi.textContent = `Crowdcount: ${dataObject.payload_cooked.crowdcount} @ ${hours}:${minutes}:${seconds}`;
    dataList?.appendChild(dataLi);

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
        lectureEventLi.textContent = `Lecture boundary event @ ${hours}:${minutes}:${seconds}`;
        lectureEvents?.appendChild(lectureEventLi);
    }

    if(spansObj.differenceSpan && spansObj.diffEMASpan) {
        spansObj.differenceSpan.textContent = String(crowdCountObj.diffCrowdCount)
        spansObj.diffEMASpan.textContent = String(crowdCountObj.EMA.toFixed(2))
    }
};

const wsOnclose = (event: CloseEvent) => {
    console.log('Closed');
};