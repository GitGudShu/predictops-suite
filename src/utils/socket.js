import { io } from "socket.io-client";
import { api } from "boot/axios";

export const socket = io(api.defaults.baseURL.replace('api', ''), {
  autoConnect: false
})

export function connectSocket() {
  if (!socket.connected) {
    socket.connect();
  }
}

export function disconnectSocket() {
  if (socket.connected) {
    socket.disconnect();
  }
}
