import plotSeatDiagram from "/infrastructure/facentrate/plotters/plotSeatDiagram.js";
import plotMainGraph from "/infrastructure/facentrate/plotters/plotMainGraph.js";
import plotSeatMetricsDiagram from "/infrastructure/facentrate/plotters/plotSeatMetricsDiagram.js";
import plotStabilityGraph from "/infrastructure/facentrate/plotters/plotStabilityGraph.js";
import plotConcentrationGraph from "/infrastructure/facentrate/plotters/plotConcentrationGraph.js";

export const graphWidth = 1800;
export const graphHeight = 600;

const plotGraphs = (endTime, startTime, day, dataArrObj) => {
    // console.log(dataArrObj.leccentrationArr)

    const oldChart = document.getElementById("chart")
    // const oldStabilityChart = document.getElementById("stabilityChart")
    const oldConcetrationChart = document.getElementById("concentrationChart")
    const oldSeatMetricsDiagram = document.getElementById("seatMetricsDiagram")
    
    oldChart.replaceWith(
        plotMainGraph(
            dataArrObj.dataArr, 
            dataArrObj.eventArr, 
            dataArrObj.barcodeArr, 
            dataArrObj.varianceArr, 
            dataArrObj.sensorArr,
            graphHeight, 
            graphWidth,
            startTime,
            endTime,
            day,
        )
    );
    oldConcetrationChart.replaceWith(
        plotConcentrationGraph(
            dataArrObj.leccentrationArr,
            graphHeight/2,
            graphWidth,
            startTime,
            endTime,
            day,
        )
    )
    // oldStabilityChart.replaceWith(
    //     plotStabilityGraph(
    //         dataArrObj.wholeRoomStability,
    //         graphHeight/2,
    //         graphWidth,
    //         startTime,
    //         endTime,
    //         day,
    //     )
    // );
    oldSeatMetricsDiagram.replaceWith(
        plotSeatMetricsDiagram(
            dataArrObj.percentageConcentration,
            dataArrObj.concentrationEdges,
            dataArrObj.leccentration,
            dataArrObj.timeElapsed
        )
    );
}

const configObj = {alpha: 1/20};

const wsObj = {};

const dataArrObj = {
    dataArr: [], 
    eventArr: [], 
    barcodeArr:[], 
    varianceArr:[],
    seatHistoryArr:[],
    sensorArr:[],
    leccentrationArr:[],
    percentageConcentration: null,
    concentrationEdges: null,
    wholeRoomStability:{seatsOccupiedDiffCountTotal: 0, seatsOccupiedDiffCount: []},
    diffCountEMA: 0,
    leccentration: 0,
    isVisible:false, 
    wasVisible:false,
    timeElapsed: 0
}

const emulateDay = (event) => {
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
    const sensor = form.sensor.value;

    const startTimeTS = new Date(`${day}T${startTime}:00Z`)
    wsObj.ws = new WebSocket(
        `ws://localhost:8002/ws?speed=${speed}&day=${day}&startTime=${startTime}&endTime=${endTime}&seat=${seat}&sensor=${sensor}&alpha=${configObj.alpha}`);
    wsObj.ws.onclose = wsOnclose;
    wsObj.ws.onmessage = (event) => wsOnmessage(event, dataArrObj, seat, startTimeTS.valueOf(), form);
    wsObj.ws.onopen = (event) => wsOnopen(dataArrObj, seat);
}

const wsOnopen = (dataArrObj, seat) => {
    const oldData = document.getElementById("data");
    const newData = document.createElement("div");
    newData.id = "data"
    oldData?.replaceWith(newData);

    const oldLectureEvents = document.getElementById("lectureEvents");
    const newLectureEvents = document.createElement("div");
    newLectureEvents.id = "lectureEvents"
    oldLectureEvents?.replaceWith(newLectureEvents);

    const oldcrowdcountPeriodTableBody = document.getElementById("crowdcountPeriodTableBody");
    const newcrowdcountPeriodTableBody = document.createElement("tbody");
    newcrowdcountPeriodTableBody.id = "crowdcountPeriodTableBody"
    oldcrowdcountPeriodTableBody?.replaceWith(newcrowdcountPeriodTableBody);

    const oldco2PeriodTableBody = document.getElementById("co2PeriodTableBody");
    const newco2PeriodTableBody = document.createElement("tbody");
    newco2PeriodTableBody.id = "co2PeriodTableBody"
    oldco2PeriodTableBody?.replaceWith(newco2PeriodTableBody);

    dataArrObj.dataArr = []
    dataArrObj.eventArr = []
    dataArrObj.barcodeArr = []
    dataArrObj.varianceArr = []
    dataArrObj.seatHistoryArr = [],
    dataArrObj.sensorArr = [],
    dataArrObj.leccentrationArr = [],
    dataArrObj.percentageConcentration = null,
    dataArrObj.concentrationEdges = seat ? 0 : null,
    dataArrObj.wholeRoomStability = {seatsOccupiedDiffCountTotal: 0, seatsOccupiedDiffCount: []},
    dataArrObj.diffCountEMA = 0,
    dataArrObj.isVisible = false,
    dataArrObj.wasVisible = false,
    dataArrObj.timeElapsed = 0
}

