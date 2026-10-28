import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// jsdom does not implement scrollIntoView, which ChatPanel uses
window.HTMLElement.prototype.scrollIntoView = function () {};

afterEach(() => {
  cleanup();
  localStorage.clear();
});