import { describe, expect, it } from 'vitest';
import { useAppStore } from '../appStore';

describe('app store', () => {
  it('pushes live events newest first', () => {
    useAppStore.getState().pushEvent({ type: 'FILE_CREATED', timestamp: '2026-05-29T10:00:00Z', filename: 'a.pdf' });
    expect(useAppStore.getState().events[0].filename).toBe('a.pdf');
  });
});