const wsOnmessage = (event, dataArrObj, seat, startTimeTS, form) => {
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
                if (!dataArrObj.seatHistoryArr.includes(seat)) {
                    dataArrObj.seatHistoryArr.push(seat);
                }
            });

            seatDiagramContainer.replaceChild(plotSeatDiagram(dataObject.payload_cooked.seats_occupied, dataArrObj.seatHistoryArr), seatDiagramContainer.firstChild)
            
            const prevDiffCount = dataArrObj.wholeRoomStability.seatsOccupiedDiffCount[dataArrObj.wholeRoomStability.seatsOccupiedDiffCount.length-1] ?? {value: 0}
            const diffCountValue = prevDiffCount.value > 0 ? prevDiffCount.value/2 + dataObject.payload_cooked.seatsOccupiedDiffCount : dataObject.payload_cooked.seatsOccupiedDiffCount
            dataArrObj.diffCountEMA = (1/12) * Math.pow(diffCountValue, 2) + (11/12) * dataArrObj.diffCountEMA
            dataArrObj.wholeRoomStability.seatsOccupiedDiffCount.push({value: diffCountValue, acp_ts: +dataObject.acp_ts, ema: dataArrObj.diffCountEMA})
            dataArrObj.wholeRoomStability.seatsOccupiedDiffCountTotal = dataObject.payload_cooked.seatsOccupiedDiffCountTotal
            dataArrObj.leccentrationArr.push({value: dataObject.payload_cooked.leccentration, sd: dataObject.payload_cooked.leccentrationSD, acp_ts: +dataObject.acp_ts})

            dataArrObj.timeElapsed = +dataObject.acp_ts - startTimeTS/1000

            dataLi.textContent = `${dataObject.payload_cooked.crowdcount} @ ${hours}:${minutes}:${seconds}`;
            dataList?.appendChild(dataLi);
            dataArrObj.dataArr.push({acp_ts: dataObject.acp_ts, crowdcount: dataObject.payload_cooked.crowdcount})

            if(dataObject.payload_cooked.percent_concentration !== undefined) {  
                dataArrObj.percentageConcentration = dataObject.payload_cooked.percent_concentration
            }

            if(dataArrObj.isVisible) {
                dataArrObj.barcodeArr[dataArrObj.barcodeArr.length-1].end_acp_ts = dataObject.acp_ts
                dataArrObj.isVisible = false
                dataArrObj.wasVisible = true
            }
            if(dataObject.payload_cooked.seats_occupied.includes(seat)) {
                if(!dataArrObj.wasVisible) {
                    // init a bar
                    dataArrObj.barcodeArr.push({start_acp_ts: dataObject.acp_ts, end_acp_ts: dataObject.acp_ts})
                    dataArrObj.concentrationEdges += 1
                }
                dataArrObj.isVisible = true
            } else {
                if(dataArrObj.wasVisible) {
                    dataArrObj.concentrationEdges += 1
                    dataArrObj.wasVisible = false
                }
            }
        } 
        if (dataObject.readingType === "variance") {
            dataArrObj.varianceArr.push({...dataObject})
        }
        if (dataObject.readingType === "sensor") {
            dataArrObj.sensorArr.push({acp_ts:dataObject.acp_ts, calibrated_co2: Number(dataObject.payload_cooked.calibrated_co2)})
        }
    }
    
    if(dataObject.type === "event"){
        if(dataObject.eventType === "lectureUp") {
            dataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"lectureUp"})
            const lectureEventLi = document.createElement("li")
            lectureEventLi.textContent = `Lecture up @ ${hours}:${minutes}:${seconds}`;
            lectureEvents?.appendChild(lectureEventLi);
            dataArrObj.seatHistoryArr = []
        }
        if(dataObject.eventType === "lectureSettled") {
            dataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"lectureSettled", course: dataObject.course})
            const lectureEventLi = document.createElement("li")
            lectureEventLi.textContent = `Lecture settled @ ${hours}:${minutes}:${seconds}`;
            lectureEvents?.appendChild(lectureEventLi);
            dataArrObj.seatHistoryArr = []
        }
        if(dataObject.eventType === "lectureDown") {
            dataArrObj.eventArr.push({acp_ts: dataObject.acp_ts, event_type:"lectureDown"})
            const lectureEventLi = document.createElement("li")
            lectureEventLi.textContent = `Lecture down @ ${hours}:${minutes}:${seconds}`;
            lectureEvents?.appendChild(lectureEventLi);
            dataArrObj.seatHistoryArr = []
        }
        if(dataObject.eventType === "leccentration") {
            const crowdcountPeriodTable = document.getElementById("crowdcountPeriodTableBody")
            const crowdcountPeriodTableRow = document.createElement("tr")
            const tableValues = [`${(dataObject.lecture)}`, `${dataObject.ccPeriodMean.toFixed(1)}`, `${dataObject.ccPeriodSD.toFixed(1)}`,`${(dataObject.leccentration * 100).toFixed(1)}%`, ` ${(dataObject.leccentrationSD * 100).toFixed(1)}%`]
            tableValues.map((tableValue) => {
                const crowdcountPeriodTableRowDatum = document.createElement("td")
                crowdcountPeriodTableRowDatum.textContent = tableValue
                crowdcountPeriodTableRow.appendChild(crowdcountPeriodTableRowDatum);
            })
            crowdcountPeriodTable.appendChild(crowdcountPeriodTableRow)
        }
        if(dataObject.eventType === "lectureCo2") {
            const co2PeriodTable = document.getElementById("co2PeriodTableBody")
            const co2PeriodTableRow = document.createElement("tr")
            const tableValues = [`${dataObject.co2Avg}`, `${dataObject.co2SD}`]
            tableValues.map((tableValue) => {
                const co2PeriodTableRowDatum = document.createElement("td")
                co2PeriodTableRowDatum.textContent = tableValue
                co2PeriodTableRow.appendChild(co2PeriodTableRowDatum);
            })
            co2PeriodTable.appendChild(co2PeriodTableRow)
        }
    }
    const endTime = form.endTime.value
    const startTime = form.startTime.value
    const day = form.day.value
    plotGraphs(endTime, startTime, day, dataArrObj)
};

const wsOnclose = (event) => {
    console.log('Closed');
};

export default emulateDay