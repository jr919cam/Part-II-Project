export interface SpansObj {
    differenceSpan: HTMLElement | null
    diffEMASpan: HTMLElement | null
}

export interface ConfigObj {
    speed: number,
    alpha: number
}

export interface CrowdCountObj {
    prevCrowdCount?: number, 
    diffCrowdCount?: number, 
    EMA: number,
}

export interface TimestampObj {
    prevts?: number, 
    diffts?: number, 
    timeSinceLectureEvent?: number
}

export interface WsObj {
    ws?: WebSocket
}