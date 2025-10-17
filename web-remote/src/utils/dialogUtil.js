import { Dialog } from 'quasar';

export function showDialog(options, onOk = () => 1, onDismiss = () => 1, onCancel = () => 1) {
  Dialog.create({
    ...options,
    component: options.component,
  }).onOk(onOk).onDismiss(onDismiss).onCancel(onCancel)
}
