import { writable } from "svelte/store";
import { useAccessToken } from "./accessToken";
import { env } from '$env/dynamic/public';
import { dateObjectFromUTC } from '$lib/utils';


export function useSessions() {
    let sessions = writable([]);
    let accessToken = useAccessToken();
    let token = '';

    async function refreshSessions() {
        try {
            const response = await fetch(`${env.PUBLIC_API_URL}/sessions?token=${token}`, {
            method: 'GET'
            });
            if (response.ok) {
            const data = await response.json();
            const list = data.sessions;
            list.forEach((session) => {
                session.created_at = dateObjectFromUTC(session.created_at);
                session.last_activity_at = dateObjectFromUTC(session.last_activity_at);

                console.log(session.created_at)
            });
            list.sort((a, b) => b.last_activity_at - a.last_activity_at);
            sessions.set(data.sessions);
            } else {
            sessions.set([]);
            }
        } catch (error) {
            console.error('Error fetching sessions:', error);
            sessions.set([]);
        }
    }

    accessToken.subscribe((value) => {
        if (!value) return;
        token = value;
        refreshSessions();
    });

    return { sessions, refreshSessions };
}

export function usePayloads(sessionId, onSessionCreated, onPayloadReceived) {
    let accessToken = useAccessToken();
    let state = writable('closed');
    let sendPayload = writable((_) => {});
    let ws = writable(null);
    let finished = false;

    function connect(url) {
        ws.update((value) => {
            if (value) {
                console.log('Closing previous connection');
                value.socket.close();
                state.set('closed');
            }
            return {
                socket: new WebSocket(url),
                url: url
            }
        });
    }

    function disconnect() {
        ws.update((value) => {
            if (value) {
                value.socket.close();
                state.set('closed');
            }
            return null;
        });
    }
    
    accessToken.subscribe((value) => {
        if (!value) return;
        connect(`${env.PUBLIC_WS_URL}/chat/${`${sessionId}`.startsWith('new') ? '-1' : sessionId}?token=${value}`);
    });

    ws.subscribe((value) => {
        if (!value) return;

        console.log('Subscribing to events');

        value.socket.onopen = () => {
            console.log('Connected to YOUR APP');
        };
        value.socket.onclose = () => {
            state.set('closed');
            if (!finished) {
                console.log('Connection closed forcibly');
                ws.set(null);
                close();
            }
        };
        value.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received message', data);
            if (data.payload.type === 'state' && data.payload.state === 'closed') {
                close();
            }
            if (data.payload.type === 'state' && data.payload.state === 'opened') {
                open(value.socket);
            }
            if (data.payload.type === 'session_created') {
                console.log(data)
                sessionId = data.payload.id;
                onSessionCreated(data.payload.id);
            }
            if (data.payload.type === 'end') {
                finished = true
                value.socket.close();
                close();
            }

            onPayloadReceived(data.payload);
        };
    });

    function open(socket) {
        state.set('opened');
        console.log('Opened');
        sendPayload.set((payload) => {
            console.log('Sending payload', payload);
            socket.send(JSON.stringify(payload));
            state.set('closed');
        });
    }

    function close() {
        state.set('closed');
        sendPayload.set((_) => {});
    }

    return {
        state,
        sendPayload,
        disconnect
    };
}