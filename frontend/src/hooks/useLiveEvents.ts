import { useEffect } from 'react';
import { WS_URL } from '../services/api';
import { useAppStore } from '../store/appStore';

export function useLiveEvents() {
  const pushEvent = useAppStore((state) => state.pushEvent);
  const setSettings = useAppStore((state) => state.setSettings);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socket.onmessage = (message) => {
      const payload = JSON.parse(message.data);
      if (payload.type === 'SNAPSHOT') {
        payload.events?.forEach(pushEvent);
        if (payload.settings) setSettings(payload.settings);
        return;
      }
      pushEvent(payload);
    };
    return () => socket.close();
  }, [pushEvent, setSettings]);
}
