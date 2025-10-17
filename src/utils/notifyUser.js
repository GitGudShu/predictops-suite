import { Notify } from "quasar"

export function notifyUser(options) {
  Notify.create({
    ...options,
    progress: true,
    actions: [{ label: 'Close', color: 'white' }],
  });
}

