import { Notyf } from 'notyf';
import 'notyf/notyf.min.css';

const notyf = new Notyf({
  duration: 4000,
  position: { x: 'right', y: 'top' },
});

export function showError(msg: string): void {
  notyf.error(msg);
}

export function showSuccess(msg: string): void {
  notyf.success(msg);
}
